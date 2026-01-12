# dashboard/history_utils.py
"""
History utilities for browsing and viewing past analysis cycles
"""

import streamlit as st
from core.persistence import persistence
from typing import Dict, Any, Optional


def get_history_list():
    """Get list of all saved analysis cycles."""
    return persistence.list_history(limit=100)


def load_and_display_cycle(filename: str):
    """Load and display a cycle's detailed results."""
    result = persistence.load_cycle(filename)
    
    if result["status"] != "success":
        st.error(f"Failed to load cycle: {result.get('error')}")
        return False
    
    data = result["data"]
    summary = result["summary"]
    
    # Display cycle metadata
    st.markdown(f"### Analysis Cycle: {filename}")
    st.caption(f"Timestamp: {data.get('timestamp', 'Unknown')}")
    
    # Summary metrics
    col1, col2, col3, col4, col5 = st.columns(5)
    col1.metric("Suppliers", summary["suppliers"])
    col2.metric("News Items", summary["news_items"])
    col3.metric("Risks Detected", summary["risks_detected"])
    col4.metric("Scenarios", summary["scenarios"])
    col5.metric("Decisions", summary["decisions"])
    
    st.markdown("---")
    
    # Tabbed view of results
    tab1, tab2, tab3, tab4 = st.tabs(["Risks", "Simulations", "Decisions", "News"])
    
    with tab1:
        st.subheader("Detected Risks")
        risks = data.get("risk_result", {}).get("risks_detected", [])
        if risks:
            import pandas as pd
            risks_df = pd.DataFrame(risks)
            # Select important columns for display
            display_cols = [col for col in ["node_id", "name", "country", "material", "risk_score", "news_title"] 
                          if col in risks_df.columns]
            st.dataframe(risks_df[display_cols], use_container_width=True)
            
            # Download button
            csv = risks_df.to_csv(index=False)
            st.download_button(
                label="Download Risks as CSV",
                data=csv,
                file_name=f"{filename}_risks.csv",
                mime="text/csv"
            )
        else:
            st.info("No risks detected in this cycle")
    
    with tab2:
        st.subheader("Simulation Scenarios")
        scenarios = data.get("simulation_result", {}).get("scenarios", [])
        if scenarios:
            import pandas as pd
            scenarios_df = pd.DataFrame(scenarios)
            # Select important columns
            display_cols = [col for col in ["node_id", "estimated_delay_days", "service_level_impact_pct", 
                                           "disruption_type", "affected_nodes_count", "severity_used"]
                          if col in scenarios_df.columns]
            st.dataframe(scenarios_df[display_cols], use_container_width=True)
            
            # Download button
            csv = scenarios_df.to_csv(index=False)
            st.download_button(
                label="Download Scenarios as CSV",
                data=csv,
                file_name=f"{filename}_scenarios.csv",
                mime="text/csv"
            )
        else:
            st.info("No scenarios simulated in this cycle")
    
    with tab3:
        st.subheader("Recommended Actions")
        decisions = data.get("decision_result", {}).get("recommended_actions", [])
        if decisions:
            import pandas as pd
            
            # Flatten the nested structure for display
            flat_decisions = []
            for decision in decisions:
                node_id = decision.get("node_id", "Unknown")
                node_name = decision.get("name", "Unknown")
                for action in decision.get("recommended_actions", []):
                    flat_decisions.append({
                        "node_id": node_id,
                        "node_name": node_name,
                        "action": action.get("action", ""),
                        "urgency": action.get("urgency", ""),
                        "confidence": action.get("estimated_confidence", 0),
                        "lead_time_days": action.get("lead_time_days", 0),
                    })
            
            if flat_decisions:
                decisions_df = pd.DataFrame(flat_decisions)
                st.dataframe(decisions_df, use_container_width=True)
                
                # Download button
                csv = decisions_df.to_csv(index=False)
                st.download_button(
                    label="Download Decisions as CSV",
                    data=csv,
                    file_name=f"{filename}_decisions.csv",
                    mime="text/csv"
                )
            else:
                st.info("No actions recommended in this cycle")
        else:
            st.info("No decisions made in this cycle")
    
    with tab4:
        st.subheader("News Items Used")
        news = data.get("ingestion_result", {}).get("news_items", [])
        if news:
            import pandas as pd
            news_df = pd.DataFrame(news)
            display_cols = [col for col in ["title", "source", "published", "relevance_score"]
                          if col in news_df.columns]
            st.dataframe(news_df[display_cols], use_container_width=True)
        else:
            st.info("No news items in this cycle")
    
    st.markdown("---")
    
    # Overall decision confidence
    decision_data = data.get("decision_result", {})
    if decision_data:
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Overall Confidence", f"{decision_data.get('overall_confidence', 0):.0%}")
        with col2:
            st.metric("Top Recommendation", decision_data.get("top_recommendation", "None").replace("_", " ").title())
    
    return True


def get_history_comparison_data(filename1: str, filename2: str) -> Optional[Dict[str, Any]]:
    """Get data to compare two analysis cycles."""
    result1 = persistence.load_cycle(filename1)
    result2 = persistence.load_cycle(filename2)
    
    if result1["status"] != "success" or result2["status"] != "success":
        return None
    
    return {
        "cycle1": result1["data"],
        "cycle2": result2["data"],
        "summary1": result1["summary"],
        "summary2": result2["summary"]
    }


def display_history_stats():
    """Display overall history statistics."""
    stats = persistence.get_summary_stats()
    
    if "error" in stats:
        st.error(f"Failed to get statistics: {stats['error']}")
        return
    
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Cycles", stats.get("total_cycles", 0))
    col2.metric("Total Storage", f"{stats.get('total_storage_mb', 0):.1f} MB")
    col3.metric("Avg Size", f"{stats.get('average_size_kb', 0):.1f} KB")
    col4.metric("Date Range", f"{stats.get('newest_cycle', 'N/A')[:10] if stats.get('newest_cycle') else 'N/A'}")
