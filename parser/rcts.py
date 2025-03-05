from langchain.text_splitter import RecursiveCharacterTextSplitter


sec_text_doc_splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,
    chunk_overlap=50,
    separators=["\n\n", "\n", ".", " ", ""]
)
