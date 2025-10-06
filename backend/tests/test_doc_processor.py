import pytest
import pandas as pd
import tempfile
import os
import json

# Add backend to path for imports
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from agents.doc_processor_agent import DocProcessorAgent, load_csv, normalize_headers


class TestDocProcessorAgent:
    def setup_method(self):
        self.agent = DocProcessorAgent()
        self.temp_dir = tempfile.mkdtemp()
    
    def teardown_method(self):
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    @pytest.mark.parametrize("ext,content,expected_cols", [
        ("csv", "Name,Age\nJohn,25\nJane,30", ['name', 'age']),
        ("xlsx", {"Name": ["John"], "Age": [25]}, ['name', 'age']),
        ("json", [{"id": 1, "name": "Test"}], ['id', 'name']),
        ("txt", "Name,Score\nAlice,95", ['name', 'score']),
    ])
    def test_file_types(self, ext, content, expected_cols):
        if ext == "csv":
            file_path = os.path.join(self.temp_dir, "test.csv")
            with open(file_path, 'w') as f: f.write(content)
        elif ext == "xlsx":
            file_path = os.path.join(self.temp_dir, "test.xlsx")
            pd.DataFrame(content).to_excel(file_path, index=False)
        elif ext == "json":
            file_path = os.path.join(self.temp_dir, "test.json")
            with open(file_path, 'w') as f: json.dump(content, f)
        elif ext == "txt":
            file_path = os.path.join(self.temp_dir, "test.txt")
            with open(file_path, 'w') as f: f.write(content)
        
        df, metadata = self.agent.process_file(file_path)
        assert not df.empty
        assert list(df.columns) == expected_cols
        assert metadata['status'] == 'success'
    
    def test_errors(self):
        # Unsupported extension
        with pytest.raises(ValueError):
            self.agent.process_file("test.xyz")
        # File not found
        with pytest.raises(FileNotFoundError):
            self.agent.process_file("nonexistent.csv")
    
    def test_legacy_process(self):
        csv_path = os.path.join(self.temp_dir, "test.csv")
        with open(csv_path, 'w') as f: f.write("Name,Age\nJohn,25")
        result = self.agent.process(csv_path)
        assert 'tables' in result['json']
        assert len(result['json']['tables']) == 1


class TestHelpers:
    def test_normalize_headers(self):
        df = pd.DataFrame({'  Name  ': ['John'], 'Age (Years)': [25], None: ['data']})
        normalized = normalize_headers(df)
        assert list(normalized.columns) == ['name', 'age_years', 'unnamed']
    
    def test_legacy_functions(self):
        csv_path = os.path.join(tempfile.mkdtemp(), "test.csv")
        with open(csv_path, 'w') as f: f.write("Name,Age\nJohn,25")
        try:
            df, meta = load_csv(csv_path)
            assert not df.empty
            assert meta['status'] == 'success'
        finally:
            os.unlink(csv_path)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])