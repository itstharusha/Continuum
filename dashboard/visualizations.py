# dashboard/visualizations.py
"""
Advanced interactive visualizations for Supply Chain Risk Sentinel dashboard.
Uses Plotly for responsive, theme-aware charts.
"""

import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots

logger = logging.getLogger(__name__)

# Color mappings
COUNTRY_COLORS = {
    "China": "#EF553B",           # Red
    "Taiwan": "#FF9600",          # Orange
    "Brazil": "#00CC96",          # Green
    "Sweden": "#AB63FA",          # Purple
    "Germany": "#636EFA",         # Blue
    "South Korea": "#FFA500",     # Orange
    "Japan": "#FF6B6B",           # Light Red
    "Vietnam": "#4ECDC4",         # Teal
    "India": "#95E1D3",           # Mint
}

RELEVANCE_COLORS = {
    "low": "#90EE90",             # Light Green
    "medium": "#FFD700",          # Gold
    "high": "#FF6B6B",            # Red
}


def build_supplier_bubble_chart(risk_result: Dict[str, Any], 
                                simulation_result: Dict[str, Any]) -> Optional[go.Figure]:
    """
    Create a bubble chart showing supplier impact.
    
    Args:
        risk_result: Dict with 'risks_detected' list
        simulation_result: Dict with 'scenarios' list
    
    Returns:
        Plotly Figure or None if no data
    """
    risks = risk_result.get("risks_detected", [])
    scenarios = simulation_result.get("scenarios", [])
    
    if not risks or not scenarios:
        return None
    
    # Create scenario lookup: node_id → scenario data
    scenario_map = {s["node_id"]: s for s in scenarios}
    
    # Prepare bubble chart data
    bubble_data = []
    for risk in risks:
        node_id = risk["node_id"]
        scenario = scenario_map.get(node_id)
        
        if not scenario:
            continue
        
        bubble_data.append({
            "supplier_name": risk["name"],
            "country": risk.get("country", "Unknown"),
            "material": risk.get("material", "Unknown"),
            "risk_score": risk["risk_score"],
            "estimated_delay_days": scenario["estimated_delay_days"],
            "service_level_impact": scenario["service_level_impact_pct"],
            "news_title": risk.get("news_title", "Unknown"),
        })
    
    if not bubble_data:
        return None
    
    df = pd.DataFrame(bubble_data)
    
    # Map countries to colors
    df["color"] = df["country"].map(COUNTRY_COLORS).fillna("#636EFA")
    
    # Create bubble chart
    fig = go.Figure()
    
    # Group by country for legend
    for country in df["country"].unique():
        country_data = df[df["country"] == country]
        color = COUNTRY_COLORS.get(country, "#636EFA")
        
        fig.add_trace(go.Scatter(
            x=country_data["estimated_delay_days"],
            y=country_data["service_level_impact"],
            mode="markers",
            name=country,
            marker=dict(
                size=country_data["risk_score"] * 50,  # Scale bubble size
                color=color,
                opacity=0.7,
                line=dict(width=2, color="white"),
            ),
            text=[
                f"<b>{row['supplier_name']}</b><br>" +
                f"Country: {row['country']}<br>" +
                f"Material: {row['material']}<br>" +
                f"Risk Score: {row['risk_score']:.2f}<br>" +
                f"Delay: {row['estimated_delay_days']:.1f} days<br>" +
                f"Impact: {row['service_level_impact']:.1f}%<br>" +
                f"News: {row['news_title'][:60]}..."
                for _, row in country_data.iterrows()
            ],
            hovertemplate="<extra></extra>%{text}",
        ))
    
    fig.update_layout(
        title="<b>Supplier Impact Bubble Chart</b>",
        xaxis_title="Estimated Delay Days",
        yaxis_title="Service Level Impact (%)",
        hovermode="closest",
        template="plotly_dark",
        height=500,
        showlegend=True,
        plot_bgcolor="rgba(20, 20, 20, 0.1)",
        paper_bgcolor="rgba(0, 0, 0, 0)",
        font=dict(size=12),
    )
    
    return fig


