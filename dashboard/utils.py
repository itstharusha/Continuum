# dashboard/utils.py
import streamlit as st
import networkx as nx
from pyvis.network import Network
import os
from core.memory import memory
from agents.ingestion_agent import IngestionAgent
from agents.graph_agent import GraphAgent
from agents.risk_agent import RiskAgent
from agents.simulation_agent import SimulationAgent
from agents.decision_agent import DecisionAgent

def run_full_analysis():
    """Trigger complete analysis cycle and store results in memory"""
    with st.spinner("Running full analysis cycle..."):
        ing = IngestionAgent()
        ingest = ing.run()

        graph_agent = GraphAgent()
        graph_agent.run(ingest["suppliers"])

        risk = RiskAgent()
        risk.run(ingest["news_items"], memory.get("graph_result"))

        sim = SimulationAgent()
        sim.run(memory.get("graph_result"), memory.get("risk_result"))

        decision = DecisionAgent()
        decision.run(memory.get("risk_result"), memory.get("simulation_result"))

    st.success("Analysis complete!")
    return memory.get("decision_result")

def get_interactive_graph_html():
    """Convert NetworkX graph to interactive PyVis HTML"""
    G = memory.get("supply_chain_graph")
    if G is None or G.number_of_nodes() == 0:
        return "<p>No graph available. Run analysis first.</p>"

    net = Network(
        height="550px",
        width="100%",
        directed=True,
        notebook=False,
        bgcolor="#222222",
        font_color="white"
    )

    net.from_nx(G)

    # Customize a bit
    for node in net.nodes:
        node["title"] = f"{node.get('name', node['id'])}\nType: {node.get('type', '?')}"
        if node.get("type") == "supplier":
            node["color"] = "#4CAF50"
        elif node.get("type") == "factory":
            node["color"] = "#2196F3"
        elif node.get("type") == "warehouse":
            node["color"] = "#FF9800"
        elif node.get("type") == "customer":
            node["color"] = "#9C27B0"

    # Save to temp file
    html_path = "temp_graph.html"
    net.save_graph(html_path)

    with open(html_path, "r", encoding="utf-8") as f:
        html_content = f.read()

    os.remove(html_path)  # cleanup
    return html_content