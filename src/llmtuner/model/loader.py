import os
from typing import TYPE_CHECKING
from transformers import AutoConfig, AutoModelForCausalLM, AutoTokenizer
from transformers.integrations import is_deepspeed_zero3_enabled

from ..extras.logging import get_logger


if TYPE_CHECKING:
    from ..hparams import ModelArguments

logger = get_logger(__name__)


def load_model_and_tokenizer(model_args: "ModelArguments"):
    r"""
    加载模型和分词器。
    """

    config_kwargs = {
        "trust_remote_code": True,
    }

    tokenizer = AutoTokenizer.from_pretrained(
        model_args.model_name_or_path,
        use_fast=model_args.use_fast_tokenizer,
        split_special_tokens=model_args.split_special_tokens,
        padding_side="right",
        **config_kwargs,
    )

    # config = AutoConfig.from_pretrained(model_args.model_name_or_path, **config_kwargs)

    # model = AutoModelForCausalLM.from_pretrained(
    #     model_args.model_name_or_path,
    #     config=config,
    #     torch_dtype=model_args.compute_dtype,
    #     low_cpu_mem_usage=(not is_deepspeed_zero3_enabled()),
    #     **config_kwargs,
    # )

    # model.requires_grad_(False)
    # model = model.to(model_args.compute_dtype) if not getattr(model, "quantization_method", None) else model
    # model.eval()

    # for param in model.parameters():
    #     logger.info(param.dtype)  # 打印每个参数的精度
    #     break  # 只需要检查一个参数，因为所有参数通常具有相同的精度

    # return model, tokenizer
    return tokenizer
