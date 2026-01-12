# dashboard/app.py
import streamlit as st
from streamlit_extras.app_logo import add_logo
from core.memory import memory
from core.persistence import persistence
from dashboard.utils import run_full_analysis, get_interactive_graph_html
from dashboard.visualizations import (
    build_supplier_bubble_chart,
    build_news_timeline,
    build_scenario_comparison,
)
from dashboard.history_utils import (
    get_history_list,
    load_and_display_cycle,
    get_history_comparison_data,
    display_history_stats,
)

st.set_page_config(
    page_title="CONTINUUM",
    page_icon="ᯤ",
    layout="wide"
)

# Optional nice sidebar logo/title
add_logo("https://img.icons8.com/color/96/000000/supply-chain.png", height=80)  # or use local image

st.title("Continuum - Supply Chain Risk Sentinel")
st.markdown("Real-time risk monitoring & decision support system")

# Sidebar controls
st.sidebar.title("Controls")
if st.sidebar.button("Run New Analysis", type="primary"):
    run_full_analysis()

st.sidebar.markdown("---")
st.sidebar.info("Last analysis: " + (memory.get("decision_result") or {}).get("decision_timestamp", "Never"))

# Main tabs
tab1, tab2, tab3, tab4, tab5 = st.tabs(["Overview", "Supply Chain Graph", "Risks & Decisions", "Advanced Visuals", "History"])

with tab1:
    st.subheader("Latest Summary")
    decision = memory.get("decision_result", {})

    if decision:
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Max Risk Severity", f"{memory.get('risk_result', {}).get('max_severity', 0):.2f}")
        col2.metric("Worst Delay", f"{memory.get('simulation_result', {}).get('worst_case_delay_days', 0)} days")
        col3.metric("Decisions Made", decision.get("decision_count", 0))
        col4.metric("Top Action", decision.get("top_recommendation", "—"))

        st.markdown("**Overall Confidence**")
        confidence = min(decision.get("overall_confidence", 0.0), 1.0)
        st.progress(confidence)
    else:
        st.info("No analysis results yet. Click 'Run New Analysis' in sidebar.")

with tab2:
    st.subheader("Supply Chain Network")
    html = get_interactive_graph_html()
    st.components.v1.html(html, height=600, scrolling=True)

