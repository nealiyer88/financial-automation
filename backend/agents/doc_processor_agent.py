class DocProcessorAgent:
    def __init__(self):
        pass

    def process(self, file_path):
        """
        Converts an input file into HTML and JSON.
        """
        tables = extract_tables_with_pdfplumber(file_path)
        print(tables)  # TEMP: just to inspect output for now

        return {
            "html": "<html>stub</html>",
            "json": {
                "tables": tables
            }
        }

# ADD THIS OUTSIDE THE CLASS ↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓
import pdfplumber
from typing import List

def extract_tables_with_pdfplumber(file_path: str) -> List[List[List[str]]]:
    """
    Extracts all tables from all pages of a PDF using pdfplumber.
    """
    all_tables = []

    try:
        with pdfplumber.open(file_path) as pdf:
            for page_number, page in enumerate(pdf.pages):
                tables = page.extract_tables()
                for table in tables:
                    cleaned_table = []
                    for row in table:
                        cleaned_row = [cell.strip() if cell else "" for cell in row]
                        cleaned_table.append(cleaned_row)
                    all_tables.append(cleaned_table)

    except Exception as e:
        print(f"[ERROR] Failed to extract tables: {e}")
        return []

    return all_tables
