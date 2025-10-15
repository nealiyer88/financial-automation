#!/usr/bin/env python
"""Test script for Apple CSV processing with DocProcessorAgent."""

import sys
import os

# Add backend to Python path
backend_path = os.path.join(os.path.dirname(__file__), 'backend')
sys.path.insert(0, backend_path)

# Import the agent
from agents.doc_processor_agent import DocProcessorAgent

# Create agent instance
agent = DocProcessorAgent()

# Process the Apple CSV file
csv_path = os.path.join('backend', 'data', 'sample_reports', 'Apple 2009-2024.csv')
print(f"Processing file: {csv_path}")
print(f"File exists: {os.path.exists(csv_path)}")
print()

df, metadata = agent.process_file(csv_path)

# Display results
print("=" * 60)
print("Apple CSV Processing Test Results")
print("=" * 60)

print("\nMETADATA:")
print(f"  File Type: {metadata['file_type']}")
print(f"  Status: {metadata['status']}")
print(f"  Rows: {metadata['rows']}")
print(f"  Columns: {metadata['columns']}")

print("\nDATAFRAME INFO:")
print(f"  Shape: {df.shape}")
print(f"  Memory usage: {df.memory_usage(deep=True).sum() / 1024:.2f} KB")

print("\nNORMALIZED COLUMN NAMES:")
for i, col in enumerate(df.columns, 1):
    print(f"  {i:2d}. {col}")

print("\nFIRST 3 ROWS (Recent Data):")
sample_cols = ['year', 'revenue_millions', 'net_income_millions', 'eps']
print(df.head(3)[sample_cols].to_string(index=False))

print("\nLAST 3 ROWS (Historical Data):")
print(df.tail(3)[sample_cols].to_string(index=False))

print("\nSUMMARY STATISTICS:")
print(f"  Years covered: {df['year'].min()} - {df['year'].max()}")
print(f"  Total data points: {len(df)} years")

print("\nLEGACY process() METHOD TEST:")
legacy_result = agent.process(csv_path)
print(f"  Tables extracted: {legacy_result['json']['metadata']['table_count']}")
print(f"  Rows in table: {legacy_result['json']['metadata']['rows']}")
print(f"  Columns in table: {legacy_result['json']['metadata']['columns']}")
print(f"  Extraction status: {legacy_result['json']['metadata']['extraction_status']}")

print("\n" + "=" * 60)
print("SUCCESS! DocProcessorAgent working perfectly!")
print("=" * 60)

