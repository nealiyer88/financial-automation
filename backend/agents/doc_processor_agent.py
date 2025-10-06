import os
import pandas as pd
import json
import logging
import re
from typing import Tuple, Dict, Any
from pathlib import Path
import pdfplumber
from io import StringIO

class DocProcessorAgent:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.supported = {'.csv', '.xlsx', '.xls', '.txt', '.json', '.pdf'}

    def process_file(self, path: str) -> Tuple[pd.DataFrame, Dict[str, Any]]:
        path = Path(path)
        if not path.exists(): raise FileNotFoundError(f"File not found: {path}")
        ext = path.suffix.lower()
        if ext not in self.supported: raise ValueError(f"Unsupported: {ext}")
        loaders = {
            '.csv': pd.read_csv,
            '.xlsx': pd.read_excel, '.xls': pd.read_excel,
            '.json': self._load_json,
            '.txt': self._load_txt,
            '.pdf': self._load_pdf
        }
        return self._try_load(loaders[ext], str(path), ext.strip('.'))

    def process(self, file_path: str) -> Dict[str, Any]:
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

    def _try_load(self, loader, path: str, ftype: str) -> Tuple[pd.DataFrame, Dict[str, Any]]:
        try:
            df = loader(path)
            df = self._normalize(df)
            return df, self._meta('success', ftype, len(df), len(df.columns))
        except Exception as e:
            self.logger.error(f"Error processing {path}: {e}")
            return pd.DataFrame(), self._meta('failed', ftype, 0, 0, str(e))

    def _load_json(self, p: str) -> pd.DataFrame:
        with open(p, 'r', encoding='utf-8') as f: data = json.load(f)
        return pd.DataFrame(data['data'] if isinstance(data, dict) and 'data' in data else data)

    def _load_txt(self, p: str) -> pd.DataFrame:
        with open(p, 'r', encoding='utf-8') as f: c = f.read()
        try: return pd.read_csv(StringIO(c))
        except: return pd.DataFrame({'text': c.splitlines()})

    def _load_pdf(self, p: str) -> pd.DataFrame:
        with pdfplumber.open(p) as pdf:
            text = ''.join(page.extract_text() or '' for page in pdf.pages)
        try: return pd.read_csv(StringIO(text))
        except: return pd.DataFrame({'raw_text': [text[:1000]]})

    def _normalize(self, df: pd.DataFrame) -> pd.DataFrame:
        if df.empty: return df
        df.columns = [re.sub(r'\W+', '_', str(c)).strip('_').lower() or 'unnamed' for c in df.columns]
        return df

    def _meta(self, status: str, ftype: str, rows: int, cols: int, err: str = None) -> Dict[str, Any]:
        m = {'file_type': ftype, 'status': status, 'rows': rows, 'columns': cols}
        if err: m['error'] = err
        return m


# Legacy compatibility functions
def load_csv(file_path: str) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    return DocProcessorAgent()._try_load(pd.read_csv, file_path, 'csv')

def load_excel(file_path: str) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    return DocProcessorAgent()._try_load(pd.read_excel, file_path, 'excel')

def load_json(file_path: str) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    return DocProcessorAgent()._try_load(DocProcessorAgent()._load_json, file_path, 'json')

def load_txt(file_path: str) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    return DocProcessorAgent()._try_load(DocProcessorAgent()._load_txt, file_path, 'txt')

def load_pdf(file_path: str) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    return DocProcessorAgent()._try_load(DocProcessorAgent()._load_pdf, file_path, 'pdf')

def normalize_headers(df: pd.DataFrame) -> pd.DataFrame:
    return DocProcessorAgent()._normalize(df)