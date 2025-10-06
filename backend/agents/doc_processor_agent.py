import os
import pandas as pd
import json
import logging
from typing import Tuple, Dict, Any
from io import StringIO
import pdfplumber

logger = logging.getLogger(__name__)


class DocProcessorAgent:
    """
    Modular document processor that prioritizes Excel/CSV/TXT/JSON ingestion
    with minimal PDF fallback using pdfplumber.
    """
    
    def __init__(self):
        """Initialize the document processor."""
        self.supported_extensions = {'.csv', '.xlsx', '.xls', '.txt', '.json', '.pdf'}
    
    def process_file(self, file_path: str) -> Tuple[pd.DataFrame, Dict[str, Any]]:
        """
        Main entry point for processing files.
        
        Args:
            file_path (str): Path to the file to process
            
        Returns:
            Tuple[pd.DataFrame, Dict[str, Any]]: DataFrame and metadata dict
            
        Raises:
            ValueError: If file type is unsupported
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
        
        file_ext = os.path.splitext(file_path)[1].lower()
        
        if file_ext not in self.supported_extensions:
            raise ValueError(f"Unsupported file type: {file_ext}")
        
        try:
            if file_ext == '.csv':
                return load_csv(file_path)
            elif file_ext in ['.xlsx', '.xls']:
                return load_excel(file_path)
            elif file_ext == '.json':
                return load_json(file_path)
            elif file_ext == '.txt':
                return load_txt(file_path)
            elif file_ext == '.pdf':
                return load_pdf(file_path)
        except Exception as e:
            logger.error(f"Error processing {file_path}: {e}")
            return pd.DataFrame(), {
                "error": str(e),
                "file_type": file_ext,
                "status": "failed"
            }


def load_csv(file_path: str) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """Load and process CSV file."""
    try:
        df = pd.read_csv(file_path)
        df = normalize_headers(df)
        
        metadata = {
            "file_type": "csv",
            "rows": len(df),
            "columns": len(df.columns),
            "status": "success"
        }
        
        return df, metadata
    except Exception as e:
        logger.error(f"CSV loading failed: {e}")
        return pd.DataFrame(), {"error": str(e), "file_type": "csv", "status": "failed"}


def load_excel(file_path: str) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """Load and process Excel file."""
    try:
        # Read the first sheet by default
        df = pd.read_excel(file_path)
        df = normalize_headers(df)
        
        metadata = {
            "file_type": "excel",
            "rows": len(df),
            "columns": len(df.columns),
            "status": "success"
        }
        
        return df, metadata
    except Exception as e:
        logger.error(f"Excel loading failed: {e}")
        return pd.DataFrame(), {"error": str(e), "file_type": "excel", "status": "failed"}


def load_json(file_path: str) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """Load and process JSON file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Convert to DataFrame if it's a list of dicts
        if isinstance(data, list) and all(isinstance(item, dict) for item in data):
            df = pd.DataFrame(data)
        else:
            # For other JSON structures, create a single-row DataFrame
            df = pd.DataFrame([data])
        
        df = normalize_headers(df)
        
        metadata = {
            "file_type": "json",
            "rows": len(df),
            "columns": len(df.columns),
            "status": "success"
        }
        
        return df, metadata
    except Exception as e:
        logger.error(f"JSON loading failed: {e}")
        return pd.DataFrame(), {"error": str(e), "file_type": "json", "status": "failed"}


def load_txt(file_path: str) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """Load and process TXT file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Try to parse as CSV if it looks tabular
        lines = content.strip().split('\n')
        if len(lines) > 1 and ',' in lines[0]:
            try:
                df = pd.read_csv(StringIO(content))
                df = normalize_headers(df)
            except:
                # If CSV parsing fails, treat as raw text
                df = pd.DataFrame({'text': [content[:1000]]})  # First 1000 chars
        else:
            # Treat as raw text
            df = pd.DataFrame({'text': [content[:1000]]})
        
        metadata = {
            "file_type": "txt",
            "rows": len(df),
            "columns": len(df.columns),
            "status": "success"
        }
        
        return df, metadata
    except Exception as e:
        logger.error(f"TXT loading failed: {e}")
        return pd.DataFrame(), {"error": str(e), "file_type": "txt", "status": "failed"}


def load_pdf(file_path: str) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """Minimal PDF processing using pdfplumber."""
    try:
        with pdfplumber.open(file_path) as pdf:
            text_content = ""
            for page in pdf.pages:
                text_content += page.extract_text() or ""
        
        # Try to parse as CSV if it looks tabular
        if ',' in text_content and '\n' in text_content:
            try:
                df = pd.read_csv(StringIO(text_content))
                df = normalize_headers(df)
                
                metadata = {
                    "file_type": "pdf",
                    "rows": len(df),
                    "columns": len(df.columns),
                    "status": "success",
                    "extraction_method": "pdfplumber_csv"
                }
                return df, metadata
            except:
                pass
        
        # Fallback to raw text
        df = pd.DataFrame({'raw_text': [text_content[:1000]]})
        
        metadata = {
            "file_type": "pdf",
            "rows": 1,
            "columns": 1,
            "status": "success",
            "extraction_method": "pdfplumber_text"
        }
        
        return df, metadata
    except Exception as e:
        logger.error(f"PDF loading failed: {e}")
        return pd.DataFrame(), {"error": str(e), "file_type": "pdf", "status": "failed"}


def normalize_headers(df: pd.DataFrame) -> pd.DataFrame:
    """Normalize column headers: strip whitespace, lowercase, replace spaces with underscores."""
    if df.empty:
        return df
    
    # Create normalized column names
    normalized_columns = []
    for col in df.columns:
        if isinstance(col, str):
            # Strip whitespace, lowercase, replace spaces and special chars with underscores
            normalized = col.strip().lower().replace(' ', '_').replace('-', '_')
            # Remove multiple underscores and non-alphanumeric chars except underscores
            normalized = '_'.join(filter(None, normalized.split('_')))
            normalized = ''.join(c if c.isalnum() or c == '_' else '' for c in normalized)
            # Ensure it doesn't start with a number
            if normalized and normalized[0].isdigit():
                normalized = f"col_{normalized}"
            # Ensure it's not empty
            if not normalized:
                normalized = f"col_{len(normalized_columns)}"
        else:
            normalized = f"col_{len(normalized_columns)}"
        
        normalized_columns.append(normalized)
    
    # Handle duplicate column names
    final_columns = []
    seen = set()
    for col in normalized_columns:
        if col in seen:
            counter = 1
            while f"{col}_{counter}" in seen:
                counter += 1
            final_columns.append(f"{col}_{counter}")
            seen.add(f"{col}_{counter}")
        else:
            final_columns.append(col)
            seen.add(col)
    
    df.columns = final_columns
    return df