import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from agents.doc_processor_agent import DocProcessorAgent
import logging

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    path = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", "data", "sample_reports", "McDs 2024 Income.pdf")
    )
    logging.debug(f"Exists? {os.path.exists(path)}")
    logging.debug(f"Full path: {path}")

    agent = DocProcessorAgent()
    output = agent.process(path)
    metadata = output["json"]["metadata"]
    logging.info(f"Extraction status: {metadata.get('extraction_status')}")
    print(metadata)
    print("[DEBUG] Tables:")
    for i, table in enumerate(output["json"]["tables"]):
        print(f"\nTable {i+1}:")
        for row in table:
            print(row)

