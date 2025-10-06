import pytest
import pandas as pd
import tempfile
import os
import json
from pathlib import Path

# Add backend to path for imports
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from agents.doc_processor_agent import (
    DocProcessorAgent, 
    load_csv, 
    load_excel, 
    load_json, 
    load_txt, 
    load_pdf, 
    normalize_headers
)


class TestDocProcessorAgent:
    """Test suite for the refactored DocProcessorAgent."""
    
    def setup_method(self):
        """Set up test fixtures before each test method."""
        self.agent = DocProcessorAgent()
        self.temp_dir = tempfile.mkdtemp()
    
    def teardown_method(self):
        """Clean up after each test method."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_csv_happy_path(self):
        """Test CSV file processing happy path."""
        csv_content = "Name,Age,City\nJohn,25,New York\nJane,30,Los Angeles"
        csv_path = os.path.join(self.temp_dir, "test.csv")
        
        with open(csv_path, 'w') as f:
            f.write(csv_content)
        
        df, metadata = self.agent.process_file(csv_path)
        
        assert not df.empty
        assert len(df) == 2
        assert len(df.columns) == 3
        assert list(df.columns) == ['name', 'age', 'city']
        assert metadata['file_type'] == 'csv'
        assert metadata['status'] == 'success'
        assert metadata['rows'] == 2
        assert metadata['columns'] == 3
    
    def test_excel_happy_path(self):
        """Test Excel file processing happy path."""
        excel_data = {
            'Product Name': ['Widget A', 'Widget B'],
            'Price': [10.99, 15.50],
            'Quantity': [100, 50]
        }
        df_test = pd.DataFrame(excel_data)
        excel_path = os.path.join(self.temp_dir, "test.xlsx")
        df_test.to_excel(excel_path, index=False)
        
        df, metadata = self.agent.process_file(excel_path)
        
        assert not df.empty
        assert len(df) == 2
        assert len(df.columns) == 3
        assert list(df.columns) == ['product_name', 'price', 'quantity']
        assert metadata['file_type'] == 'excel'
        assert metadata['status'] == 'success'
        assert metadata['rows'] == 2
        assert metadata['columns'] == 3
    
    def test_json_happy_path(self):
        """Test JSON file processing happy path."""
        json_data = [
            {"id": 1, "name": "Item 1", "value": 100},
            {"id": 2, "name": "Item 2", "value": 200}
        ]
        json_path = os.path.join(self.temp_dir, "test.json")
        
        with open(json_path, 'w') as f:
            json.dump(json_data, f)
        
        df, metadata = self.agent.process_file(json_path)
        
        assert not df.empty
        assert len(df) == 2
        assert len(df.columns) == 3
        assert list(df.columns) == ['id', 'name', 'value']
        assert metadata['file_type'] == 'json'
        assert metadata['status'] == 'success'
        assert metadata['rows'] == 2
        assert metadata['columns'] == 3
    
    def test_txt_csv_happy_path(self):
        """Test TXT file with CSV content."""
        txt_content = "Name,Score\nAlice,95\nBob,87"
        txt_path = os.path.join(self.temp_dir, "test.txt")
        
        with open(txt_path, 'w') as f:
            f.write(txt_content)
        
        df, metadata = self.agent.process_file(txt_path)
        
        assert not df.empty
        assert len(df) == 2
        assert len(df.columns) == 2
        assert list(df.columns) == ['name', 'score']
        assert metadata['file_type'] == 'txt_csv'
        assert metadata['status'] == 'success'
        assert metadata['rows'] == 2
        assert metadata['columns'] == 2
    
    def test_txt_plain_happy_path(self):
        """Test TXT file with plain text content."""
        txt_content = "Line 1\nLine 2\nLine 3"
        txt_path = os.path.join(self.temp_dir, "test.txt")
        
        with open(txt_path, 'w') as f:
            f.write(txt_content)
        
        df, metadata = self.agent.process_file(txt_path)
        
        assert not df.empty
        assert len(df) == 3
        assert len(df.columns) == 1
        assert list(df.columns) == ['text']
        assert metadata['file_type'] == 'txt'
        assert metadata['status'] == 'success'
        assert metadata['rows'] == 3
        assert metadata['columns'] == 1
    
    def test_unsupported_extension_raises_error(self):
        """Test that unsupported file extensions raise ValueError."""
        unsupported_path = os.path.join(self.temp_dir, "test.xyz")
        with open(unsupported_path, 'w') as f:
            f.write("test content")
        
        with pytest.raises(ValueError, match="Unsupported file type"):
            self.agent.process_file(unsupported_path)
    
    def test_file_not_found_raises_error(self):
        """Test that non-existent files raise FileNotFoundError."""
        non_existent_path = os.path.join(self.temp_dir, "nonexistent.csv")
        
        with pytest.raises(FileNotFoundError):
            self.agent.process_file(non_existent_path)
    
    def test_legacy_process_method(self):
        """Test legacy process method for backward compatibility."""
        csv_content = "Name,Age\nJohn,25"
        csv_path = os.path.join(self.temp_dir, "test.csv")
        
        with open(csv_path, 'w') as f:
            f.write(csv_content)
        
        result = self.agent.process(csv_path)
        
        assert 'html' in result
        assert 'json' in result
        assert 'tables' in result['json']
        assert 'metadata' in result['json']
        assert result['json']['metadata']['status'] == 'success'
        assert len(result['json']['tables']) == 1
        assert len(result['json']['tables'][0]) == 1  # 1 row
        assert len(result['json']['tables'][0][0]) == 2  # 2 columns


class TestHelperFunctions:
    """Test suite for helper functions."""
    
    def test_normalize_headers(self):
        """Test column header normalization."""
        df = pd.DataFrame({
            '  Name  ': ['John', 'Jane'],
            'Age (Years)': [25, 30],
            'City/State': ['NY', 'CA'],
            'Email-Address': ['john@test.com', 'jane@test.com'],
            None: ['data1', 'data2']
        })
        
        normalized_df = normalize_headers(df)
        
        expected_columns = ['name', 'age_years', 'city_state', 'email_address', 'unnamed_column']
        assert list(normalized_df.columns) == expected_columns
        assert normalized_df.shape == (2, 5)
    
    def test_normalize_headers_empty_dataframe(self):
        """Test normalize_headers with empty DataFrame."""
        df = pd.DataFrame()
        normalized_df = normalize_headers(df)
        
        assert normalized_df.empty
        assert list(normalized_df.columns) == []


class TestLegacyFunctions:
    """Test suite for legacy function exports."""
    
    def setup_method(self):
        """Set up test fixtures before each test method."""
        self.temp_dir = tempfile.mkdtemp()
    
    def teardown_method(self):
        """Clean up after each test method."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_load_csv_legacy(self):
        """Test legacy load_csv function."""
        csv_content = "Name,Age\nJohn,25\nJane,30"
        csv_path = os.path.join(self.temp_dir, "test.csv")
        
        with open(csv_path, 'w') as f:
            f.write(csv_content)
        
        df, metadata = load_csv(csv_path)
        
        assert not df.empty
        assert len(df) == 2
        assert list(df.columns) == ['name', 'age']
        assert metadata['file_type'] == 'csv'
        assert metadata['status'] == 'success'
    
    def test_load_excel_legacy(self):
        """Test legacy load_excel function."""
        excel_data = {'Name': ['John'], 'Age': [25]}
        df_test = pd.DataFrame(excel_data)
        excel_path = os.path.join(self.temp_dir, "test.xlsx")
        df_test.to_excel(excel_path, index=False)
        
        df, metadata = load_excel(excel_path)
        
        assert not df.empty
        assert list(df.columns) == ['name', 'age']
        assert metadata['file_type'] == 'excel'
        assert metadata['status'] == 'success'
    
    def test_load_json_legacy(self):
        """Test legacy load_json function."""
        json_data = [{"id": 1, "name": "Test"}]
        json_path = os.path.join(self.temp_dir, "test.json")
        
        with open(json_path, 'w') as f:
            json.dump(json_data, f)
        
        df, metadata = load_json(json_path)
        
        assert not df.empty
        assert list(df.columns) == ['id', 'name']
        assert metadata['file_type'] == 'json'
        assert metadata['status'] == 'success'
    
    def test_load_txt_legacy(self):
        """Test legacy load_txt function."""
        txt_content = "Name,Age\nJohn,25"
        txt_path = os.path.join(self.temp_dir, "test.txt")
        
        with open(txt_path, 'w') as f:
            f.write(txt_content)
        
        df, metadata = load_txt(txt_path)
        
        assert not df.empty
        assert list(df.columns) == ['name', 'age']
        assert metadata['file_type'] == 'txt_csv'
        assert metadata['status'] == 'success'


