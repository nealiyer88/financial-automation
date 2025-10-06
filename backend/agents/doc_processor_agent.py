import os
import pandas as pd
import json
import logging
from typing import Tuple, Dict, Any
from pathlib import Path
import pdfplumber
from io import StringIO

class DocProcessorAgent:
    """
    Modular document processor that prioritizes Excel/CSV/TXT/JSON ingestion
    with minimal PDF fallback using pdfplumber.
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.supported_extensions = {'.csv', '.xlsx', '.xls', '.txt', '.json', '.pdf'}
    
    def process_file(self, file_path: str) -> Tuple[pd.DataFrame, Dict[str, Any]]:
        """
        Main entry point for file processing.
        
        Args:
            file_path (str): Path to the file to process
            
        Returns:
            Tuple[pd.DataFrame, Dict[str, Any]]: DataFrame and metadata JSON
            
        Raises:
            ValueError: If file type is not supported
        """
        file_path = Path(file_path)
        
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        file_ext = file_path.suffix.lower()
        
        if file_ext not in self.supported_extensions:
            raise ValueError(f"Unsupported file type: {file_ext}. Supported: {self.supported_extensions}")
        
        try:
            if file_ext == '.csv':
                return load_csv(str(file_path))
            elif file_ext in ['.xlsx', '.xls']:
                return load_excel(str(file_path))
            elif file_ext == '.json':
                return load_json(str(file_path))
            elif file_ext == '.txt':
                return load_txt(str(file_path))
            elif file_ext == '.pdf':
                return load_pdf(str(file_path))
        except Exception as e:
            self.logger.error(f"Error processing {file_path}: {e}")
            return pd.DataFrame(), {
                "error": str(e),
                "file_type": file_ext,
                "status": "failed"
            }


def load_csv(file_path: str) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """Load CSV file and return DataFrame with normalized headers."""
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
        return pd.DataFrame(), {"error": str(e), "file_type": "csv", "status": "failed"}


def load_excel(file_path: str) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """Load Excel file and return DataFrame with normalized headers."""
    try:
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
        return pd.DataFrame(), {"error": str(e), "file_type": "excel", "status": "failed"}


def load_json(file_path: str) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """Load JSON file and convert to DataFrame."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Handle different JSON structures
        if isinstance(data, list):
            df = pd.DataFrame(data)
        elif isinstance(data, dict):
            # Try to find the main data array
            if 'data' in data:
                df = pd.DataFrame(data['data'])
            else:
                df = pd.DataFrame([data])
        else:
            df = pd.DataFrame()
        
        df = normalize_headers(df)
        
        metadata = {
            "file_type": "json",
            "rows": len(df),
            "columns": len(df.columns),
            "status": "success"
        }
        
        return df, metadata
    except Exception as e:
        return pd.DataFrame(), {"error": str(e), "file_type": "json", "status": "failed"}


def load_txt(file_path: str) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """Load TXT file and attempt to parse as CSV."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Try to parse as CSV
        try:
            df = pd.read_csv(StringIO(content))
            df = normalize_headers(df)
            metadata = {
                "file_type": "txt_csv",
                "rows": len(df),
                "columns": len(df.columns),
                "status": "success"
            }
        except:
            # If not CSV, return as single column
            lines = content.strip().split('\n')
            df = pd.DataFrame({'text': lines})
            metadata = {
                "file_type": "txt",
                "rows": len(df),
                "columns": 1,
                "status": "success"
            }
        
        return df, metadata
    except Exception as e:
        return pd.DataFrame(), {"error": str(e), "file_type": "txt", "status": "failed"}


def load_pdf(file_path: str) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """Minimal PDF processing using pdfplumber as fallback."""
    try:
        with pdfplumber.open(file_path) as pdf:
            text_content = ""
            for page in pdf.pages:
                text_content += page.extract_text() or ""
        
        # Try to parse extracted text as CSV if it looks tabular
        if ',' in text_content and '\n' in text_content:
            try:
                df = pd.read_csv(StringIO(text_content))
                df = normalize_headers(df)
                metadata = {
                    "file_type": "pdf_csv",
                    "rows": len(df),
                    "columns": len(df.columns),
                    "status": "success"
                }
                return df, metadata
            except:
                pass
        
        # Fallback: return raw text (first 1000 chars)
        raw_text = text_content[:1000] if text_content else ""
        df = pd.DataFrame({'raw_text': [raw_text]})
        
        metadata = {
            "file_type": "pdf",
            "rows": 1,
            "columns": 1,
            "raw_text_length": len(text_content),
            "status": "success"
        }
        
        return df, metadata
    except Exception as e:
        return pd.DataFrame(), {"error": str(e), "file_type": "pdf", "status": "failed"}


def normalize_headers(df: pd.DataFrame) -> pd.DataFrame:
    """Normalize column headers: strip whitespace, lowercase, replace spaces with underscores."""
    if df.empty:
        return df
    
    # Create normalized column names
    new_columns = []
    for col in df.columns:
        if col is None:
            new_columns.append('unnamed_column')
        else:
            # Strip whitespace, lowercase, replace spaces and special chars with underscores
            normalized = str(col).strip().lower()
            normalized = ''.join(c if c.isalnum() else '_' for c in normalized)
            normalized = '_'.join(normalized.split())  # Remove multiple underscores
            new_columns.append(normalized)
    
    df.columns = new_columns
    return df


# Legacy compatibility method
def process(self, file_path: str) -> Dict[str, Any]:
    """
    Legacy method for backward compatibility.
    Converts new format to old format.
    """
    df, metadata = self.process_file(file_path)
    
    # Convert DataFrame to old format
    if df.empty:
        tables = []
    else:
        tables = [df.values.tolist()]
    
    return {
        "html": "<html><body><p>Data processed successfully</p></body></html>",
        "json": {
            "tables": tables,
            "blocks": [],
            "metadata": {
                "table_count": len(tables),
                "block_count": 0,
                "source_file": os.path.basename(file_path),
                "extraction_status": metadata.get("status", "unknown"),
                "rows": metadata.get("rows", 0),
                "columns": metadata.get("columns", 0)
            }
        }
    }
