import os
import gradio as gr
from datetime import datetime
from ..extras.constants import EN_2_ZH, ZH_2_EN, DIRECTION, ES_AND_VEC, ES, RETRIEVAL_MODE
from .css import CSS
from .chatter import WebChatModel
from .file_parser import parse_file


# 文件翻译结果保存目录（项目根下的 translation_output）
TRANSLATION_OUTPUT_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))),
    "translation_output",
)


def _ensure_output_dir():
    os.makedirs(TRANSLATION_OUTPUT_DIR, exist_ok=True)


def _progress_html(msg: str, is_error: bool = False) -> str:
    color = "#dc2626" if is_error else "#0d9488"
    bg = "#fef2f2" if is_error else "#f0fdf9"
    border = "#fca5a5" if is_error else "#99f6e4"
    return (
        f'<div style="padding:12px 16px;background:{bg};border:1px solid {border};'
        f'border-radius:8px;color:{color};font-size:0.95rem;font-weight:500;">{msg}</div>'
    )


def _save_docx(results, out_path: str) -> None:
    from docx import Document
    doc = Document()
    for _, trans in results:
        if trans.strip():
            doc.add_paragraph(trans)
    doc.save(out_path)


def _save_pdf(results, out_path: str) -> None:
    try:
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
        from reportlab.lib.styles import ParagraphStyle
        from reportlab.lib.pagesizes import A4
        from reportlab.lib.units import cm
        from reportlab.pdfbase import pdfmetrics
        from reportlab.pdfbase.cidfonts import UnicodeCIDFont
    except ImportError:
        raise RuntimeError("请先安装 reportlab: pip install reportlab")

    pdfmetrics.registerFont(UnicodeCIDFont("STSong-Light"))
    style = ParagraphStyle(
        "Body", fontName="STSong-Light", fontSize=11, leading=22, spaceAfter=8,
    )
    story = []
    for _, trans in results:
        if trans.strip():
            safe = trans.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
            story.append(Paragraph(safe, style))
            story.append(Spacer(1, 6))
    if not story:
        story.append(Paragraph("（无翻译内容）", style))
    doc = SimpleDocTemplate(
        out_path, pagesize=A4,
        leftMargin=2 * cm, rightMargin=2 * cm,
        topMargin=2 * cm, bottomMargin=2 * cm,
    )
    doc.build(story)


def _make_translate_file_fn(chatter: "WebChatModel"):
    """闭包：使用已加载的 chatter 实例进行文件翻译，避免重复加载模型。"""

    async def translate_file(file_path, direction: str, retrieval_mode: str):
        # 参数校验
        if not file_path:
            yield _progress_html("请先上传 .docx 或 .pdf 文件", is_error=True), None
            return
        if isinstance(file_path, list):
            file_path = file_path[0] if file_path else None
        path = file_path if isinstance(file_path, str) else getattr(file_path, "name", None)
        if not path or not os.path.isfile(path):
            yield _progress_html("无效文件，请重新上传", is_error=True), None
            return

        ext = os.path.splitext(path)[1].lower()
        if ext not in (".docx", ".pdf"):
            yield _progress_html(f"不支持的格式 {ext}，请上传 .docx 或 .pdf 文件", is_error=True), None
            return

        yield _progress_html("正在解析文件…"), None

        paragraphs, err = parse_file(path)
        if err:
            yield _progress_html(f"解析失败：{err}", is_error=True), None
            return
        if not paragraphs:
            yield _progress_html("未识别到可翻译的段落", is_error=True), None
            return

        _ensure_output_dir()
        total = len(paragraphs)
        results = []

        for i, para in enumerate(paragraphs):
            try:
                translated = await chatter.translate_segment(para, direction, retrieval_mode)
                results.append((para, translated))
            except Exception as e:
                results.append((para, f"[翻译异常: {e}]"))
            yield _progress_html(f"当前已翻译 {i + 1}/{total} 段"), None

        # 保存为原始格式
        base_name = os.path.splitext(os.path.basename(path))[0]
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        out_name = f"{base_name}_translated_{timestamp}{ext}"
        out_path = os.path.join(TRANSLATION_OUTPUT_DIR, out_name)
        try:
            if ext == ".docx":
                _save_docx(results, out_path)
            else:
                _save_pdf(results, out_path)
        except Exception as e:
            yield _progress_html(f"保存失败：{e}", is_error=True), None
            return

        yield _progress_html(f"翻译完成，共 {total} 段，文件已保存 ✓"), out_path

    return translate_file


