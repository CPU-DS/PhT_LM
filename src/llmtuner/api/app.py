import asyncio
import json
import os
from retrieval.util import format_prompt
from contextlib import asynccontextmanager
from typing import Any, Dict, Sequence, List
from fastapi import FastAPI, status
from fastapi.middleware.cors import CORSMiddleware
from starlette.responses import StreamingResponse
import uvicorn
from pydantic import BaseModel
from ..chat import ChatModel
from ..extras.misc import torch_gc
from ..extras.logging import get_logger
from .protocol import (
    ChatCompletionRequest,
    ChatCompletionTestRequest,
    ChatCompletionResponse,
    ChatCompletionResponseChoice,
    ChatCompletionStreamResponse,
    Role
)


logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: "FastAPI"):
    yield
    torch_gc()


def dictify(data: "BaseModel") -> Dict[str, Any]:
    try:  # pydantic v2
        return data.model_dump(exclude_unset=True)
    except AttributeError:  # pydantic v1
        return data.dict(exclude_unset=True)


def jsonify(data: "BaseModel") -> str:
    try:  # pydantic v2
        return json.dumps(data.model_dump(exclude_unset=True), ensure_ascii=False)
    except AttributeError:  # pydantic v1
        return data.json(exclude_unset=True, ensure_ascii=False)


def create_app(chat_model: "ChatModel", documentsEmbedding) -> "FastAPI":
    app = FastAPI(lifespan=lifespan)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    semaphore = asyncio.Semaphore(int(os.environ.get("MAX_CONCURRENT", 10)))

    @app.post("/chat", response_model=ChatCompletionResponse, status_code=status.HTTP_200_OK)
    async def create_chat_completion(request: ChatCompletionRequest):
        logger.info("model api start...")
        messages = []
        prompt = await format_prompt(request.query, request.is_zh, request.topk, request.fusion_weight, request.is_es, documentsEmbedding)
        messages.append({
            "role": Role.USER,
            "content": prompt
        })
        
        return await chat_completion(messages, request)
        
    
    @app.post("/chat/stream", response_model=ChatCompletionResponse, status_code=status.HTTP_200_OK)
    async def create_chat_stream(request: ChatCompletionRequest):
        logger.info("model api start...")
        messages = []
        prompt = await format_prompt(request.query, request.is_zh, request.topk, request.fusion_weight, request.is_es, documentsEmbedding) 
        
        messages.append({
            "role": Role.USER,
            "content": prompt
        })
        async with semaphore:
            return chat_stream(messages, request)
        
    @app.post("/chat/test", response_model=ChatCompletionResponse, status_code=status.HTTP_200_OK)
    async def create_chat_completion_test(request: ChatCompletionTestRequest):
        logger.info("model api start...")
        messages = [dictify(message) for message in request.messages]
        return await chat_completion_test(messages, request)

    async def chat_completion_test(messages: Sequence[Dict[str, str]], request: ChatCompletionTestRequest):
        responses = chat_model.chat(
            messages,
            temperature=request.temperature,
            top_p=request.top_p,
            max_new_tokens=request.max_tokens
        )

        choices = []
        for i, response in enumerate(responses):
            result = response.response_text
            choices.append(
                ChatCompletionResponseChoice(index=0, message=result)
            )
        
        logger.info("model api finish...")
        torch_gc()
        return ChatCompletionResponse(success=True, content=choices[0].message)
    
    async def chat_completion(messages: Sequence[Dict[str, str]], request: ChatCompletionRequest):
        try: 
            responses = await chat_model.chat(
                messages,
                temperature=request.temperature,
                top_p=request.top_p,
                max_new_tokens=request.max_tokens
            )

            choices = []
            for i, response in enumerate(responses):
                result = response.response_text.strip('\n').strip()

                choices.append(
                    ChatCompletionResponseChoice(index=0, message=result)
                )
            logger.info("model api finish...")
            torch_gc()
            return ChatCompletionResponse(success=True, content=choices[0].message)
        except Exception as e:
            logger.error(e)
            return ChatCompletionResponse(success=False, content='大模型API调用异常')
            


    def chat_stream(messages: Sequence[Dict[str, str]], request: ChatCompletionRequest):
        generate = stream_chat_completion(messages, request)
        return StreamingResponse(generate)


    async def stream_chat_completion(
        messages: Sequence[Dict[str, str]], request: ChatCompletionRequest
    ):
        result = ''
        
        async for new_text in chat_model.stream_chat(
            messages,
            temperature=request.temperature,
            top_p=request.top_p,
            max_new_tokens=request.max_tokens
        ):
            result += new_text
            chunk = ChatCompletionStreamResponse(success=True, content=new_text)
            logger.info(result)
            yield jsonify(chunk) + '\n'
        
        logger.info("model api finish...")
        torch_gc()

    return app


if __name__ == "__main__":
    chat_model = ChatModel()
    app = create_app(chat_model)
    uvicorn.run(app, host="IP", port=int(os.environ.get("API_PORT", 8001)), workers=1)
