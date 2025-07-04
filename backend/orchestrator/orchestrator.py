# backend/orchestrator/orchestrator.py

class Orchestrator:
    """
    Modular, dynamic orchestrator for chaining any agents in any order.
    """

    def __init__(self, agents: dict, agent_sequence: list):
        """
        Args:
            agents (dict): Dictionary of agent instances keyed by agent name.
            agent_sequence (list): List of agent keys in execution order.
        """
        self.agents = agents
        self.agent_sequence = agent_sequence

    def run_pipeline(self, initial_input):
        outputs = {}
        prev_output = initial_input

        for agent_key in self.agent_sequence:
            agent = self.agents[agent_key]
            # Dynamically find the main callable method (skip __ methods)
            method = [
                func for func in dir(agent)
                if not func.startswith("__") and callable(getattr(agent, func))
            ][0]
            result = getattr(agent, method)(prev_output)
            outputs[agent_key] = result
            prev_output = result  # Chain output to next agent by default

        return outputs
