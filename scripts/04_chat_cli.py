# scripts/04_chat_cli.py

import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from dotenv import load_dotenv
load_dotenv()

from langchain_community.vectorstores import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.llms import Ollama
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough, RunnableLambda

INDEX_DIR = "indexes/accidents"

def build_pipeline():
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

    db = Chroma(
        embedding_function=embeddings,
        persist_directory=INDEX_DIR
    )

    retriever = db.as_retriever(search_type="similarity", search_kwargs={"k": 5})

    llm = Ollama(model="llama3")

    prompt = ChatPromptTemplate.from_template("""
You are a mining safety analysis assistant.
Answer ONLY based on the retrieved accident data.
Be concise and factual.

Context:
{context}

Question:
{question}

Answer:
""")

    def extract_question(input: dict):
        return input["question"]

    def format_docs(docs):
        return "\n\n".join([d.page_content for d in docs])

    chain = (
        {
            "context": RunnableLambda(extract_question) | retriever | format_docs,
            "question": RunnablePassthrough()
        }
        | prompt
        | llm
    )

    return chain

def chat():
    chain = build_pipeline()
    print("✅ Mining Safety QA Agent Ready — type 'exit' to quit.\n")

    while True:
        q = input("You: ")
        if q.lower() in ["exit", "quit"]:
            print("👋 Bye")
            break

        try:
            response = chain.invoke({"question": q})
            print("\nAssistant:", response.content, "\n")
        except Exception as e:
            print("Error:", e, "\n")

if __name__ == "__main__":
    chat()
