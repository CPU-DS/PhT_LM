CSS = r"""
/* ========== 主题变量 ========== */
:root {
  --pht-primary: #0d9488;
  --pht-primary-hover: #0f766e;
  --pht-primary-light: #ccfbf1;
  --pht-surface: #f8fafc;
  --pht-border: #e2e8f0;
  --pht-text: #1e293b;
  --pht-text-muted: #64748b;
  --pht-radius: 12px;
  --pht-shadow: 0 1px 3px rgba(0,0,0,0.08);
  --pht-shadow-lg: 0 4px 12px rgba(13, 148, 136, 0.12);
}

.dark {
  --pht-surface: #1e293b;
  --pht-border: #334155;
  --pht-text: #f1f5f9;
  --pht-text-muted: #94a3b8;
}

/* ========== 主容器 ========== */
.main-container {
  max-width: 900px !important;
  margin: 0 auto !important;
  padding: 24px !important;
  background: var(--pht-surface) !important;
  border-radius: 16px !important;
  box-shadow: var(--pht-shadow-lg) !important;
  border: 1px solid var(--pht-border) !important;
}

/* ========== 页头 ========== */
.app-header {
  text-align: center;
  margin-bottom: 28px !important;
  padding-bottom: 24px !important;
  border-bottom: 2px solid var(--pht-border) !important;
}
.app-title {
  font-size: 1.75rem !important;
  font-weight: 700 !important;
  color: var(--pht-primary) !important;
  margin: 0 0 8px 0 !important;
  letter-spacing: -0.02em;
}
.app-subtitle {
  font-size: 0.95rem !important;
  color: var(--pht-text-muted) !important;
  margin: 0 !important;
}

/* ========== 对话区域 ========== */
#translation-chatbot {
  border-radius: var(--pht-radius) !important;
  border: 1px solid var(--pht-border) !important;
  box-shadow: var(--pht-shadow) !important;
  margin-bottom: 20px !important;
  overflow: hidden !important;
  /* 确保聊天内容可选中、可复制 */
  user-select: text !important;
  -webkit-user-select: text !important;
  -moz-user-select: text !important;
  -ms-user-select: text !important;
}
#translation-chatbot *,
#translation-chatbot .message,
#translation-chatbot .message *,
#translation-chatbot .wrap,
#translation-chatbot .wrap *,
#translation-chatbot .message-body,
#translation-chatbot .markdown,
#translation-chatbot .prose,
#translation-chatbot [class*="message"],
#translation-chatbot [class*="content"] {
  user-select: text !important;
  -webkit-user-select: text !important;
  -moz-user-select: text !important;
  -ms-user-select: text !important;
  cursor: text !important;
}
#translation-chatbot .message {
  padding: 14px 18px !important;
  border-radius: 10px !important;
}
#translation-chatbot .message.user {
  background: var(--pht-primary-light) !important;
  border-left: 4px solid var(--pht-primary) !important;
}
.dark #translation-chatbot .message.user {
  background: rgba(13, 148, 136, 0.2) !important;
}

/* ========== 选项行 ========== */
.options-row {
  gap: 16px !important;
  margin-bottom: 16px !important;
}
.option-dropdown label {
  font-weight: 600 !important;
  color: var(--pht-text) !important;
}
.option-dropdown .wrap {
  border-radius: var(--pht-radius) !important;
  border: 1px solid var(--pht-border) !important;
  transition: box-shadow 0.2s ease !important;
}
.option-dropdown .wrap:focus-within {
  box-shadow: 0 0 0 2px var(--pht-primary-light) !important;
  border-color: var(--pht-primary) !important;
}

/* ========== 输入框 ========== */
.input-row {
  margin-bottom: 20px !important;
}
.translation-input textarea {
  border-radius: var(--pht-radius) !important;
  border: 1px solid var(--pht-border) !important;
  padding: 14px 16px !important;
  font-size: 0.95rem !important;
  line-height: 1.6 !important;
  transition: border-color 0.2s ease, box-shadow 0.2s ease !important;
}
.translation-input textarea:focus {
  border-color: var(--pht-primary) !important;
  box-shadow: 0 0 0 2px var(--pht-primary-light) !important;
  outline: none !important;
}
/* 输入框可选中、可复制 */
.translation-input,
.translation-input textarea,
.translation-input .wrap {
  user-select: text !important;
  -webkit-user-select: text !important;
  -moz-user-select: text !important;
  -ms-user-select: text !important;
}

/* ========== 按钮 ========== */
.actions-row {
  gap: 12px !important;
  flex-wrap: wrap !important;
}
.btn-primary {
  background: var(--pht-primary) !important;
  color: white !important;
  border: none !important;
  border-radius: 10px !important;
  padding: 12px 28px !important;
  font-weight: 600 !important;
  font-size: 0.95rem !important;
  transition: background 0.2s ease, transform 0.1s ease !important;
  box-shadow: var(--pht-shadow) !important;
}
.btn-primary:hover {
  background: var(--pht-primary-hover) !important;
  transform: translateY(-1px) !important;
}
.btn-secondary {
  background: transparent !important;
  color: var(--pht-text) !important;
  border: 2px solid var(--pht-border) !important;
  border-radius: 10px !important;
  padding: 10px 24px !important;
  font-weight: 500 !important;
  transition: border-color 0.2s ease, background 0.2s ease !important;
}
.btn-secondary:hover {
  border-color: var(--pht-primary) !important;
  color: var(--pht-primary) !important;
  background: var(--pht-primary-light) !important;
}
.dark .btn-secondary:hover {
  background: rgba(13, 148, 136, 0.15) !important;
}

/* ========== 文件翻译按钮全宽 ========== */
#file-translate-btn {
  width: 100% !important;
  display: block !important;
  margin-bottom: 12px !important;
}

/* ========== 保留原有样式 ========== */
.duplicate-button {
  margin: auto !important;
  color: white !important;
  background: black !important;
  border-radius: 100vh !important;
}

.modal-box {
  position: fixed !important;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  max-width: 1000px;
  max-height: 750px;
  overflow-y: auto;
  background-color: var(--input-background-fill);
  flex-wrap: nowrap !important;
  border: 2px solid var(--pht-border) !important;
  border-radius: 16px !important;
  z-index: 1000;
  padding: 10px;
  box-shadow: var(--pht-shadow-lg) !important;
}

.dark .modal-box {
  border-color: #475569 !important;
}
"""