with tab3:
    st.subheader("Detected Risks & Recommendations")

    risks = memory.get("risk_result", {}).get("risks_detected", [])
    decisions = memory.get("decision_result", {}).get("recommended_actions", [])

    if not risks:
        st.info("No risks detected yet or no analysis has been run.")
        st.stop()

    # Create lookup: node_id → decision
    decision_map = {d["node_id"]: d for d in decisions}

    # Sort risks by severity DESCENDING
    sorted_risks = sorted(risks, key=lambda r: r["risk_score"], reverse=True)

    # Top 3 Actions Today card
    all_actions = []
    for decision in decisions:
        for act in decision.get("recommended_actions", []):
            act_copy = act.copy()
            act_copy["node_id"] = decision["node_id"]
            act_copy["node_name"] = decision.get("name", decision["node_id"])
            act_copy["material"] = decision.get("material", "Unknown")
            act_copy["country"] = decision.get("country", "Unknown")
            act_copy["risk_score"] = decision.get("risk_score", 0)
            act_copy["delay_days"] = decision.get("delay_days", 0)
            act_copy["service_impact"] = decision.get("service_impact_pct", 0)
            all_actions.append(act_copy)

    # Sort all actions by urgency DESC, then by confidence
    top_actions = sorted(
        all_actions,
        key=lambda a: (a["urgency"], a.get("estimated_confidence", 0)),
        reverse=True
    )[:3]

    if top_actions:
        st.markdown("### Top 3 Actions Today")
        cols = st.columns(3)
        for i, act in enumerate(top_actions):
            with cols[i]:
                urgency_color = "🔴" if act["urgency"] >= 4 else "🟠" if act["urgency"] >= 3 else "🟡"
                confidence_pct = min(max(act.get("estimated_confidence", 0), 0), 1.0) * 100
                
                st.metric(
                    label=f"{urgency_color} {act['action'].replace('_', ' ').title()}",
                    value=f"{confidence_pct:.0f}%",
                    delta=f"Urgency {act['urgency']}/5",
                )
                
                # Show additional context
                desc = act['description']
                affected = act['node_name']
                material_info = f" ({act.get('material', 'Unknown')})" if act.get('material') else ""
                country_info = f" - {act.get('country', '')}" if act.get('country') else ""
                
                st.caption(f"{desc}\nAffected: {affected}{material_info}{country_info}")
    else:
        st.info("No recommended actions available yet.")

    st.markdown("---")

    # Risks list – sorted by severity
    for risk in sorted_risks[:8]:
        node_id = risk["node_id"]
        decision = decision_map.get(node_id, {})

        severity = risk["risk_score"]
        severity_color = "🔴" if severity >= 0.9 else "🟠" if severity >= 0.6 else "🟡"

        with st.expander(f"{severity_color} {node_id} - {risk['name']} (Severity: {severity:.2f})"):
            # Risk summary
            col1, col2, col3 = st.columns(3)
            col1.metric("Risk Score", f"{severity:.2f}/1.0")
            col2.metric("Country", risk.get("country", "Unknown"))
            col3.metric("Material", risk.get("material", "Unknown"))
            
            st.markdown(f"**News Trigger:** {risk['news_title']}")
            
            # Simulation impact
            if decision:
                sim_col1, sim_col2, sim_col3 = st.columns(3)
                sim_col1.metric("Est. Delay", f"{decision.get('delay_days', 0):.1f} days")
                sim_col2.metric("Service Impact", f"{decision.get('service_impact_pct', 0):.1f}%")
                sim_col3.metric("Affected Nodes", decision.get("affected_nodes_count", 0))
            
            st.markdown("**Recommended Actions:**")
            if decision and decision.get("recommended_actions"):
                for act in decision["recommended_actions"]:
                    urgency = act["urgency"]
                    color = "#ff4d4d" if urgency >= 4 else "#ffa726" if urgency >= 3 else "#4caf50"
                    confidence = act.get("estimated_confidence", 0.0)
                    lead_time = act.get("lead_time_days", 0)
                    
                    # Ensure confidence is capped at 1.0
                    confidence = min(max(confidence, 0), 1.0)
                    
                    action_name = act['action'].replace('_', ' ').title()
                    lead_time_text = f" | Lead Time: {lead_time}d" if lead_time > 0 else ""
                    
                    st.markdown(
                        f"""
                        <div style="
                            padding: 12px;
                            margin: 10px 0;
                            border-left: 6px solid {color};
                            background-color: #f0f2f6;
                            border-radius: 6px;
                            color: #111111 !important;
                            font-size: 15px;
                            line-height: 1.45;
                        ">
                            <strong>{action_name}</strong><br>
                            <span style="color: #555;">Urgency: {urgency}/5 | Confidence: {confidence:.0%}{lead_time_text}</span><br>
                            <small>{act['description']}</small>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )
            else:
                st.warning("No decision recommendations generated for this risk yet.")

with tab4:
    st.subheader("Advanced Analytics & Visualizations")
    st.markdown("Interactive visualizations for supply chain impact analysis")
    
    # Get data from memory
    risk_result = memory.get("risk_result", {})
    simulation_result = memory.get("simulation_result", {})
    ingestion_result = memory.get("ingestion_result", {})
    
    if not risk_result or not simulation_result:
        st.info("No analysis results available. Please run 'Run New Analysis' to generate visualizations.")
        st.stop()
    
    # Visualization 1: Supplier Impact Bubble Chart
    st.markdown("#### Supplier Impact Bubble Chart")
    st.markdown(
        "Each bubble represents a supplier. "
        "Size = risk score, Color = country, Position = delay vs impact"
    )
    
    bubble_fig = build_supplier_bubble_chart(risk_result, simulation_result)
    if bubble_fig:
        st.plotly_chart(bubble_fig, use_container_width=True)
    else:
        st.warning("No data available for bubble chart. Ensure analysis has detected risks and simulations.")
    
    st.markdown("---")
    
    # Visualization 2: Timeline of News Events
    st.markdown("#### Timeline of Recent News Events")
    st.markdown(
        "Chronological timeline of news items. "
        "Color indicates relevance: Green (low) → Red (high)"
    )
    
    timeline_fig = build_news_timeline(ingestion_result)
    if timeline_fig:
        st.plotly_chart(timeline_fig, use_container_width=True)
    else:
        st.info("No news items available. Check if ingestion agent has fetched recent news.")
    
    st.markdown("---")
    
    # Visualization 3: Scenario Comparison Bar Groups
    st.markdown("#### Simulation Scenario Comparison")
    st.markdown(
        "Grouped bars comparing delay days (blue) vs service impact % (red) "
        "across simulation scenarios"
    )
    
    scenario_fig = build_scenario_comparison(simulation_result)
    if scenario_fig:
        st.plotly_chart(scenario_fig, use_container_width=True)
    else:
        st.warning("No scenarios available. Ensure simulation agent has run scenarios.")
    
    st.markdown("---")
    st.caption(
        "💡 **Tip:** Hover over charts for detailed information. "
        "Use browser zoom for better readability on smaller screens." )

with tab5:
    st.subheader("Analysis History & Archive")
    st.markdown("Browse, compare, and export past analysis cycles")
    
    # History statistics
    st.markdown("### History Statistics")
    display_history_stats()
    
    st.markdown("---")
    
    # History browser
    st.markdown("### Browse Past Cycles")
    
    history = get_history_list()
    
    if not history:
        st.info("No analysis cycles saved yet. Run 'Run New Analysis' to create one.")
    else:
        # Create list of cycles for selection
        cycle_options = {
            f"{entry['timestamp'][:19]} | {entry['file_size_bytes']:,} bytes": entry['filename']
            for entry in history
        }
        
        selected_display = st.selectbox(
            "Select a cycle to view:",
            options=list(cycle_options.keys()),
            index=0
        )
        
        if selected_display:
            selected_filename = cycle_options[selected_display]
            
            # Display selected cycle
            st.markdown("---")
            load_and_display_cycle(selected_filename)
            
            # Action buttons
            col1, col2, col3 = st.columns(3)
            
            with col1:
                if st.button("Delete This Cycle", key=f"delete_{selected_filename}"):
                    result = persistence.delete_cycle(selected_filename)
                    if result["status"] == "success":
                        st.success("Cycle deleted!")
                        st.rerun()
                    else:
                        st.error(f"Failed to delete: {result.get('error')}")
            
            with col2:
                # Export as CSV option
                export_options = ["Risks", "Scenarios", "Decisions", "All"]
                export_choice = st.selectbox(
                    "Export as CSV:",
                    options=export_options,
                    key=f"export_{selected_filename}"
                )
                
                if export_choice and st.button("Generate Export", key=f"export_btn_{selected_filename}"):
                    export_result = persistence.export_cycle_csv(selected_filename)
                    if export_result["status"] == "success":
                        st.success(f"Exported {export_result['count']} files")
                        for label, path in export_result["exported_files"]:
                            st.caption(f"📄 {label}: {path}")
                    else:
                        st.error(f"Export failed: {export_result.get('error')}")
            
            with col3:
                st.caption("More options in development")
        
        st.markdown("---")
        
        # Comparison feature
        st.markdown("### Compare Two Cycles")
        
        if len(history) >= 2:
            col1, col2 = st.columns(2)
            
            with col1:
                cycle1_display = st.selectbox(
                    "First cycle:",
                    options=list(cycle_options.keys()),
                    index=0,
                    key="compare_1"
                )
                cycle1_filename = cycle_options[cycle1_display]
            
            with col2:
                cycle2_display = st.selectbox(
                    "Second cycle:",
                    options=list(cycle_options.keys()),
                    index=1 if len(history) > 1 else 0,
                    key="compare_2"
                )
                cycle2_filename = cycle_options[cycle2_display]
            
            if st.button("Compare Cycles"):
                comparison = get_history_comparison_data(cycle1_filename, cycle2_filename)
                
                if comparison:
                    st.markdown("#### Comparison Results")
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.markdown("**Cycle 1**")
                        st.metric("Risks", comparison["summary1"]["risks_detected"])
                        st.metric("Scenarios", comparison["summary1"]["scenarios"])
                        st.metric("Decisions", comparison["summary1"]["decisions"])
                    
                    with col2:
                        st.markdown("**Cycle 2**")
                        st.metric("Risks", comparison["summary2"]["risks_detected"])
                        st.metric("Scenarios", comparison["summary2"]["scenarios"])
                        st.metric("Decisions", comparison["summary2"]["decisions"])
                    
                    # Risk comparison
                    st.markdown("#### Risk Changes")
                    risks1 = set(r.get("node_id") for r in comparison["cycle1"].get("risk_result", {}).get("risks_detected", []))
                    risks2 = set(r.get("node_id") for r in comparison["cycle2"].get("risk_result", {}).get("risks_detected", []))
                    
                    new_risks = risks2 - risks1
                    resolved_risks = risks1 - risks2
                    
                    if new_risks:
                        st.warning(f"New risks: {', '.join(sorted(new_risks))}")
                    if resolved_risks:
                        st.success(f"Resolved: {', '.join(sorted(resolved_risks))}")
                    if not new_risks and not resolved_risks:
                        st.info("No changes in risk detection")
                else:
                    st.error("Failed to load comparison data")
        else:
            st.info("Need at least 2 cycles to compare")