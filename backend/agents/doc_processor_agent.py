import os
import pdfplumber
import fitz  # PyMuPDF
from typing import List, Dict, Any
from pdf2image import convert_from_path
import pytesseract
from pytesseract import Output
import shutil
import logging
import re


class DocProcessorAgent:
    def __init__(self):
        if shutil.which("tesseract") is None:
            logging.warning("Tesseract OCR executable not found in PATH. OCR extraction will fail unless Tesseract is installed and available.")

    def process(self, file_path: str) -> Dict[str, Any]:
        """
        Extract tables from PDF using pdfplumber, fallback to PyMuPDF if needed.

        Args:
            file_path (str): Path to uploaded file

        Returns:
            dict: {
                "html": fallback stub string,
                "json": {
                    "tables": [...],
                    "blocks": [],
                    "metadata": {...}
                }
            }
        """
        logger = logging.getLogger(__name__)
        extraction_status = None
        tables = extract_tables_with_pdfplumber(file_path)
        if tables and not contains_garbage_text(tables):
            extraction_status = "pdfplumber"
        else:
            if not tables:
                logger.warning("Fallback to PyMuPDF: pdfplumber found no tables.")
            else:
                logger.warning("Fallback to PyMuPDF: pdfplumber tables unusable (garbage detected).")
            tables = extract_tables_with_pymupdf(file_path)
            if tables and not contains_garbage_text(tables):
                extraction_status = "fitz"
            else:
                if not tables:
                    logger.warning("Fallback to OCR: fitz found no tables.")
                else:
                    logger.warning("Fallback to OCR: fitz tables unusable (garbage detected).")
                tables = extract_tables_with_ocr(file_path)
                if tables:
                    extraction_status = "ocr"
                else:
                    extraction_status = "FAILED_ALL_METHODS"
        logger.debug(f"Extracted {len(tables)} tables")
        logger.debug(f"Source file: {file_path}")

        return {
            "html": "<html><body><p>Unstructured disabled due to crash</p></body></html>",
            "json": {
                "tables": tables,
                "blocks": [],
                "metadata": {
                    "table_count": len(tables),
                    "block_count": 0,
                    "source_file": os.path.basename(file_path),
                    "extraction_status": extraction_status
                }
            }
        }



def extract_tables_with_pdfplumber(file_path: str) -> List[List[List[str]]]:
    all_tables = []

    try:
        with pdfplumber.open(file_path) as pdf:
            for page_number, page in enumerate(pdf.pages):
                tables = page.extract_tables()
                for table in tables:
                    cleaned_table = [
                        [cell.strip() if cell else "" for cell in row]
                        for row in table
                    ]
                    all_tables.append(cleaned_table)
    except Exception as e:
        print(f"[ERROR] pdfplumber failed: {e}")
        return []

    return all_tables


def extract_tables_with_pymupdf(file_path: str) -> List[List[List[str]]]:
    doc = fitz.open(file_path)
    all_tables = []

    for page_index, page in enumerate(doc):
        words = page.get_text("words")  # returns list of (x0, y0, x1, y1, word, block_no, line_no, word_no)
        words.sort(key=lambda w: (round(w[1], 1), w[0]))  # sort by y, then x

        rows = []
        current_y = None
        current_row = []

        for w in words:
            x0, y0, x1, y1, text, *_ = w
            y_key = round(y0, 1)

            if current_y is None:
                current_y = y_key

            if abs(y_key - current_y) > 1.5:  # new row threshold
                rows.append(current_row)
                current_row = [text]
                current_y = y_key
            else:
                current_row.append(text)

        if current_row:
            rows.append(current_row)

        all_tables.append(rows)

    return all_tables


