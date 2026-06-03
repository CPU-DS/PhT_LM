from dataclasses import dataclass
from threading import Thread
from typing import Any, Dict, AsyncGenerator, Generator, List, Literal, Optional, Sequence, Tuple
from vllm import AsyncEngineArgs, AsyncLLMEngine, RequestOutput, SamplingParams, LLM
from vllm.lora.request import LoRARequest
from vllm.sequence import MultiModalData

import uuid
import torch
from transformers import GenerationConfig, TextIteratorStreamer

from ..data import get_template_and_fix_tokenizer
from ..extras.misc import get_logits_processor, get_device_count
from ..hparams import get_infer_args
from ..model import dispatch_model, load_model_and_tokenizer
from ..extras.logging import get_logger

logger = get_logger(__name__)


@dataclass
class Response:
    response_text: str
    response_length: int
    prompt_length: int


class ChatModel:
    def __init__(self, args: Optional[Dict[str, Any]] = None) -> None:
        model_args, data_args, self.generating_args = get_infer_args(args)
        self.tokenizer = load_model_and_tokenizer(model_args)
        self.tokenizer.padding_side = "left"
        self.template = get_template_and_fix_tokenizer(data_args.template, self.tokenizer)
        
        engine_args = {
            "model": model_args.model_name_or_path,
            "trust_remote_code": True,
            "dtype": model_args.vllm_dtype,
            "enforce_eager": model_args.vllm_enforce_eager,
            "tensor_parallel_size": get_device_count() or 1,
            "gpu_memory_utilization": model_args.vllm_gpu_util
        }
        self.model = AsyncLLMEngine.from_engine_args(AsyncEngineArgs(**engine_args))
        if model_args.adapter_name_or_path is not None:
            self.lora_request = LoRARequest("default", 1, model_args.adapter_name_or_path[0])
        else:
            self.lora_request = None

    async def _process_args(
        self,
        messages: Sequence[Dict[str, str]],
        **input_kwargs,
    ) -> Tuple[Dict[str, Any], int]:
        request_id = "chatcmpl-{}".format(uuid.uuid4().hex)
        paired_messages = messages + [{"role": "assistant", "content": ""}]
        prompt, _ = self.template.encode_oneturn(
            tokenizer=self.tokenizer, messages=paired_messages
        )

        temperature = input_kwargs.pop("temperature", None)
        top_p = input_kwargs.pop("top_p", None)
        max_length = input_kwargs.pop("max_length", None)
        max_new_tokens = input_kwargs.pop("max_new_tokens", None)
        repetition_penalty = input_kwargs.pop("repetition_penalty", None)

        generating_args = self.generating_args.to_dict()
        generating_args.update(
            dict(
                do_sample=generating_args["do_sample"],
                temperature=temperature or generating_args["temperature"],
                top_p=top_p or generating_args["top_p"],
                num_return_sequences=1,
                repetition_penalty=generating_args["repetition_penalty"],
                eos_token_id=[self.tokenizer.eos_token_id] + self.tokenizer.additional_special_tokens_ids,
                pad_token_id=self.tokenizer.pad_token_id,
            )
        )
        if max_length:
            generating_args.pop("max_new_tokens", None)
            generating_args["max_length"] = max_length

        if max_new_tokens:
            generating_args.pop("max_length", None)
            generating_args["max_new_tokens"] = max_new_tokens


        sampling_params = SamplingParams(
            repetition_penalty=(
                repetition_penalty if repetition_penalty is not None else generating_args["repetition_penalty"]
            )
            or 1.0,  # repetition_penalty must > 0
            temperature=temperature if temperature is not None else generating_args["temperature"],
            top_p=(top_p if top_p is not None else generating_args["top_p"]) or 1.0,  # top_p must > 0
            stop_token_ids=[self.tokenizer.eos_token_id] + self.tokenizer.additional_special_tokens_ids,
            max_tokens=max_new_tokens,
            skip_special_tokens=True
        )
        
        result_generator = self.model.generate(
            inputs={"prompt_token_ids": prompt, "multi_modal_data": None},
            sampling_params=sampling_params,
            request_id=request_id,
            lora_request=self.lora_request,
        )

        return result_generator
    
    # 在模型推理时关闭梯度计算与自动求导，提升执行速度并降低内存占用
    @torch.inference_mode()
    async def chat(
        self,
        messages: Sequence[Dict[str, str]],
        system: Optional[str] = None,
        tools: Optional[str] = None,
        **input_kwargs,
    ) -> List[Response]:
        final_output = None
        generator = await self._process_args(messages, **input_kwargs)
        async for request_output in generator:
            final_output = request_output
        
        results = []
        for output in final_output.outputs:
            results.append(
                Response(
                    response_text=output.text,
                    response_length=len(output.token_ids),
                    prompt_length=len(final_output.prompt_token_ids)
                )
            )

        return results
    

    @torch.inference_mode()
    async def stream_chat(
        self,
        messages: Sequence[Dict[str, str]],
        system: Optional[str] = None,
        tools: Optional[str] = None,
        **input_kwargs,
    ) -> AsyncGenerator[str, None]:
        generated_text = ""
        generator = await self._process_args(messages, **input_kwargs)
        async for result in generator:
            delta_text = result.outputs[0].text[len(generated_text) :]
            generated_text = result.outputs[0].text
            yield delta_text
    
    
    # @torch.inference_mode()
    # def chat(
    #     self,
    #     messages: Sequence[Dict[str, str]],
    #     **input_kwargs,
    # ):
    #     gen_kwargs, prompt_length = self._process_args(messages, **input_kwargs)
    #     generate_output = self.model.generate(**gen_kwargs)
    #     response_ids = generate_output[:, prompt_length:]
    #     response = self.tokenizer.batch_decode(
    #         response_ids, skip_special_tokens=True, clean_up_tokenization_spaces=True
    #     )
    #     results = []
    #     for i in range(len(response)):
    #         eos_index = (response_ids[i] == self.tokenizer.eos_token_id).nonzero()
    #         response_length = (eos_index[0].item() + 1) if len(eos_index) else len(response_ids[i])
    #         results.append(
    #             Response(
    #                 response_text=response[i],
    #                 response_length=response_length,
    #                 prompt_length=prompt_length
    #             )
    #         )

    #     return results

    # @torch.inference_mode()
    # def stream_chat(
    #     self,
    #     messages: Sequence[Dict[str, str]],
    #     **input_kwargs,
    # ):
    #     gen_kwargs, _ = self._process_args(messages, **input_kwargs)
    #     streamer = TextIteratorStreamer(self.tokenizer, timeout=60.0, skip_prompt=True, skip_special_tokens=True)
    #     gen_kwargs["streamer"] = streamer

    #     thread = Thread(target=self.model.generate, kwargs=gen_kwargs)
    #     thread.start()

    #     yield from streamer
