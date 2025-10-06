import pytest
import pandas as pd
import os
import tempfile
import json
from unittest.mock import patch, mock_open
from agents.doc_processor_agent import DocProcessorAgent, load_csv, load_excel, load_json


class TestDocProcessorAgent:
    """Unit tests for DocProcessorAgent."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.agent = DocProcessorAgent()
        self.temp_dir = tempfile.mkdtemp()
    
    def teardown_method(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_csv_happy_path(self):
        """Test CSV file processing happy path."""
        # Create test CSV file
        csv_content = "Name,Age,City\nJohn,25,New York\nJane,30,Los Angeles"
        csv_path = os.path.join(self.temp_dir, "test.csv")
        
        with open(csv_path, 'w') as f:
            f.write(csv_content)
        
        # Test the agent
        df, metadata = self.agent.process_file(csv_path)
        
        # Assertions
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
        # Create test Excel file
        excel_path = os.path.join(self.temp_dir, "test.xlsx")
        test_data = pd.DataFrame({
            'Product Name': ['Widget A', 'Widget B'],
            'Price': [10.99, 15.50],
            'Quantity': [100, 50]
        })
        test_data.to_excel(excel_path, index=False)
        
        # Test the agent
        df, metadata = self.agent.process_file(excel_path)
        
        # Assertions
        assert not df.empty
        assert len(df) == 2
        assert len(df.columns) == 3
        assert 'product_name' in df.columns
        assert 'price' in df.columns
        assert 'quantity' in df.columns
        assert metadata['file_type'] == 'excel'
        assert metadata['status'] == 'success'
    
    def test_unsupported_extension_raises_error(self):
        """Test that unsupported file extensions raise ValueError."""
        unsupported_path = os.path.join(self.temp_dir, "test.xyz")
        
        with pytest.raises(ValueError, match="Unsupported file type"):
            self.agent.process_file(unsupported_path)
    
    def test_nonexistent_file_raises_error(self):
        """Test that nonexistent files raise FileNotFoundError."""
        nonexistent_path = os.path.join(self.temp_dir, "nonexistent.csv")
        
        with pytest.raises(FileNotFoundError):
            self.agent.process_file(nonexistent_path)
    
    def test_json_processing(self):
        """Test JSON file processing."""
        # Create test JSON file
        json_data = [
            {"id": 1, "name": "Item 1", "value": 100},
            {"id": 2, "name": "Item 2", "value": 200}
        ]
        json_path = os.path.join(self.temp_dir, "test.json")
        
        with open(json_path, 'w') as f:
            json.dump(json_data, f)
        
        # Test the agent
        df, metadata = self.agent.process_file(json_path)
        
        # Assertions
        assert not df.empty
        assert len(df) == 2
        assert len(df.columns) == 3
        assert 'id' in df.columns
        assert 'name' in df.columns
        assert 'value' in df.columns
        assert metadata['file_type'] == 'json'
        assert metadata['status'] == 'success'
    
    def test_txt_processing(self):
        """Test TXT file processing."""
        # Create test TXT file with CSV-like content
        txt_content = "Name,Age\nJohn,25\nJane,30"
        txt_path = os.path.join(self.temp_dir, "test.txt")
        
        with open(txt_path, 'w') as f:
            f.write(txt_content)
        
        # Test the agent
        df, metadata = self.agent.process_file(txt_path)
        
        # Assertions
        assert not df.empty
        assert metadata['file_type'] == 'txt'
        assert metadata['status'] == 'success'
    
    def test_pdf_processing_fallback(self):
        """Test PDF processing fallback."""
        # This test would require a mock PDF file or mocking pdfplumber
        # For now, we'll test the error handling
        pdf_path = os.path.join(self.temp_dir, "test.pdf")
        
        # Create an empty file to simulate PDF
        with open(pdf_path, 'w') as f:
            f.write("")
        
        # Test the agent (should handle gracefully)
        df, metadata = self.agent.process_file(pdf_path)
        
        # Should return empty DataFrame with error metadata
        assert df.empty
        assert metadata['file_type'] == 'pdf'
        assert metadata['status'] == 'failed'


class TestHelperFunctions:
    """Test individual helper functions."""
    
    def test_load_csv_function(self):
        """Test load_csv helper function."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write("Name,Age\nJohn,25\nJane,30")
            csv_path = f.name
        
        try:
            df, metadata = load_csv(csv_path)
            assert not df.empty
            assert len(df) == 2
            assert metadata['file_type'] == 'csv'
        finally:
            os.unlink(csv_path)
    
    def test_load_excel_function(self):
        """Test load_excel helper function."""
        with tempfile.NamedTemporaryFile(suffix='.xlsx', delete=False) as f:
            excel_path = f.name
        
        try:
            # Create test data
            test_data = pd.DataFrame({'A': [1, 2], 'B': [3, 4]})
            test_data.to_excel(excel_path, index=False)
            
            df, metadata = load_excel(excel_path)
            assert not df.empty
            assert len(df) == 2
            assert metadata['file_type'] == 'excel'
        finally:
            os.unlink(excel_path)
    
    def test_load_json_function(self):
        """Test load_json helper function."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump([{"a": 1, "b": 2}], f)
            json_path = f.name
        
        try:
            df, metadata = load_json(json_path)
            assert not df.empty
            assert len(df) == 1
            assert metadata['file_type'] == 'json'
        finally:
            os.unlink(json_path)


if __name__ == "__main__":
    pytest.main([__file__])
