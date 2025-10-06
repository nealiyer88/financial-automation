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
        """Main entry point for file processing."""
        file_path = Path(file_path)
        
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        file_ext = file_path.suffix.lower()
        if file_ext not in self.supported_extensions:
            raise ValueError(f"Unsupported file type: {file_ext}. Supported: {self.supported_extensions}")
        
        try:
            if file_ext == '.csv':
                return self._load_csv(str(file_path))
            elif file_ext in ['.xlsx', '.xls']:
                return self._load_excel(str(file_path))
            elif file_ext == '.json':
                return self._load_json(str(file_path))
            elif file_ext == '.txt':
                return self._load_txt(str(file_path))
            elif file_ext == '.pdf':
                return self._load_pdf(str(file_path))
        except Exception as e:
            self.logger.error(f"Error processing {file_path}: {e}")
            return pd.DataFrame(), self._build_meta("failed", file_ext, error=str(e))

    def process(self, file_path: str) -> Dict[str, Any]:
        """Legacy method for backward compatibility."""
        df, metadata = self.process_file(file_path)
        
        tables = [df.values.tolist()] if not df.empty else []
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
    
    def _try_load(self, loader_func, file_path: str, file_type: str) -> Tuple[pd.DataFrame, Dict[str, Any]]:
        """Helper to try loading file and return standardized format."""
        try:
            df = loader_func(file_path)
            df = self._normalize_headers(df)
            return df, self._build_meta("success", file_type, rows=len(df), columns=len(df.columns))
        except Exception as e:
            return pd.DataFrame(), self._build_meta("failed", file_type, error=str(e))
    
    def _build_meta(self, status: str, file_type: str, **kwargs) -> Dict[str, Any]:
        """Helper to build standardized metadata."""
        meta = {"file_type": file_type, "status": status}
        meta.update(kwargs)
        return meta
    
    def _normalize_headers(self, df: pd.DataFrame) -> pd.DataFrame:
        """Normalize column headers: strip whitespace, lowercase, replace spaces with underscores."""
        if df.empty:
            return df
        
        new_columns = []
        for col in df.columns:
            if col is None:
                new_columns.append('unnamed_column')
            else:
                normalized = str(col).strip().lower()
                normalized = ''.join(c if c.isalnum() else '_' for c in normalized)
                normalized = '_'.join(normalized.split())
                new_columns.append(normalized)
        
        df.columns = new_columns
        return df
    
    def _load_csv(self, file_path: str) -> pd.DataFrame:
        """Load CSV file."""
        return pd.read_csv(file_path)
    
    def _load_excel(self, file_path: str) -> pd.DataFrame:
        """Load Excel file."""
        return pd.read_excel(file_path)
    
    def _load_json(self, file_path: str) -> pd.DataFrame:
        """Load JSON file and convert to DataFrame."""
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        if isinstance(data, list):
            return pd.DataFrame(data)
        elif isinstance(data, dict):
            return pd.DataFrame(data['data'] if 'data' in data else [data])
        else:
            return pd.DataFrame()
    
    def _load_txt(self, file_path: str) -> pd.DataFrame:
        """Load TXT file and attempt to parse as CSV."""
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        try:
            return pd.read_csv(StringIO(content))
        except:
            lines = content.strip().split('\n')
            return pd.DataFrame({'text': lines})
    
    def _load_pdf(self, file_path: str) -> pd.DataFrame:
        """Minimal PDF processing using pdfplumber as fallback."""
        with pdfplumber.open(file_path) as pdf:
            text_content = ""
            for page in pdf.pages:
                text_content += page.extract_text() or ""
        
        # Try to parse as CSV if tabular
        if ',' in text_content and '\n' in text_content:
            try:
                return pd.read_csv(StringIO(text_content))
            except:
                pass
        
        # Fallback: return raw text (first 1000 chars)
        raw_text = text_content[:1000] if text_content else ""
        return pd.DataFrame({'raw_text': [raw_text]})


# Legacy function exports for backward compatibility
def load_csv(file_path: str) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """Legacy function for backward compatibility."""
    agent = DocProcessorAgent()
    return agent._try_load(agent._load_csv, file_path, "csv")

def load_excel(file_path: str) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """Legacy function for backward compatibility."""
    agent = DocProcessorAgent()
    return agent._try_load(agent._load_excel, file_path, "excel")

def load_json(file_path: str) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """Legacy function for backward compatibility."""
    agent = DocProcessorAgent()
    return agent._try_load(agent._load_json, file_path, "json")

def load_txt(file_path: str) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """Legacy function for backward compatibility."""
    agent = DocProcessorAgent()
    return agent._try_load(agent._load_txt, file_path, "txt")

def load_pdf(file_path: str) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """Legacy function for backward compatibility."""
    agent = DocProcessorAgent()
    return agent._try_load(agent._load_pdf, file_path, "pdf")

def normalize_headers(df: pd.DataFrame) -> pd.DataFrame:
    """Legacy function for backward compatibility."""
    agent = DocProcessorAgent()
    return agent._normalize_headers(df)