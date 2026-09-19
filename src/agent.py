from typing import Callable

from .store import EmbeddingStore


class KnowledgeBaseAgent:
    """
    An agent that answers questions using a vector knowledge base.

    Retrieval-augmented generation (RAG) pattern:
        1. Retrieve top-k relevant chunks from the store.
        2. Build a prompt with the chunks as context.
        3. Call the LLM to generate an answer.
    """

    def __init__(self, store: EmbeddingStore, llm_fn: Callable[[str], str]) -> None:
        self.store = store
        self.llm_fn = llm_fn

    def answer(self, question: str, top_k: int = 3) -> str:
        retrieved_chunks = self.store.search(question, top_k=top_k)

        context_parts = []
        for index, result in enumerate(retrieved_chunks, start=1):
            content = result.get("content", "")
            if content:
                context_parts.append(f"[Chunk {index}]\n{content}")

        context = "\n\n".join(context_parts)
        prompt = (
            "Bạn là trợ lý trả lời câu hỏi dựa trên ngữ cảnh được cung cấp. "
            "Chỉ sử dụng thông tin trong ngữ cảnh. Nếu ngữ cảnh không có đủ "
            "thông tin, hãy nói rằng không tìm thấy câu trả lời trong tài liệu.\n\n"
            f"Ngữ cảnh:\n{context}\n\n"
            f"Câu hỏi: {question}\n"
            "Trả lời:"
        )

        return self.llm_fn(prompt)