class TestErrorHandling:
    """Test suite for error handling scenarios."""
    
    def setup_method(self):
        """Set up test fixtures before each test method."""
        self.agent = DocProcessorAgent()
        self.temp_dir = tempfile.mkdtemp()
    
    def teardown_method(self):
        """Clean up after each test method."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_corrupted_csv_handling(self):
        """Test handling of corrupted CSV files."""
        # Create a CSV with encoding issues
        csv_path = os.path.join(self.temp_dir, "corrupted.csv")
        with open(csv_path, 'w', encoding='utf-8') as f:
            f.write("Name,Age\nJohn,25\nJane,30\x00")  # Null byte
        
        df, metadata = self.agent.process_file(csv_path)
        
        # Should still work or return empty with error
        assert metadata['file_type'] == 'csv'
        # Either success or failed status is acceptable
    
    def test_empty_file_handling(self):
        """Test handling of empty files."""
        empty_path = os.path.join(self.temp_dir, "empty.csv")
        with open(empty_path, 'w') as f:
            pass  # Empty file
        
        df, metadata = self.agent.process_file(empty_path)
        
        assert df.empty
        assert metadata['file_type'] == 'csv'
        assert metadata['rows'] == 0
        assert metadata['columns'] == 0


if __name__ == "__main__":
    # Run tests if executed directly
    pytest.main([__file__, "-v"])