
# pip install llama-parse llama-index
# Bash :  export LLAMA_PARSE_API_KEY="your_api_key_here"
from llama_parse import LlamaParse

from llama_parse import LlamaParse
import os

def extract_text_llamaparse(file_path: str) -> str:
    """
    Extract text from PDF using LlamaParse
    Returns combined text from all parsed documents
    """

    api_key = os.getenv("LLAMA_PARSE_API_KEY")
    if not api_key:
        raise ValueError("LLAMA_PARSE_API_KEY not set")

    parser = LlamaParse(
        api_key=api_key,
        result_type="markdown"  # options: "markdown" or "text"
    )

    documents = parser.load_data(file_path)

    text = []
    for doc in documents:
        if hasattr(doc, "text") and doc.text:
            text.append(doc.text)

    return "\n".join(text)