# -*- coding: utf-8 -*-
"""解析 Word(.docx)、PDF 文件，按段返回文本列表。"""
import os
from typing import List, Optional, Tuple


def _normalize_paragraphs(lines: List[str]) -> List[str]:
    """合并空行、去掉首尾空白，按段拆分（连续非空行为一段）。"""
    paragraphs: List[str] = []
    current: List[str] = []
    for line in lines:
        line = line.rstrip("\n\r")
        if line.strip():
            current.append(line)
        else:
            if current:
                paragraphs.append("\n".join(current))
                current = []
    if current:
        paragraphs.append("\n".join(current))
    return [p.strip() for p in paragraphs if p.strip()]


def parse_txt(path: str) -> Tuple[List[str], Optional[str]]:
    """解析 TXT：按空行分段落。返回 (段落列表, 错误信息)。"""
    try:
        with open(path, "r", encoding="utf-8", errors="replace") as f:
            text = f.read()
    except Exception as e:
        return [], str(e)
    lines = text.replace("\r\n", "\n").replace("\r", "\n").split("\n")
    return _normalize_paragraphs(lines), None


def parse_docx(path: str) -> Tuple[List[str], Optional[str]]:
    """解析 Word：按文档段落。返回 (段落列表, 错误信息)。"""
    try:
        from docx import Document
    except ImportError:
        return [], "请安装 python-docx: pip install python-docx"
    try:
        doc = Document(path)
        paragraphs = []
        for p in doc.paragraphs:
            text = p.text.strip()
            if text:
                paragraphs.append(text)
        if not paragraphs:
            return [], "文档中未识别到有效段落"
        return paragraphs, None
    except Exception as e:
        return [], str(e)


def parse_pdf(path: str) -> Tuple[List[str], Optional[str]]:
    """解析 PDF：按页提取文本后按空行分段落。返回 (段落列表, 错误信息)。"""
    try:
        from pypdf import PdfReader
    except ImportError:
        return [], "请安装 pypdf: pip install pypdf"
    try:
        reader = PdfReader(path)
        lines = []
        for page in reader.pages:
            text = page.extract_text()
            if text:
                lines.extend(text.replace("\r\n", "\n").replace("\r", "\n").split("\n"))
        return _normalize_paragraphs(lines), None
    except Exception as e:
        return [], str(e)


def parse_file(path: str) -> Tuple[List[str], Optional[str]]:
    """
    根据扩展名选择解析器，返回 (段落列表, 错误信息)。
    支持 .docx, .pdf（小写）。
    """
    if not path or not os.path.isfile(path):
        return [], "请选择有效文件"
    ext = os.path.splitext(path)[1].lower()
    if ext == ".docx":
        return parse_docx(path)
    if ext == ".pdf":
        return parse_pdf(path)
    return [], f"不支持的文件类型: {ext}，仅支持 .docx / .pdf"
