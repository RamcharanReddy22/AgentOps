from typing import TypedDict
from langgraph.graph import StateGraph, END
from agents.researcher import run_researcher
from agents.analyst import run_analyst, get_last_charts
from agents.safety import run_safety
from groq import Groq
from config import GROQ_API_KEY, MODEL, MAX_TOKENS

client = Groq(api_key=GROQ_API_KEY)

class AgentState(TypedDict):
    query: str
    planned_query: str
    research_result: str
    analyst_result: str
    final_report: str
    safety_result: dict
    chart_files: list

def planner_node(state: AgentState) -> dict:
    print("Planner running...")
    response = client.chat.completions.create(
        model=MODEL,
        max_tokens=200,
        messages=[
            {"role": "system", "content": "You are a research planner. Given a query, extract the company name and rewrite it as a clear research objective in one sentence. Return only the rewritten query, nothing else."},
            {"role": "user", "content": state["query"]}
        ]
    )
    planned = response.choices[0].message.content.strip()
    print(f"Planner output: {planned}")
    return {"planned_query": planned}

def researcher_node(state: AgentState) -> dict:
    print("Researcher running...")
    result = run_researcher(state["planned_query"])
    return {"research_result": result}

def analyst_node(state: AgentState) -> dict:
    print("Analyst running...")
    result = run_analyst(f"Financial analysis for: {state['planned_query']}")
    charts = get_last_charts()
    return {"analyst_result": result, "chart_files": charts}

def writer_node(state: AgentState) -> dict:
    print("Writer running...")
    response = client.chat.completions.create(
        model=MODEL,
        max_tokens=MAX_TOKENS,
        messages=[
            {"role": "system", "content": "You are a professional report writer. Combine research and financial analysis into a structured market research report with sections: Executive Summary, Recent Developments, Financial Analysis, Market Position, Key Risks, Conclusion."},
            {"role": "user", "content": f"Query: {state['planned_query']}\n\nResearch:\n{state['research_result']}\n\nFinancial Analysis:\n{state['analyst_result']}\n\nWrite the final report."}
        ]
    )
    return {"final_report": response.choices[0].message.content}

def safety_node(state: AgentState) -> dict:
    print("Safety Agent running...")
    result = run_safety(state["final_report"])
    print(f"Safety result: {result}")
    return {"safety_result": result}

def build_pipeline():
    graph = StateGraph(AgentState)
    graph.add_node("planner", planner_node)
    graph.add_node("researcher", researcher_node)
    graph.add_node("analyst", analyst_node)
    graph.add_node("writer", writer_node)
    graph.add_node("safety", safety_node)
    graph.set_entry_point("planner")
    graph.add_edge("planner", "researcher")
    graph.add_edge("researcher", "analyst")
    graph.add_edge("analyst", "writer")
    graph.add_edge("writer", "safety")
    graph.add_edge("safety", END)
    return graph.compile()

pipeline = build_pipeline()

def run_pipeline(query: str) -> dict:
    print(f"\n{'='*50}")
    print(f"Pipeline starting for: {query}")
    print('='*50)
    initial_state = {
        "query": query,
        "planned_query": query,
        "research_result": "",
        "analyst_result": "",
        "final_report": "",
        "safety_result": {},
        "chart_files": []
    }
    result = pipeline.invoke(initial_state)
    return {
        "query": query,
        "research": result.get("research_result", ""),
        "financial": result.get("analyst_result", ""),
        "report": result.get("final_report", ""),
        "safety": result.get("safety_result", {}),
        "charts": result.get("chart_files", [])
    }
