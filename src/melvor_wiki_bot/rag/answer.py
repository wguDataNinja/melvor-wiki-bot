"""
Answer-building from retrieved wiki chunks.
"""

from typing import List

from melvor_wiki_bot.rag.chunking import WikiChunk


def build_answer_from_chunks(question: str, chunks: List[WikiChunk]) -> str:
    """
    Placeholder answer builder.

    Later this will call an LLM with the question + chunks and return
    an answer that includes citations.
    """
    raise NotImplementedError("build_answer_from_chunks is not implemented yet.")
