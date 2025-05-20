from langgraph.graph import StateGraph, END, START
from backend.app.agents.slides_agent import slides_adaptation_agent

def create_prince2_graph():
    workflow = StateGraph(dict)
    workflow.add_node("prince2", slides_adaptation_agent)
    workflow.add_edge(START, "prince2")
    workflow.add_edge("prince2", END)
    return workflow.compile()

agent_graph = create_prince2_graph()
