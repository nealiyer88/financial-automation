from agents.doc_processor_agent import DocProcessorAgent
from agents.chunker_agent import ChunkerAgent
from agents.metrics_calculator_agent import MetricsCalculatorAgent
from agents.variance_analysis_agent import VarianceAnalysisAgent
from agents.chart_agent import ChartAgent
from agents.llm_answer_agent import LLMAnswerAgent

from orchestrator.orchestrator import Orchestrator

def main():
    agents = {
        "doc_processor": DocProcessorAgent(),
        "chunker": ChunkerAgent(),
        "metrics_calculator": MetricsCalculatorAgent(),
        "variance_analysis": VarianceAnalysisAgent(),
        "chart": ChartAgent(),
        "llm_answer": LLMAnswerAgent(),
    }

    agent_sequence = [
        "doc_processor",
        "chunker",
        "metrics_calculator",
        "variance_analysis",
        "chart",
        "llm_answer"
    ]

    orchestrator = Orchestrator(agents, agent_sequence)
    file_path = "dummy_file_path"
    results = orchestrator.run_pipeline(file_path)

    print("Pipeline Outputs:")
    for step, output in results.items():
        print(f"{step}: {output}")

if __name__ == "__main__":
    main()
