# backend/agents/chunker_agent.py

class ChunkerAgent:
    """
    Modular agent that splits a processed financial document into retrievable chunks
    (sections, tables, paragraphs, etc.) for downstream analysis.
    """

    def __init__(self):
        # Placeholder for future configuration, if needed
        pass

    def chunk(self, doc):
        """
        Splits processed doc into logical chunks.

        Args:
            doc (dict): Output dict from DocProcessorAgent.process()

        Returns:
            list: List of chunk dicts (currently stubbed)
        """
        # TODO: Implement actual chunking logic.
        return [
            {"chunk_id": 0, "text": "stub chunk", "type": "section"}
        ]
