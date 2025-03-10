import pandas as pd
from langchain.docstore.document import Document as LangchainDocument
from tqdm import tqdm


def create_knowledge_base(path: str) -> None:
    # Load the CSV file
    df = pd.read_csv(path)
    df = df.iloc[:2]
    print(f"Loaded {len(df)} job postings from {path}")

    # Create LangChain documents from the CSV data
    RAW_KNOWLEDGE_BASE = []

    for _, row in tqdm(df.iterrows()):
        # Combine the job information into the page_content
        job_content = row["description"]

        # Create a LangChain Document with the job content and metadata
        document = LangchainDocument(
            page_content=job_content,
            metadata={
                "source": row["job_url"],
                "title": row["title"],
                "company": row["company"],
                "location": row["location"],
                "job_type": row["job_type"],
                "date_posted": row["date_posted"],
                "company_industry": row["company_industry"],
            },
        )

        RAW_KNOWLEDGE_BASE.append(document)

    return RAW_KNOWLEDGE_BASE

from langchain.text_splitter import RecursiveCharacterTextSplitter
from transformers import AutoTokenizer


def split_documents(
    chunk_size: int,
    knowledge_base: List[LangchainDocument],
    tokenizer_name: str,
) -> List[LangchainDocument]:
    """
    Split documents into chunks of size `chunk_size` characters and return a list of documents.
    """
    text_splitter = RecursiveCharacterTextSplitter.from_huggingface_tokenizer(
        AutoTokenizer.from_pretrained(tokenizer_name),
        chunk_size=chunk_size,
        chunk_overlap=int(chunk_size / 10),
        add_start_index=True,
        strip_whitespace=True,
        separators=["\n\n", "\n", ".", " ", ""],
    )

    docs_processed = []
    for doc in knowledge_base:
        docs_processed += text_splitter.split_documents([doc])

    # Remove duplicates
    unique_texts = {}
    docs_processed_unique = []
    for doc in docs_processed:
        if doc.page_content not in unique_texts:
            unique_texts[doc.page_content] = True
            docs_processed_unique.append(doc)

    return docs_processed_unique


if __name__ == "__main__":
    print(create_knowledge_base("/home/seif/job-agent/data/jobs-reserve.csv"))
