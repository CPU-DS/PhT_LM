import os
import sys
from typing import Any, Dict, Optional

from transformers import HfArgumentParser

from .data_args import DataArguments
from .generating_args import GeneratingArguments
from .model_args import ModelArguments


def _parse_args(parser: "HfArgumentParser", args: Optional[Dict[str, Any]] = None):
    if args is not None:
        return parser.parse_dict(args)

    if len(sys.argv) == 2 and sys.argv[1].endswith(".yaml"):
        return parser.parse_yaml_file(os.path.abspath(sys.argv[1]))

    if len(sys.argv) == 2 and sys.argv[1].endswith(".json"):
        return parser.parse_json_file(os.path.abspath(sys.argv[1]))

    (*parsed_args, unknown_args) = parser.parse_args_into_dataclasses(return_remaining_strings=True)

    if unknown_args:
        print(parser.format_help())
        print("获得未知参数，可能被弃用：{}".format(unknown_args))
        raise ValueError("一些指定的参数不被HfArgumentParser使用: {}".format(unknown_args))

    return (*parsed_args,)

def get_infer_args(args: Optional[Dict[str, Any]] = None):
    parser = HfArgumentParser([ModelArguments, DataArguments, GeneratingArguments])
    model_args, data_args, generating_args = _parse_args(parser, args)

    return model_args, data_args, generating_args