def create_web_demo() -> gr.Blocks:
    chatter = WebChatModel()

    with gr.Blocks(title="药品国际注册文件翻译平台", css=CSS) as demo:
        gr.HTML(
            '<div class="app-header">'
            '<h1 class="app-title">药品国际注册文件翻译平台</h1>'
            '<p class="app-subtitle">支持英译中 / 中译英，基于检索增强的精准翻译 · 支持文本与文件翻译</p>'
            '</div>'
        )
        with gr.Tabs():
            with gr.Tab("文本翻译"):
                create_chat_box(chatter, visible=True)
            with gr.Tab("文件翻译"):
                create_file_translate_tab(chatter)
        demo.load()

    return demo



def create_file_translate_tab(chatter: "WebChatModel"):
    """文件翻译：上传 Word/PDF，按段翻译并保存到本地、提供下载。"""
    translate_file_fn = _make_translate_file_fn(chatter)
    with gr.Box(elem_classes=["main-container", "file-translate-box"]):
        gr.Markdown("上传 **Word(.docx)** 或 **PDF** 文件，将按段落依次翻译，译文保存为对应格式并可供下载。")
        file_input = gr.File(
            label="选择文件",
            file_count="single",
        )
        with gr.Row(elem_classes=["options-row"]):
            with gr.Column(scale=1, min_width=180):
                direction = gr.Dropdown(
                    label=DIRECTION,
                    choices=[EN_2_ZH, ZH_2_EN],
                    value=EN_2_ZH,
                    elem_classes=["option-dropdown"],
                )
            with gr.Column(scale=1, min_width=180):
                only_es = gr.Dropdown(
                    label=RETRIEVAL_MODE,
                    choices=[ES_AND_VEC, ES],
                    value=ES_AND_VEC,
                    elem_classes=["option-dropdown"],
                )
        translate_file_btn = gr.Button(
            value="开始翻译",
            variant="primary",
            elem_id="file-translate-btn",
            elem_classes=["btn-primary"],
        )
        progress_html = gr.HTML(value="")
        download_out = gr.File(label="下载翻译结果", interactive=False)
    translate_file_btn.click(
        translate_file_fn,
        inputs=[file_input, direction, only_es],
        outputs=[progress_html, download_out],
        show_progress=False,
    )


def create_chat_box(
    chatter: "WebChatModel", visible: False
):
    with gr.Box(visible=visible, elem_classes=["main-container"]) as chat_box:
        chatbot = gr.Chatbot(
            label="",
            elem_id="translation-chatbot",
            height=400,
        )
        messages = gr.State([])
        with gr.Row(elem_classes=["options-row"]):
            with gr.Column(scale=1, min_width=180):
                direction = gr.Dropdown(
                    label=DIRECTION,
                    choices=[EN_2_ZH, ZH_2_EN],
                    value=EN_2_ZH,
                    elem_classes=["option-dropdown"],
                )
            with gr.Column(scale=1, min_width=180):
                only_es = gr.Dropdown(
                    label=RETRIEVAL_MODE,
                    choices=[ES_AND_VEC, ES],
                    value=ES_AND_VEC,
                    elem_classes=["option-dropdown"],
                )
        with gr.Row(elem_classes=["input-row"]):
            with gr.Column(scale=1):
                query = gr.Textbox(
                    show_label=False,
                    placeholder="在此输入待翻译的药品注册相关文本，支持多段内容…",
                    lines=6,
                    max_lines=12,
                    elem_classes=["translation-input"],
                )
        with gr.Row(elem_classes=["actions-row"]):
            submit_btn = gr.Button(
                value="开始翻译",
                variant="primary",
                elem_classes=["btn-primary"],
            )
            clear_btn = gr.Button(
                value="清除历史记录",
                variant="secondary",
                elem_classes=["btn-secondary"],
            )

    submit_btn.click(
        chatter.predict,
        [chatbot, query, messages, direction, only_es],
        [chatbot, messages],
        show_progress=True,
    ).then(lambda: gr.update(value=""), outputs=[query])
    clear_btn.click(lambda: ([], []), outputs=[chatbot, messages], show_progress=True)

if __name__ == "__main__":
    demo = create_web_demo()
    demo.queue()
    demo.launch(server_name="10.4.0.141", share=False, inbrowser=True)
