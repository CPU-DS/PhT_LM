from retrieval.util import format_prompt
from typing import List, Sequence, Tuple
from ..extras.constants import TOP_P, TEMPERATURE, MAX_TOKENS, ZH_2_EN, ES
from ..chat import ChatModel
from ..data import Role
from ..hparams import GeneratingArguments
from ..extras.misc import torch_gc
from ..extras.logging import get_logger


logger = get_logger(__name__)


class WebChatModel(ChatModel):
    def __init__(
        self
    ) -> None:
        self.model = None
        self.tokenizer = None
        self.generating_args = GeneratingArguments()
        super().__init__()

    async def predict(
        self,
        chatbot: List[Tuple[str, str]],
        query: str,
        messages: Sequence[Tuple[str, str]],
        direction: str,
        retrieval_mode: str,
        topk: int=4,
        fusion_weight: float=0.5,
        max_new_tokens: int=MAX_TOKENS,
        top_p: float=TOP_P,
        temperature: float=TEMPERATURE
    ):
        chatbot.append([query, ""])
        prompt = await format_prompt(query, direction == ZH_2_EN, topk, fusion_weight, retrieval_mode == ES)
        query_messages = [{"role": Role.USER, "content": prompt}]
        response = ""       
        async for new_text in self.stream_chat(
            query_messages, max_new_tokens=max_new_tokens, top_p=top_p, temperature=temperature
        ):
            response += new_text
            result = response

            output_messages = query_messages + [{"role": Role.ASSISTANT, "content": result}]
            bot_text = result

            chatbot[-1] = [query, self.postprocess(bot_text)]
            yield chatbot, output_messages
        torch_gc()

    async def translate_segment(
        self,
        segment: str,
        direction: str,
        retrieval_mode: str,
        topk: int = 4,
        fusion_weight: float = 0.5,
        max_new_tokens: int = MAX_TOKENS,
        top_p: float = TOP_P,
        temperature: float = TEMPERATURE,
    ) -> str:
        """翻译单段文本，用于文件按段翻译。返回翻译结果（已 postprocess）。"""
        if not segment or not segment.strip():
            return ""
        prompt = await format_prompt(
            segment.strip(),
            direction == ZH_2_EN,
            topk,
            fusion_weight,
            retrieval_mode == ES,
        )
        query_messages = [{"role": Role.USER, "content": prompt}]
        responses = await self.chat(
            query_messages,
            max_new_tokens=max_new_tokens,
            top_p=top_p,
            temperature=temperature,
        )
        if not responses:
            return ""
        text = responses[0].response_text.strip()
        return self.postprocess(text)

    def postprocess(self, response: str) -> str:
        blocks = response.split("```")
        for i, block in enumerate(blocks):
            if i % 2 == 0:
                blocks[i] = block.replace("<", "&lt;").replace(">", "&gt;")
        return "```".join(blocks)
