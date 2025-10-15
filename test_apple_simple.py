import sys
sys.path.insert(0, 'backend')

from agents.doc_processor_agent import DocProcessorAgent

agent = DocProcessorAgent()
df, metadata = agent.process_file('backend/data/sample_reports/Apple 2009-2024.csv')

print("Apple CSV Processing Test")
print("-" * 40)
print("Status:", metadata['status'])
print("Rows:", metadata['rows'])
print("Columns:", metadata['columns'])
print()
print("Column Names:")
for col in df.columns:
    print(" -", col)
print()
print("First 3 rows:")
print(df.head(3))

