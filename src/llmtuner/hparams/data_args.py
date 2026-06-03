from dataclasses import dataclass, field
from typing import Literal, Optional


@dataclass
class DataArguments:
    template: Optional[str] = field(
        default="qwen", metadata={"help": "Which template to use for constructing prompts in training and inference."}
    )