def build_news_timeline(ingestion_result: Dict[str, Any]) -> Optional[go.Figure]:
    """
    Create a horizontal timeline of news events.
    
    Args:
        ingestion_result: Dict with 'news_items' list
    
    Returns:
        Plotly Figure or None if no data
    """
    news_items = ingestion_result.get("news_items", [])
    
    if not news_items:
        return None
    
    # Prepare timeline data
    timeline_data = []
    for item in news_items:
        # Parse published timestamp
        try:
            pub_date = pd.to_datetime(item.get("published", datetime.now().isoformat()))
        except:
            pub_date = datetime.now()
        
        relevance = item.get("relevance_score", 0.5)
        
        # Map relevance to color
        if relevance >= 0.75:
            color = RELEVANCE_COLORS["high"]
            relevance_label = "High"
        elif relevance >= 0.5:
            color = RELEVANCE_COLORS["medium"]
            relevance_label = "Medium"
        else:
            color = RELEVANCE_COLORS["low"]
            relevance_label = "Low"
        
        timeline_data.append({
            "published": pub_date,
            "title": item.get("title", "Unknown"),
            "source": item.get("source", "Unknown"),
            "summary": item.get("summary", ""),
            "url": item.get("url", ""),
            "relevance_score": relevance,
            "color": color,
            "relevance_label": relevance_label,
        })
    
    if not timeline_data:
        return None
    
    df = pd.DataFrame(timeline_data)
    df = df.sort_values("published", ascending=True).tail(15)  # Last 15 items
    
    # Create timeline using scatter plot
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=df["published"],
        y=[1] * len(df),  # Dummy y-axis for horizontal timeline
        mode="markers+text",
        marker=dict(
            size=12,
            color=df["color"],
            line=dict(width=2, color="white"),
        ),
        text=df["title"].str[:40],
        textposition="top center",
        textfont=dict(size=9),
        hovertemplate=(
            "<b>%{customdata[0]}</b><br>" +
            "Published: %{x|%Y-%m-%d %H:%M}<br>" +
            "Source: %{customdata[1]}<br>" +
            "Relevance: %{customdata[2]}<br>" +
            "Summary: %{customdata[3][:100]}...<br>" +
            "<a href='%{customdata[4]}' target='_blank'>Read Full Article</a>" +
            "<extra></extra>"
        ),
        customdata=df[["title", "source", "relevance_label", "summary", "url"]].values,
    ))
    
    fig.update_layout(
        title="<b>Timeline of Recent News Events</b>",
        xaxis_title="Published Date",
        yaxis_visible=False,
        hovermode="closest",
        template="plotly_dark",
        height=400,
        showlegend=False,
        plot_bgcolor="rgba(20, 20, 20, 0.1)",
        paper_bgcolor="rgba(0, 0, 0, 0)",
        font=dict(size=11),
        margin=dict(t=80, b=60, l=60, r=60),
    )
    
    # Remove y-axis line
    fig.update_yaxes(showgrid=False)
    
    return fig


def build_scenario_comparison(simulation_result: Dict[str, Any]) -> Optional[go.Figure]:
    """
    Create a grouped bar chart comparing simulation scenarios.
    
    Args:
        simulation_result: Dict with 'scenarios' list
    
    Returns:
        Plotly Figure or None if no data
    """
    scenarios = simulation_result.get("scenarios", [])
    
    if not scenarios:
        return None
    
    # Prepare data
    scenario_data = []
    for scenario in scenarios:
        # Truncate news title for x-axis readability
        title = scenario.get("news_title", "Unknown")[:35]
        node_id = scenario.get("node_id", "Unknown")
        
        scenario_data.append({
            "scenario_label": f"{node_id}\n{title}",
            "delay_days": scenario.get("estimated_delay_days", 0),
            "impact_pct": scenario.get("service_level_impact_pct", 0),
            "disruption_type": scenario.get("disruption_type", "Unknown"),
            "affected_nodes": scenario.get("affected_nodes_count", 0),
            "severity": scenario.get("severity_used", 0),
        })
    
    df = pd.DataFrame(scenario_data)
    
    # Create grouped bar chart
    fig = go.Figure()
    
    # Delay bars (blue)
    fig.add_trace(go.Bar(
        name="Estimated Delay (days)",
        x=df["scenario_label"],
        y=df["delay_days"],
        marker=dict(color="#636EFA"),
        hovertemplate=(
            "<b>%{x}</b><br>" +
            "Delay: %{y:.1f} days<br>" +
            "<extra></extra>"
        ),
    ))
    
    # Impact bars (red)
    fig.add_trace(go.Bar(
        name="Service Impact (%)",
        x=df["scenario_label"],
        y=df["impact_pct"],
        marker=dict(color="#EF553B"),
        hovertemplate=(
            "<b>%{x}</b><br>" +
            "Impact: %{y:.1f}%<br>" +
            "<extra></extra>"
        ),
    ))
    
    # Enhance hover with full details
    for idx, row in df.iterrows():
        full_hover = (
            f"<b>{row['scenario_label']}</b><br>" +
            f"Delay: {row['delay_days']:.1f} days<br>" +
            f"Service Impact: {row['impact_pct']:.1f}%<br>" +
            f"Disruption Type: {row['disruption_type']}<br>" +
            f"Affected Nodes: {row['affected_nodes']}<br>" +
            f"Severity: {row['severity']:.2f}"
        )
    
    fig.update_layout(
        title="<b>Simulation Scenario Comparison</b>",
        xaxis_title="Scenario (Node + News)",
        yaxis_title="Value",
        barmode="group",
        hovermode="x unified",
        template="plotly_dark",
        height=500,
        showlegend=True,
        plot_bgcolor="rgba(20, 20, 20, 0.1)",
        paper_bgcolor="rgba(0, 0, 0, 0)",
        font=dict(size=11),
        xaxis=dict(tickangle=-45),
    )
    
    return fig
