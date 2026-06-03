import os

import uvicorn

from llmtuner import ChatModel, create_app
from retrieval.retrieval.retrieval.documents_embedding import DocumentsEmbedding


def main():
    documentsEmbedding = None
    chat_model = ChatModel()
    app = create_app(chat_model, documentsEmbedding)
    print("Visit http://localhost:{}/docs for API document.".format(os.environ.get("API_PORT", 8001)))
    uvicorn.run(app, host="IP", port=int(os.environ.get("API_PORT", 8001)), workers=1)


if __name__ == "__main__":
    main()
