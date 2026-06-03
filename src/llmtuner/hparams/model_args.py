import torch

from dataclasses import asdict, dataclass, field
from typing import Any, Dict, Optional, Literal


@dataclass
class ModelArguments:
    r"""
    model arguments
    """
    model_name_or_path: str = field(
        metadata={"help": "Path to the model weight or identifier from huggingface.co/models or modelscope.cn/models."}
    )
    vllm_enforce_eager: bool = field(
        default=True,
        metadata={"help": "Whether or not to disable CUDA graph in the vLLM engine."},
    )
    vllm_dtype: Literal["auto", "float16", "bfloat16", "float32"] = field(
        default="bfloat16",
        metadata={"help": "Data type for model weights and activations in the vLLM engine."},
    )
    vllm_gpu_util: float = field(
        default=0.5,
        metadata={"help": "The fraction of GPU memory in (0,1) to be used for the vLLM engine."},
    )
    adapter_name_or_path: Optional[str] = field(
        default=None, metadata={"help": "Path to the adapter weight or identifier from huggingface.co/models."}
    )
    use_fast_tokenizer: Optional[bool] = field(
        default=False,
        metadata={"help": "Whether or not to use one of the fast tokenizer (backed by the tokenizers library)."},
    )
    split_special_tokens: Optional[bool] = field(
        default=False,
        metadata={"help": "Whether or not the special tokens should be split during the tokenization process."},
    )
    
    def __post_init__(self):
        self.compute_dtype = torch.bfloat16
        self.model_max_length = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
