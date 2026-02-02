from typing import List, Optional
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_chroma import Chroma
from langchain_core.documents import Document
from sqlalchemy.orm import Session
import chromadb

from app.config import settings
from app.models.task import Task
from app.models.project import Project

_embeddings: Optional[GoogleGenerativeAIEmbeddings] = None
_vector_store: Optional[Chroma] = None
_chroma_client: Optional[chromadb.HttpClient] = None


def get_embeddings() -> GoogleGenerativeAIEmbeddings:
    global _embeddings
    if _embeddings is None:
        _embeddings = GoogleGenerativeAIEmbeddings(
            model="gemini-embedding-001", google_api_key=settings.GEMINI_API_KEY
        )
    return _embeddings


def get_chroma_client() -> Optional[chromadb.HttpClient]:
    """Get ChromaDB HTTP client if CHROMA_HOST is configured."""
    global _chroma_client
    if _chroma_client is None and settings.CHROMA_HOST:
        _chroma_client = chromadb.HttpClient(
            host=settings.CHROMA_HOST,
            port=settings.CHROMA_PORT,
        )
    return _chroma_client


def get_vector_store() -> Chroma:
    global _vector_store
    if _vector_store is None:
        _vector_store = Chroma(
            client=get_chroma_client(),
            collection_name="tasks_collection",
            embedding_function=get_embeddings(),
        )
    return _vector_store


def index_data(db: Session) -> int:
    vector_store = get_vector_store()
    tasks = db.query(Task).join(Project).all()

    if not tasks:
        return 0

    documents = []
    ids = []

    for task in tasks:
        assignee_name = task.assignee.full_name if task.assignee else "Unassigned"
        project_name = task.project.name if task.project else "Unknown Project"
        due_date_str = (
            task.due_date.strftime("%Y-%m-%d") if task.due_date else "No due date"
        )

        content = (
            f"Task: {task.title}. "
            f"Description: {task.description or 'No description'}. "
            f"Status: {task.status.value}. "
            f"Priority: {task.priority.value}. "
            f"Assigned to: {assignee_name}. "
            f"Project: {project_name}. "
            f"Due date: {due_date_str}."
        )

        doc = Document(
            page_content=content,
            metadata={
                "task_id": task.id,
                "project_id": task.project_id,
                "status": task.status.value,
                "priority": task.priority.value,
                "assignee_id": task.assignee_id,
            },
        )
        documents.append(doc)
        ids.append(f"task_{task.id}")
    try:
        existing_ids = vector_store.get()["ids"]
        if existing_ids:
            vector_store.delete(ids=existing_ids)
    except Exception:
        pass

    vector_store.add_documents(documents, ids=ids)

    return len(documents)


def retrieve_documents(query: str, top_k: int = 5) -> List[Document]:
    vector_store = get_vector_store()
    retriever = vector_store.as_retriever(search_kwargs={"k": top_k * 2})
    initial_docs = retriever.invoke(query)

    if not initial_docs:
        return []
    try:
        from flashrank import Ranker, RerankRequest

        ranker = Ranker(model_name="ms-marco-MiniLM-L-12-v2", cache_dir="./storage")

        passages = [
            {
                "id": str(doc.metadata.get("task_id", i)),
                "text": doc.page_content,
                "meta": doc.metadata,
            }
            for i, doc in enumerate(initial_docs)
        ]

        rerank_request = RerankRequest(query=query, passages=passages)
        results = ranker.rerank(rerank_request)
        final_docs = []
        for res in results[:top_k]:
            final_docs.append(
                Document(page_content=res["text"], metadata=res.get("meta", {}))
            )
        return final_docs

    except ImportError:
        return initial_docs[:top_k]
    except Exception:
        return initial_docs[:top_k]


def search_tasks(query: str, top_k: int = 5) -> str:
    docs = retrieve_documents(query, top_k)

    if not docs:
        return "No relevant tasks found."

    return "\n\n".join([doc.page_content for doc in docs])