def contains_garbage_text(tables: List[List[List[str]]]) -> bool:
    """
    Returns True if the tables are likely to be garbled nonsense.
    - Triggers on encoding artifacts (e.g., (cid:, \uFFFD)
    - Triggers if more than 50% of chars in a cell are non-alphanumeric (excluding numbers)
    - Triggers if a row has fewer than 2 word-like cells (at least 2 consecutive letters)
    Numeric values (e.g., '1234', '8,223') are not considered word-like, but do not count as garbage unless the row is mostly symbols or short codes.
    """
    logger = logging.getLogger(__name__)
    non_alpha_threshold = 0.5  # If more than 50% of chars are non-alphanumeric
    min_wordlike_cells = 2     # Require at least 2 word-like cells per row
    for table in tables:
        for row in table:
            wordlike_cells = 0
            for cell in row:
                # Check for encoding artifacts
                if "(cid:" in cell or "\uFFFD" in cell:
                    logger.warning(f"Detected encoding artifact in cell: {cell}")
                    return True
                # Check for mostly non-alphanumeric (excluding numbers)
                if cell:
                    non_alpha = sum(1 for c in cell if not c.isalnum())
                    if len(cell) > 0 and (non_alpha / len(cell)) > non_alpha_threshold:
                        logger.warning(f"Cell has high non-alphanumeric ratio: {cell}")
                        continue
                    # Check for word-like content (at least 2 consecutive letters)
                    if re.search(r"[A-Za-z]{2,}", cell):
                        wordlike_cells += 1
            if wordlike_cells < min_wordlike_cells:
                logger.warning(f"Row has too few word-like cells: {row}")
                return True
    return False

def extract_tables_with_ocr(file_path: str) -> List[List[List[str]]]:
    """
    Fallback: Extract tables from scanned/image-only PDFs using OCR.

    Returns:
        List of tables, each a list of rows, each row a list of strings.
    """
    logger = logging.getLogger(__name__)
    logger.info("Running OCR fallback...")
    try:
        images = convert_from_path(file_path, dpi=300)
        all_tables = []
        for page_num, image in enumerate(images):
            ocr_data = pytesseract.image_to_data(image, output_type=Output.DICT)
            # Step 1: Group words by Y (row)
            row_buckets = {}
            for i in range(len(ocr_data["text"])):
                word = ocr_data["text"][i].strip()
                if not word:
                    continue
                y = ocr_data["top"][i]
                y_rounded = round(y / 10.0) * 10  # cluster y's by row band
                if y_rounded not in row_buckets:
                    row_buckets[y_rounded] = []
                row_buckets[y_rounded].append({
                    "word": word,
                    "x": ocr_data["left"][i]
                })
            # Step 2: For each row, sort/group by X (column)
            sorted_y = sorted(row_buckets.keys())
            page_table = []
            # Heuristic: estimate number of columns from the row with most words
            max_row = max(row_buckets.values(), key=lambda r: len(r)) if row_buckets else []
            n_cols = min(8, max(2, len(max_row)))  # Clamp to [2,8] columns for safety
            # For each row, cluster by X
            for y in sorted_y:
                row = row_buckets[y]
                # Sort words left-to-right
                row_sorted = sorted(row, key=lambda w: w["x"])
                # Get X positions
                x_positions = [w["x"] for w in row_sorted]
                # If enough words, estimate column boundaries
                if len(x_positions) >= n_cols:
                    # Compute column boundaries by splitting X range into n_cols buckets
                    min_x, max_x = min(x_positions), max(x_positions)
                    col_width = (max_x - min_x) / n_cols if n_cols > 1 else 1
                    col_bounds = [min_x + i * col_width for i in range(n_cols + 1)]
                else:
                    # Fallback: treat each word as a column
                    col_bounds = [w["x"] for w in row_sorted] + [row_sorted[-1]["x"] + 100] if row_sorted else []
                # Assign words to columns
                columns = [[] for _ in range(n_cols)]
                for w in row_sorted:
                    col_idx = 0
                    for i in range(n_cols):
                        if w["x"] >= col_bounds[i] and w["x"] < col_bounds[i+1]:
                            col_idx = i
                            break
                    columns[col_idx].append(w["word"])
                # Join words in each column
                clean_row = [" ".join(col).strip() for col in columns if col]
                if any(cell for cell in clean_row):
                    page_table.append(clean_row)
            if page_table:
                all_tables.append(page_table)
        return all_tables
    except Exception as e:
        logger.error(f"OCR extraction failed: {e}")
        return []