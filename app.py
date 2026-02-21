"""
SF CHAI - Streamlit + eChart + AI
Main application file.

Phase 1: Skeleton + UI basics
Phase 2: Data loading & Vision analysis

- Streamlit page config, layout (sidebar + main)
- Sidebar: AI provider selector, key inputs
- Main: CSV uploader, PNG uploader, "Generate" button
- CSV data loading and preview
- Vision analysis with Bedrock/OpenAI
"""

import streamlit as st
from pathlib import Path
from datetime import datetime
import uuid
import pandas as pd
import json

# Import database module
from database import init_database, list_sessions, load_session, save_session, delete_session

# Import sample data module
from samples import get_sample_data, list_samples

# Import AI client module
from ai_client import (
    get_ai_client, 
    encode_image_to_base64, 
    analyze_chart_image,
    generate_chart_json,
    generate_summary,
    process_chat_message,
    VISION_ANALYSIS_PROMPT
)

from plotly_chart_generator import generate_plotly_chart, convert_plotly_to_json

# Import export manager
from export_manager import export_to_html, export_to_python

# For ECharts rendering (keeping for backward compatibility)
from streamlit_echarts import st_echarts

# ============================================================================
# Page Configuration
# ============================================================================

st.set_page_config(
    page_title="SF CHAI - Streamlit + eChart + AI",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ============================================================================
# Session State Initialization
# ============================================================================

def init_session_state():
    """Initialize all session state variables."""
    defaults = {
        # Current session info
        "session_id": str(uuid.uuid4()),
        "session_name": "New Session",
        
        # AI Provider
        "ai_provider": "bedrock",  # "bedrock" or "openai"
        
        # Conversation state (NEW)
        "conversation_phase": "idle",  # idle, upload, analysis, review, generation, refinement
        "chat_history": [],  # List of {role, content, metadata}
        
        # File uploads (NEW - for chatbot workflow)
        "uploaded_csv": None,  # pandas DataFrame
        "uploaded_csv_filename": None,
        "uploaded_png": None,  # PIL Image
        "uploaded_png_filename": None,
        "last_csv_upload": None,  # Track last upload to prevent duplicates
        "last_png_upload": None,
        
        # OLD file uploads (keep for backward compatibility)
        "csv_file": None,
        "csv_filename": None,
        "csv_data": None,  # pandas DataFrame
        
        "png_file": None,
        "png_filename": None,
        "png_image": None,  # PIL Image
        
        # Analysis results
        "current_proposal": None,  # Proposal JSON (NEW)
        "chart_analysis": None,  # Vision LLM output
        "chart_json": None,  # ECharts option JSON
        "summary_text": None,  # Executive summary
        
        # UI state
        "theme": "dark",
        "ready_to_generate": False,
    }
    
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


# ============================================================================
# Sidebar - Session Management & AI Provider
# ============================================================================

def render_sidebar():
    """Render the sidebar with session management and AI provider selection."""
    st.sidebar.title("📊 SF CHAI")
    st.sidebar.markdown("---")
    
    # AI Provider Selector
    st.sidebar.subheader("🤖 AI Provider")
    ai_provider = st.sidebar.radio(
        "Select AI Backend",
        ["AWS Bedrock (Claude)", "OpenAI (GPT-4o)"],
        index=0 if st.session_state.ai_provider == "bedrock" else 1,
        key="ai_provider_radio",
        help="AWS Bedrock uses Claude. OpenAI uses GPT-4o."
    )
    st.session_state.ai_provider = "bedrock" if "Bedrock" in ai_provider else "openai"
    
    # API Key status
    st.sidebar.markdown("**API Configuration:**")
    if st.session_state.ai_provider == "bedrock":
        # Check for AWS credentials
        import os
        aws_access = os.environ.get("AWS_ACCESS_KEY_ID", "")
        aws_secret = os.environ.get("AWS_SECRET_ACCESS_KEY", "")
        
        if aws_access and aws_secret:
            st.sidebar.success("✅ AWS credentials configured")
        else:
            st.sidebar.warning("⚠️ AWS credentials not found in .env")
            st.sidebar.info("Using OpenAI instead...")
            st.session_state.ai_provider = "openai"
    else:
        import os
        openai_key = os.environ.get("OPENAI_API_KEY", "")
        if openai_key:
            st.sidebar.success("✅ OpenAI API key configured")
        else:
            st.sidebar.warning("⚠️ OpenAI API key not found in .env")
    
    st.sidebar.markdown("---")
    
    # Session Management
    st.sidebar.subheader("💾 Sessions")
    
    # Save current session button
    can_save = (
        st.session_state.csv_data is not None or 
        st.session_state.chart_json is not None
    )
    
    if st.sidebar.button("💾 Save Session", key="save_session_btn", disabled=not can_save):
        # Save the current session
        save_session(
            session_id=st.session_state.session_id,
            name=st.session_state.session_name,
            csv_file=st.session_state.csv_file,
            png_file=st.session_state.png_file,
            csv_data=st.session_state.csv_data,
            chart_json=st.session_state.chart_json,
            summary_text=st.session_state.summary_text,
            chat_history=st.session_state.chat_history
        )
        st.sidebar.success("Session saved!")
        st.rerun()
    
    # List saved sessions
    sessions = list_sessions()
    
    if sessions:
        session_options = {s['name']: s['id'] for s in sessions}
        selected_session_name = st.sidebar.selectbox(
            "Load Session",
            options=list(session_options.keys()),
            key="session_selector"
        )
        
        if selected_session_name:
            selected_session_id = session_options[selected_session_name]
            
            col1, col2 = st.sidebar.columns(2)
            with col1:
                if st.button("📂 Load", key="load_session_btn"):
                    # Load the selected session
                    session_data = load_session(selected_session_id)
                    if session_data:
                        st.session_state.session_id = selected_session_id
                        st.session_state.session_name = session_data.get('name', 'Loaded Session')
                        st.session_state.chart_json = session_data.get('chart_json')
                        st.session_state.summary_text = session_data.get('summary_text')
                        st.session_state.chat_history = session_data.get('chat_history', [])
                        
                        # Load CSV if available
                        if session_data.get('csv_path') and session_data['csv_path'].exists():
                            st.session_state.csv_data = pd.read_csv(session_data['csv_path'])
                            st.session_state.csv_filename = session_data.get('csv_filename')
                        
                        # Load PNG if available
                        if session_data.get('png_path') and session_data['png_path'].exists():
                            from PIL import Image
                            st.session_state.png_image = Image.open(session_data['png_path'])
                            st.session_state.png_filename = session_data.get('png_filename')
                        
                        st.sidebar.success("Session loaded!")
                        st.rerun()
            
            with col2:
                if st.button("🗑️ Delete", key="delete_session_btn"):
                    if delete_session(selected_session_id):
                        st.sidebar.success("Session deleted!")
                        st.rerun()
    else:
        st.sidebar.info("No saved sessions yet")
    
    # Current session name
    st.sidebar.markdown("---")
    st.sidebar.subheader("📝 Current Session")
    session_name = st.sidebar.text_input(
        "Session Name",
        value=st.session_state.session_name,
        key="session_name_input"
    )
    st.session_state.session_name = session_name
    
    # Theme toggle
    st.sidebar.markdown("---")
    st.sidebar.subheader("🎨 Theme")
    theme = st.sidebar.toggle(
        "Dark Mode",
        value=st.session_state.theme == "dark",
        key="theme_toggle"
    )
    st.session_state.theme = "dark" if theme else "light"
    
    st.sidebar.markdown("---")
    st.sidebar.caption(f"Session ID: `{st.session_state['session_id'][:8]}...`")


# ============================================================================
# Floating Chat Interface
# ============================================================================

def run_chat(user_message: str) -> dict:
    """
    Process a chat message and return response.
    
    Args:
        user_message: User's chat message
        
    Returns:
        Response dict with action and response/changes
    """
    try:
        # Get AI client
        client = get_ai_client(st.session_state.ai_provider)
        
        # Process message
        response = process_chat_message(
            client,
            user_message,
            st.session_state.csv_data,
            st.session_state.chart_analysis,
            st.session_state.chart_json,
            st.session_state.summary_text
        )
        
        return response
        
    except Exception as e:
        return {
            "action": "text",
            "response": f"Error processing message: {str(e)}"
        }


def apply_chart_modifications(chart_json: dict, changes: dict) -> dict:
    """
    Apply modifications to chart JSON configuration.
    
    Args:
        chart_json: Current ECharts configuration
        changes: Changes to apply
        
    Returns:
        Updated chart JSON
    """
    import copy
    updated_chart = copy.deepcopy(chart_json)
    
    # Deep merge changes into chart
    def deep_merge(target, source):
        for key, value in source.items():
            if key in target and isinstance(target[key], dict) and isinstance(value, dict):
                # Recursively merge dictionaries
                deep_merge(target[key], value)
            elif key in target and isinstance(target[key], list) and isinstance(value, list):
                # For arrays, handle different merge strategies
                if len(value) > 0 and isinstance(value[0], dict):
                    # If source array has dicts, merge each element
                    for i, item in enumerate(value):
                        if i < len(target[key]):
                            if isinstance(item, dict) and isinstance(target[key][i], dict):
                                deep_merge(target[key][i], item)
                            else:
                                target[key][i] = item
                        else:
                            target[key].append(item)
                else:
                    # For simple arrays, replace entirely
                    target[key] = value
            else:
                # For simple values or new keys, just set the value
                target[key] = value
    
    deep_merge(updated_chart, changes)
    return updated_chart


def render_floating_chat():
    """Render floating chatbot overlay."""
    # Initialize chat open state
    if "chat_open" not in st.session_state:
        st.session_state.chat_open = False
    
    # CSS for floating button - bigger, more visible, right bottom
    st.markdown("""
    <style>
    /* Target the floating chat button specifically */
    div[data-testid="stVerticalBlock"] > div:has(button[key="floating_chat_btn"]) {
        position: fixed !important;
        bottom: 30px !important;
        right: 30px !important;
        z-index: 9999 !important;
    }
    
    /* Style the button itself */
    button[key="floating_chat_btn"] {
        width: 80px !important;
        height: 80px !important;
        min-width: 80px !important;
        min-height: 80px !important;
        border-radius: 50% !important;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        color: white !important;
        border: 3px solid rgba(255, 255, 255, 0.3) !important;
        box-shadow: 0 8px 24px rgba(102, 126, 234, 0.6), 0 4px 8px rgba(0,0,0,0.3) !important;
        font-size: 40px !important;
        padding: 0 !important;
        cursor: pointer !important;
        transition: all 0.3s ease !important;
        position: relative !important;
    }
    
    button[key="floating_chat_btn"]:hover {
        transform: scale(1.15) translateY(-3px) !important;
        box-shadow: 0 12px 32px rgba(102, 126, 234, 0.7), 0 6px 12px rgba(0,0,0,0.4) !important;
        background: linear-gradient(135deg, #7688f0 0%, #8655b2 100%) !important;
        border-color: rgba(255, 255, 255, 0.5) !important;
    }
    
    button[key="floating_chat_btn"]:active {
        transform: scale(1.05) translateY(0px) !important;
        box-shadow: 0 4px 16px rgba(102, 126, 234, 0.5) !important;
    }
    
    /* Add a subtle pulse animation to make it more noticeable */
    @keyframes pulse {
        0%, 100% {
            box-shadow: 0 8px 24px rgba(102, 126, 234, 0.6), 0 4px 8px rgba(0,0,0,0.3);
        }
        50% {
            box-shadow: 0 8px 32px rgba(102, 126, 234, 0.8), 0 4px 12px rgba(0,0,0,0.4);
        }
    }
    
    button[key="floating_chat_btn"] {
        animation: pulse 2s ease-in-out infinite !important;
    }
    
    /* Chat panel styling */
    div[data-testid="stPopover"] {
        position: fixed !important;
        bottom: 130px !important;
        right: 30px !important;
        width: 450px !important;
        max-height: 650px !important;
        box-shadow: 0 8px 32px rgba(0,0,0,0.15) !important;
        border-radius: 12px !important;
        z-index: 9998 !important;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Render floating button in a container that will be positioned
    with st.container():
        if st.button("🤖", key="floating_chat_btn", help="Open AI Assistant", type="primary"):
            st.session_state.chat_open = not st.session_state.chat_open
            st.rerun()
    
    # Render chat panel if open
    if st.session_state.chat_open:
        with st.popover("🤖 AI Assistant", use_container_width=False):
            # Check if we have data
            if st.session_state.csv_data is None:
                st.info("📊 Upload CSV to start")
            else:
                # Compact help
                with st.expander("ℹ️ Help", expanded=False):
                    st.caption("""
                    - "Add vertical line at 2020"
                    - "Change first series to blue"
                    - "Add horizontal line at 2.0"
                    """)
                
                # Chat history (compact - last 5 messages)
                for message in st.session_state.chat_history[-5:]:
                    with st.chat_message(message["role"]):
                        st.caption(message["content"])
                
                # Chat input
                user_input = st.chat_input("Ask me...", key="floating_chat_input")
                
                if user_input:
                    st.session_state.chat_history.append({"role": "user", "content": user_input})
                    response = run_chat(user_input)
                    
                    if response.get("action") == "text":
                        st.session_state.chat_history.append({"role": "assistant", "content": response.get("response", "")})
                    elif response.get("action") == "modify_chart":
                        if st.session_state.chart_json:
                            st.session_state.chart_json = apply_chart_modifications(st.session_state.chart_json, response.get("changes", {}))
                            st.session_state.chat_history.append({"role": "assistant", "content": "✅ Chart updated!"})
                    elif response.get("action") == "regenerate_summary":
                        new_summary = run_summary_generation()
                        if new_summary:
                            st.session_state.summary_text = new_summary
                            st.session_state.chat_history.append({"role": "assistant", "content": "✅ Summary regenerated!"})
                    st.rerun()
                
                if st.button("Clear", key="clear_chat"):
                    st.session_state.chat_history = []
                    st.rerun()


# ============================================================================
# CSV Data Loading & Preview
# ============================================================================

def load_csv_data(csv_file) -> pd.DataFrame:
    """
    Load CSV file into a pandas DataFrame.
    
    Args:
        csv_file: Streamlit uploaded file
        
    Returns:
        pandas DataFrame
    """
    try:
        df = pd.read_csv(csv_file)
        return df
    except Exception as e:
        st.error(f"Error loading CSV: {e}")
        return None


def render_data_preview(df: pd.DataFrame):
    """
    Render data preview with stats.
    
    Args:
        df: pandas DataFrame
    """
    if df is None:
        return
    
    # Data info
    st.markdown("#### 📊 Data Overview")
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Rows", df.shape[0])
    with col2:
        st.metric("Columns", df.shape[1])
    with col3:
        st.metric("Numeric Cols", len(df.select_dtypes(include=['number']).columns))
    with col4:
        st.metric("Text Cols", len(df.select_dtypes(include=['object']).columns))
    
    # Column details
    st.markdown("#### 📋 Column Details")
    col_info = []
    for col in df.columns:
        dtype = str(df[col].dtype)
        nulls = df[col].isnull().sum()
        unique = df[col].nunique()
        col_info.append({
            "Column": col,
            "Type": dtype,
            "Nulls": nulls,
            "Unique": unique,
            "Sample": str(df[col].iloc[0]) if len(df) > 0 else ""
        })
    
    col_df = pd.DataFrame(col_info)
    st.dataframe(col_df, width='stretch', hide_index=True)
    
    # Data preview
    with st.expander("📄 View Raw Data (First 10 rows)"):
        st.dataframe(df.head(10), width='stretch')


# ============================================================================
# Vision Analysis
# ============================================================================

def run_vision_analysis():
    """
    Run vision analysis on the uploaded PNG using AI.
    
    Returns:
        Chart analysis dict or None on error
    """
    try:
        # Get AI client
        client = get_ai_client(st.session_state.ai_provider)
        
        # Encode image to base64
        image_base64 = encode_image_to_base64(st.session_state.png_image)
        
        # Run vision analysis
        with st.spinner("🤖 Analyzing reference chart..."):
            analysis = analyze_chart_image(client, image_base64)
        
        # Check if there's an error
        if isinstance(analysis, dict) and "error" in analysis:
            st.warning(f"⚠️ {analysis.get('error')}")
            
            # Check if there's a fallback analysis
            if "fallback_analysis" in analysis:
                st.info("📊 Using fallback analysis to generate a basic chart. You can customize it using the chatbot.")
                return analysis["fallback_analysis"]
            
            return None
        
        return analysis
        
    except Exception as e:
        st.error(f"Vision analysis failed: {e}")
        return None


# ============================================================================
# Chart Generation
# ============================================================================

def validate_chart_json(chart_json: dict, csv_data: pd.DataFrame, analysis: dict) -> list:
    """
    Validate that the generated chart matches requirements.
    
    Args:
        chart_json: Generated ECharts configuration
        csv_data: Source CSV data
        analysis: Vision analysis results
        
    Returns:
        List of validation issues (empty if all good)
    """
    issues = []
    
    # Pivot data if needed
    if 'key' in csv_data.columns and 'value' in csv_data.columns:
        csv_data = csv_data.pivot(index='date', columns='key', values='value').reset_index()
    
    # Check series count
    expected_series_count = len(csv_data.columns) - 1  # Minus date column
    actual_series_count = len(chart_json.get("series", []))
    if actual_series_count != expected_series_count:
        issues.append(f"Expected {expected_series_count} series but got {actual_series_count}")
    
    # Check for annotations
    if analysis and isinstance(analysis, dict):
        annotations = analysis.get("annotations", {})
        if isinstance(annotations, dict):
            h_lines = annotations.get("horizontal_lines", [])
            if h_lines and chart_json.get("series"):
                # Check if first series has markLine
                first_series = chart_json["series"][0]
                if "markLine" not in first_series:
                    issues.append(f"Reference has {len(h_lines)} horizontal annotation(s) but markLine not added")
    
    # Check legend type
    if analysis and isinstance(analysis, dict):
        legend_info = analysis.get("legend", {})
        if isinstance(legend_info, dict):
            legend_type = legend_info.get("type")
            if legend_type == "inline":
                # Should have endLabel on series, not legend component
                if "legend" in chart_json:
                    issues.append("Reference uses inline labels but legend component was added")
                if chart_json.get("series"):
                    for i, series in enumerate(chart_json["series"]):
                        if "endLabel" not in series or not series["endLabel"].get("show"):
                            issues.append(f"Series {i} missing endLabel (reference uses inline labels)")
            elif legend_type == "box":
                # Should have legend component, not endLabel
                if "legend" not in chart_json:
                    issues.append("Reference uses legend box but legend component not added")
    
    # Check colors
    if analysis and isinstance(analysis, dict):
        ref_colors = analysis.get("colors", [])
        if ref_colors and chart_json.get("series"):
            for i, series in enumerate(chart_json["series"]):
                if i < len(ref_colors):
                    series_color = series.get("itemStyle", {}).get("color")
                    if series_color != ref_colors[i]:
                        issues.append(f"Series {i} color mismatch: expected {ref_colors[i]}, got {series_color}")
    
    return issues


def get_csv_info(df: pd.DataFrame) -> str:
    """
    Get a string summary of CSV data for the AI prompt.
    
    Args:
        df: pandas DataFrame
        
    Returns:
        String with CSV column info
    """
    # Check if data is in long format (date, key, value)
    if 'key' in df.columns and 'value' in df.columns:
        # Pivot to wide format
        df_wide = df.pivot(index='date', columns='key', values='value').reset_index()
        info = f"CSV (pivoted from long format) has {df_wide.shape[0]} rows and {df_wide.shape[1]} columns:\n"
        
        for i, col in enumerate(df_wide.columns):
            dtype = str(df_wide[col].dtype)
            info += f"- Column {i}: '{col}' (type: {dtype})"
            if pd.api.types.is_numeric_dtype(df_wide[col]):
                info += f", min={df_wide[col].min():.2f}, max={df_wide[col].max():.2f}"
            else:
                info += f", unique values: {df_wide[col].nunique()}"
            info += "\n"
        
        info += f"\nFirst 5 rows:\n{df_wide.head(5).to_string()}\n"
        return info
    
    # Standard wide format
    info = f"CSV has {df.shape[0]} rows and {df.shape[1]} columns:\n"
    
    for i, col in enumerate(df.columns):
        dtype = str(df[col].dtype)
        info += f"- Column {i}: '{col}' (type: {dtype})"
        if pd.api.types.is_numeric_dtype(df[col]):
            info += f", min={df[col].min():.2f}, max={df[col].max():.2f}"
        else:
            info += f", unique values: {df[col].nunique()}"
        info += "\n"
    
    info += f"\nFirst 5 rows:\n{df.head(5).to_string()}\n"
    return info


def run_chart_generation():
    """
    Generate ECharts JSON from vision analysis and CSV data.
    
    Returns:
        ECharts option JSON or mismatch object
    """
    try:
        # Use AI generation for all charts
        client = get_ai_client(st.session_state.ai_provider)
        csv_info = get_csv_info(st.session_state.csv_data)
        
        with st.spinner("🎨 Generating chart..."):
            chart_json = generate_chart_json(
                client, 
                st.session_state.chart_analysis, 
                st.session_state.csv_data,
                csv_info
            )
        
        # Validate the generated chart
        if chart_json and not chart_json.get("mismatch"):
            validation_issues = validate_chart_json(
                chart_json,
                st.session_state.csv_data,
                st.session_state.chart_analysis
            )
            
            if validation_issues:
                st.warning("⚠️ Chart generated but has issues:")
                for issue in validation_issues:
                    st.warning(f"  • {issue}")
                st.info("💡 You can fix these issues using the chatbot")
        
        return chart_json
        
    except Exception as e:
        st.error(f"Chart generation failed: {e}")
        import traceback
        st.code(traceback.format_exc())
        return {"mismatch": True, "reason": str(e)}


def render_chart(chart_json, key_suffix=""):
    """
    Render chart (supports both Plotly and ECharts).
    
    Args:
        chart_json: Chart configuration dict
        key_suffix: Unique suffix for the chart key
    """
    if chart_json is None:
        st.error("Chart data is None")
        return
    
    # Check chart type
    chart_type = chart_json.get("type", "echarts")
    
    if chart_type == "plotly":
        # Render Plotly chart
        st.markdown("### 📈 Generated Chart")
        try:
            import plotly.graph_objects as go
            fig = go.Figure(chart_json["figure"])
            st.plotly_chart(fig, use_container_width=True, key=f"plotly_{key_suffix}")
        except Exception as e:
            st.error(f"Error rendering Plotly chart: {e}")
            import traceback
            st.code(traceback.format_exc())
        return
    
    # Original ECharts rendering
    chart_options = chart_json.get("options", chart_json)
    # Original ECharts rendering
    chart_options = chart_json.get("options", chart_json)
    
    if chart_options is None:
        st.error("Chart data is None")
        return
    
    # Check for mismatch (ECharts)
    if isinstance(chart_options, dict) and chart_options.get("mismatch"):
        st.error("⚠️ Chart Mapping Issue Detected")
        st.markdown(f"**Reason:** {chart_options.get('reason', 'Unknown issue')}")
        
        # Show clarifying questions
        questions = chart_options.get("clarifying_questions", [])
        if questions:
            st.markdown("**Clarifying Questions:**")
            for q in questions:
                st.markdown(f"- {q}")
        
        return
    
    # Render the chart
    st.markdown("### 📈 Generated Chart")
    
    try:
        # Set height and enable toolbox
        options = chart_options.copy()
        
        # Ensure toolbox has saveAsImage
        if "toolbox" not in options:
            options["toolbox"] = {
                "feature": {
                    "saveAsImage": {"title": "Save as PNG"}
                }
            }
        
        # FIX 1: Move vertical annotation from xAxis to series[0].markLine
        if "xAxis" in options and "markLine" in options["xAxis"]:
            vertical_marks = options["xAxis"].pop("markLine", {}).get("data", [])
            if vertical_marks and "series" in options and len(options["series"]) > 0:
                # Add to first series markLine
                if "markLine" not in options["series"][0]:
                    options["series"][0]["markLine"] = {"data": []}
                # Append vertical marks
                for mark in vertical_marks:
                    options["series"][0]["markLine"]["data"].append(mark)
        
        # FIX 2: Ensure smooth curves if reference had them
        if "series" in options:
            for series in options["series"]:
                if series.get("type") == "line":
                    series["smooth"] = True
                    series["smoothMonotone"] = "x"
        
        # FIX 3: Increase right margin for endLabel visibility
        if "grid" in options:
            options["grid"]["right"] = "25%"  # Increase from 22% to 25%
        
        # FIX 4: Enhance endLabel configuration
        if "series" in options:
            for series in options["series"]:
                if "endLabel" in series and series["endLabel"].get("show"):
                    series["endLabel"]["distance"] = 10
                    series["endLabel"]["fontSize"] = 12
                    series["endLabel"]["fontWeight"] = "bold"
        
        # Check if series has data
        if "series" in options and len(options["series"]) > 0:
            # Render with st_echarts - use light theme to match reference
            # Add unique key to avoid duplicate element ID error
            chart_key = f"chart_{key_suffix}" if key_suffix else "chart_main"
            st_echarts(
                options=options,
                height="500px",
                theme="light",
                key=chart_key
            )
        else:
            st.error("❌ Chart has no series data!")
            with st.expander("🔍 Chart JSON"):
                st.json(options)
        
    except Exception as e:
        st.error(f"Error rendering chart: {e}")
        import traceback
        st.code(traceback.format_exc())


# ============================================================================
# Executive Summary
# ============================================================================

def run_summary_generation():
    """
    Generate executive summary from data and chart.
    
    Returns:
        Executive summary text
    """
    try:
        # Get AI client
        client = get_ai_client(st.session_state.ai_provider)
        
        # Generate summary
        with st.spinner("📝 Generating executive summary..."):
            summary = generate_summary(
                client,
                st.session_state.csv_data,
                st.session_state.chart_analysis,
                st.session_state.chart_json
            )
        
        return summary
        
    except Exception as e:
        st.error(f"Summary generation failed: {e}")
        return None


def render_summary(summary_text: str):
    """
    Render the executive summary with copy button.
    
    Args:
        summary_text: Executive summary text
    """
    if not summary_text:
        return
    
    st.markdown("### 📝 Executive Summary")
    st.markdown(summary_text)
    
    # Download button
    st.download_button(
        label="📥 Download as Markdown",
        data=f"# Executive Summary\n\n{summary_text}",
        file_name="executive_summary.md",
        mime="text/markdown"
    )
    
    st.markdown("---")


# ============================================================================
# Main Area - Chat Interface
# ============================================================================

def render_main():
    """Render the main content area with chat interface."""
    
    st.title("📊 SF CHAI")
    st.markdown("**S**treamlit + e**C**harts + **H**elper + **AI**")
    st.markdown("Chat with me to create beautiful charts from your data!")
    
    st.markdown("---")
    
    # Display chat history
    render_chat_messages()
    
    # Chat input
    user_input = st.chat_input("Type a message or upload files...", key="main_chat_input")
    
    if user_input:
        handle_user_message(user_input)
        st.rerun()
    
    # File upload section (below chat)
    st.markdown("---")
    with st.expander("📎 Upload Files", expanded=False):
        col1, col2 = st.columns(2)
        
        with col1:
            csv_file = st.file_uploader(
                "Upload CSV Data",
                type=["csv"],
                key="csv_uploader",
                help="Upload your data file"
            )
            if csv_file and csv_file != st.session_state.get("last_csv_upload"):
                st.session_state.last_csv_upload = csv_file
                handle_csv_upload(csv_file)
                st.rerun()
        
        with col2:
            png_file = st.file_uploader(
                "Upload Reference Image",
                type=["png", "jpg", "jpeg"],
                key="png_uploader",
                help="Upload reference chart image"
            )
            if png_file and png_file != st.session_state.get("last_png_upload"):
                st.session_state.last_png_upload = png_file
                handle_png_upload(png_file)
                st.rerun()


def render_chat_messages():
    """Display all chat messages from history."""
    # Show welcome message if no history
    if not st.session_state.chat_history:
        with st.chat_message("assistant"):
            st.markdown("""
👋 **Welcome to SF CHAI!**

I'll help you create beautiful charts from your data.

**To get started:**
1. Upload your CSV data file
2. Upload a reference chart image (PNG/JPG)

I'll analyze both and show you exactly how your chart will look before generating it.

You can upload files using the "📎 Upload Files" section below, or just tell me what you'd like to do!
            """)
        return
    
    # Display chat history
    for i, message in enumerate(st.session_state.chat_history):
        role = message.get("role", "assistant")
        content = message.get("content", "")
        metadata = message.get("metadata", {})
        msg_type = metadata.get("type", "text")
        
        with st.chat_message(role):
            if msg_type == "text":
                st.markdown(content)
            elif msg_type == "file_upload":
                st.markdown(content)
            elif msg_type == "proposal":
                st.markdown(content)
            elif msg_type == "chart":
                st.markdown(content)
                # Display chart if available with unique key
                if "chart_json" in metadata:
                    render_chart(metadata["chart_json"], key_suffix=f"msg_{i}")


def handle_user_message(message: str):
    """Handle a user text message."""
    # Add user message to history
    st.session_state.chat_history.append({
        "role": "user",
        "content": message,
        "metadata": {"type": "text", "timestamp": datetime.now()}
    })
    
    # Get current phase
    phase = st.session_state.get("conversation_phase", "idle")
    
    # Route based on phase
    if phase == "idle":
        # Initial greeting or general question
        response = "I'm ready to help! Please upload your CSV data and reference chart image to get started."
        st.session_state.chat_history.append({
            "role": "assistant",
            "content": response,
            "metadata": {"type": "text", "timestamp": datetime.now()}
        })
    
    elif phase == "upload":
        # Waiting for files
        response = "I'm waiting for your files. Please upload both CSV and reference image."
        st.session_state.chat_history.append({
            "role": "assistant",
            "content": response,
            "metadata": {"type": "text", "timestamp": datetime.now()}
        })
    
    elif phase == "review":
        # User is reviewing proposal - use LLM to detect intent
        client = get_ai_client(st.session_state.ai_provider)
        intent_result = detect_user_intent(
            client, 
            message, 
            phase, 
            st.session_state.get("current_proposal")
        )
        
        intent = intent_result.get("intent")
        
        if intent == "modify":
            # User wants to modify the proposal
            handle_proposal_modification(message)
        elif intent == "approve":
            # User approved - generate chart
            response = "Great! Generating your chart now..."
            st.session_state.chat_history.append({
                "role": "assistant",
                "content": response,
                "metadata": {"type": "text", "timestamp": datetime.now()}
            })
            # Trigger chart generation
            generate_chart_from_proposal()
        else:
            # User has a question or unclear intent
            response = "I'm here to help! You can:\n- Ask me to change specific aspects of the proposal\n- Say 'looks good' or 'generate' to create the chart\n- Ask questions about any part of the proposal"
            st.session_state.chat_history.append({
                "role": "assistant",
                "content": response,
                "metadata": {"type": "text", "timestamp": datetime.now()}
            })
    
    elif phase == "generation":
        # Check for export requests first
        message_lower = message.lower()
        if any(keyword in message_lower for keyword in ["export", "download", "generate html", "generate python", "save as"]):
            handle_export_request(message)
        else:
            # Chart is being generated or already generated - use LLM to detect intent
            client = get_ai_client(st.session_state.ai_provider)
            intent_result = detect_user_intent(
                client, 
                message, 
                phase, 
                st.session_state.get("current_proposal")
            )
            
            intent = intent_result.get("intent")
            
            if intent == "modify":
                # User wants to modify the generated chart
                handle_chart_modification(message)
            else:
                response = "Your chart has been generated! You can:\n- Ask me to modify it (e.g., 'change the color', 'add labels', 'make lines smooth')\n- Export it (e.g., 'export as HTML', 'export as Python')\n- Start a new chart by uploading new files"
                st.session_state.chat_history.append({
                    "role": "assistant",
                    "content": response,
                    "metadata": {"type": "text", "timestamp": datetime.now()}
                })


def handle_csv_upload(csv_file):
    """Handle CSV file upload."""
    try:
        # Show progress indicator
        with st.spinner("📊 Processing CSV file..."):
            # Load CSV
            df = load_csv_data(csv_file)
            if df is not None:
                st.session_state.uploaded_csv = df
                st.session_state.uploaded_csv_filename = csv_file.name
                
                # Add message to chat
                message = f"""
✅ **CSV file received:** `{csv_file.name}`

📊 **Data summary:**
- {df.shape[0]} rows, {df.shape[1]} columns
- Columns: {', '.join(df.columns.tolist())}
"""
                
                # Check if it's long format
                if 'key' in df.columns and 'value' in df.columns:
                    unique_keys = df['key'].unique()
                    message += f"- {len(unique_keys)} series detected: {', '.join(unique_keys)}\n"
                
                message += "\nNow upload your reference chart image."
                
                st.session_state.chat_history.append({
                    "role": "assistant",
                    "content": message,
                    "metadata": {
                        "type": "file_upload",
                        "file_type": "csv",
                        "file_name": csv_file.name,
                        "timestamp": datetime.now()
                    }
                })
                
                # Update phase and trigger analysis if both files ready
                if st.session_state.get("uploaded_png") is not None:
                    st.session_state.conversation_phase = "analysis"
                    # Trigger analysis and proposal generation
                    generate_and_present_proposal()
                else:
                    st.session_state.conversation_phase = "upload"
    
    except Exception as e:
        st.session_state.chat_history.append({
            "role": "assistant",
            "content": f"⚠️ Error loading CSV: {str(e)}",
            "metadata": {"type": "text", "timestamp": datetime.now()}
        })


def handle_png_upload(png_file):
    """Handle PNG file upload."""
    try:
        # Show progress indicator
        with st.spinner("🖼️ Processing image file..."):
            from PIL import Image
            image = Image.open(png_file)
            
            st.session_state.uploaded_png = image
            st.session_state.uploaded_png_filename = png_file.name
            
            # Add message to chat
            message = f"""
✅ **Reference image received:** `{png_file.name}`
"""
            
            st.session_state.chat_history.append({
                "role": "assistant",
                "content": message,
                "metadata": {
                    "type": "file_upload",
                    "file_type": "png",
                    "file_name": png_file.name,
                    "timestamp": datetime.now()
                }
            })
            
            # Update phase and trigger analysis if both files ready
            if st.session_state.get("uploaded_csv") is not None:
                st.session_state.conversation_phase = "analysis"
                # Trigger analysis and proposal generation
                generate_and_present_proposal()
            else:
                st.session_state.conversation_phase = "upload"
    
    except Exception as e:
        st.session_state.chat_history.append({
            "role": "assistant",
            "content": f"⚠️ Error loading image: {str(e)}",
            "metadata": {"type": "text", "timestamp": datetime.now()}
        })


def detect_user_intent(client, message: str, conversation_phase: str, proposal: dict = None) -> dict:
    """
    Use LLM to detect user intent from message.
    
    Args:
        client: AI client
        message: User's message
        conversation_phase: Current conversation phase
        proposal: Current proposal (if any)
        
    Returns:
        Dict with intent and confidence
    """
    prompt = f"""Analyze this user message and determine their intent.

Current Phase: {conversation_phase}
User Message: "{message}"

Possible Intents:
1. "approve" - User wants to approve/generate the chart (e.g., "generate", "looks good", "create it", "go ahead", "yes", "ok", typos like "genereate")
2. "modify" - User wants to change something (e.g., "change color", "make it smooth", "move label", "add annotation")
3. "question" - User is asking a question or needs clarification
4. "other" - Something else

Consider:
- Typos and misspellings (e.g., "genereate" means "generate")
- Context of the conversation phase
- Natural language variations

Return ONLY valid JSON:
{{
  "intent": "approve" or "modify" or "question" or "other",
  "confidence": 0.0 to 1.0,
  "reasoning": "brief explanation"
}}"""

    try:
        response = client.generate_text(prompt=prompt, temperature=0.1)
        
        # Try to parse JSON
        import re
        json_match = re.search(r'\{[\s\S]*\}', response)
        if json_match:
            result = json.loads(json_match.group(0))
            return result
        
        # Fallback to keyword matching if LLM fails
        return _fallback_intent_detection(message, conversation_phase)
    except Exception as e:
        # Fallback to keyword matching
        return _fallback_intent_detection(message, conversation_phase)


def _fallback_intent_detection(message: str, conversation_phase: str) -> dict:
    """Fallback keyword-based intent detection."""
    message_lower = message.lower().strip()
    
    # Check for approval
    approval_keywords = ["approve", "generate", "genereate", "generete", "looks good", "yes", "ok", "okay", "go ahead", "proceed", "create", "make it"]
    if any(keyword in message_lower for keyword in approval_keywords):
        return {"intent": "approve", "confidence": 0.8, "reasoning": "Keyword match"}
    
    # Check for modification
    modification_keywords = ["change", "modify", "update", "adjust", "fix", "make", "add", "remove", "move", "set"]
    if any(keyword in message_lower for keyword in modification_keywords):
        return {"intent": "modify", "confidence": 0.8, "reasoning": "Keyword match"}
    
    # Check for question
    question_keywords = ["what", "how", "why", "when", "where", "can you", "could you", "?"]
    if any(keyword in message_lower for keyword in question_keywords):
        return {"intent": "question", "confidence": 0.7, "reasoning": "Keyword match"}
    
    return {"intent": "other", "confidence": 0.5, "reasoning": "No clear match"}


def detect_approval(message: str) -> bool:
    """Detect if user message is an approval (deprecated - use detect_user_intent)."""
    approval_phrases = [
        "approve", "looks good", "generate", "yes", "ok", "okay",
        "go ahead", "proceed", "correct", "that's right", "perfect",
        "genereate", "generete", "genrate"  # Common typos
    ]
    message_lower = message.lower().strip()
    return any(phrase in message_lower for phrase in approval_phrases)


def detect_modification_request(message: str) -> bool:
    """Detect if user message is requesting a modification."""
    modification_keywords = [
        "change", "modify", "update", "adjust", "fix", "should be",
        "instead", "rather", "different", "wrong", "incorrect",
        "make it", "set it", "use", "replace"
    ]
    message_lower = message.lower()
    return any(keyword in message_lower for keyword in modification_keywords)


# ============================================================================
# Phase 3: Review & Approval
# ============================================================================

def handle_proposal_modification(message: str):
    """
    Handle user request to modify the proposal.
    
    Args:
        message: User's modification request
    """
    try:
        # Get current proposal
        proposal = st.session_state.get("current_proposal")
        if not proposal:
            st.session_state.chat_history.append({
                "role": "assistant",
                "content": "⚠️ No proposal found. Please upload files first.",
                "metadata": {"type": "text", "timestamp": datetime.now()}
            })
            return
        
        # Show progress indicator
        with st.spinner("🔄 Processing your request..."):
            # Parse modification request using AI
            client = get_ai_client(st.session_state.ai_provider)
            modifications = parse_modification_request(client, message, proposal)
        
        if modifications.get("error"):
            st.session_state.chat_history.append({
                "role": "assistant",
                "content": f"⚠️ {modifications['error']}\n\nCould you please rephrase your request?",
                "metadata": {"type": "text", "timestamp": datetime.now()}
            })
            return
        
        # Check if there are actual modifications or just confirmation
        if not modifications.get("modifications") or modifications.get("modifications") == {}:
            # User is confirming current settings
            confirmation = "✅ **Understood**\n\n"
            for change in modifications.get("changes", []):
                confirmation += f"{change}\n\n"
            
            confirmation += "The proposal already matches your requirements. "
            confirmation += "Say **'looks good'** or **'generate'** to create the chart."
            
            st.session_state.chat_history.append({
                "role": "assistant",
                "content": confirmation,
                "metadata": {"type": "text", "timestamp": datetime.now()}
            })
            return
        
        # Apply modifications to proposal
        updated_proposal = apply_modifications_to_proposal(proposal, modifications)
        st.session_state.current_proposal = updated_proposal
        
        # Format and display updated proposal
        proposal_text = format_proposal_for_display(updated_proposal)
        
        # Add confirmation message
        confirmation = "✅ **Proposal Updated**\n\n"
        confirmation += f"I've made the following changes:\n"
        for change in modifications.get("changes", []):
            confirmation += f"- {change}\n"
        confirmation += "\n" + proposal_text
        
        st.session_state.chat_history.append({
            "role": "assistant",
            "content": confirmation,
            "metadata": {
                "type": "proposal",
                "proposal": updated_proposal,
                "timestamp": datetime.now()
            }
        })
        
    except Exception as e:
        st.session_state.chat_history.append({
            "role": "assistant",
            "content": f"⚠️ Error processing modification: {str(e)}",
            "metadata": {"type": "text", "timestamp": datetime.now()}
        })


def parse_modification_request(client, message: str, proposal: dict) -> dict:
    """
    Parse user's modification request using AI.
    
    Args:
        client: AI client
        message: User's message
        proposal: Current proposal
        
    Returns:
        Dict with modifications to apply
    """
    prompt = f"""Parse this modification request and return JSON with the changes to make.

Current Proposal:
{json.dumps(proposal, indent=2)}

User Request:
"{message}"

IMPORTANT DISTINCTIONS:
1. "Labels at line ends" = endLabel (labels at RIGHT edge of chart)
2. "Labels above/below lines" = inline labels (labels IN THE MIDDLE of chart, above/below the actual line)
3. "Make line smooth" or "smooth lines" = change line_style to "smooth"
4. "Straight lines" = change line_style to "straight"
5. "Annotation font size" or "label font size" for horizontal/vertical lines or bands = use update_horizontal_line_font_size, update_vertical_line_font_size, or update_band_font_size

If user says:
- "I don't want legend at line ends" → They want labels IN THE MIDDLE, not at the ends
- "Label should be above the line" → They want inline labels positioned above the line
- "Label should be below the line" → They want inline labels positioned below the line
- "Make lines smooth" → Change all series line_style to "smooth"
- "Make first line smooth" → Change series[0] line_style to "smooth"
- "Make chart lines thicker" or "increase line thickness" → Increase all_series_line_width (e.g., to 3, 4, or 5)
- "Make first line thicker" → Change series[0] line_width
- "Make axis lines thicker" or "thicker axis" → Increase axis_style.line_width (e.g., to 2 or 3)
- "Make axis black" or "black axis lines" → Set axis_style.line_color to "#000000"
- "Change axis label color" or "axis label font color" → Set font_colors.axis_label to the specified color
- "Change axis title color" → Set font_colors.axis_title to the specified color
- "Change grid color" or "change gridline color" → Set grid.color to the specified color
- "Hide grid" or "remove gridlines" → Set grid.show to false
- "Show grid" → Set grid.show to true
- "Show data table" or "add comparison table" → Set data_table.show to true
- "Hide table" or "remove table" → Set data_table.show to false
- "Show last 3 months in table" → Set data_table.periods to 3
- "Make table bigger" → Increase data_table.font_size
- "Change table font to Arial" → Set data_table.font_family to "Arial"

For inline labels (not at ends), set:
- legend_type: "inline_middle" (new type for labels in middle of chart)
- label_positions: {{"series_name": "above" or "below"}}

For line style changes:
- series_updates: [{{"index": 0, "line_style": "smooth"}}] for specific series
- OR include "all_series_line_style": "smooth" to change all series

For line width changes:
- series_updates: [{{"index": 0, "line_width": 5}}] for specific series
- OR include "all_series_line_width": 5 to change all series

Return JSON with:
{{
  "changes": ["description of change 1", "description of change 2"],
  "modifications": {{
    "legend_type": "inline" (at line ends) or "inline_middle" (above/below lines in middle) or "box" (separate legend box),
    "legend_position": "top", "bottom", "left", "right" (for box legend),
    "label_positions": {{"Headline": "above", "Core": "below"}},
    "all_series_line_style": "smooth" or "straight" (to change all series),
    "all_series_line_width": 5 (to change all series line thickness),
    "series_updates": [
      {{"index": 0, "color": "#hex", "name": "new name", "line_style": "smooth/straight", "line_width": 5}}
    ],
    "annotation_updates": {{
      "add_horizontal_lines": [{{"value": 2.0, "label": "Target", "font_size": 16}}],
      "add_vertical_lines": [{{"value": "2020", "label": "Event", "font_size": 14}}],
      "add_bands": [{{"start": "2019-12", "end": "2020-02", "label": "Covid", "color": "#d3d3d3", "font_size": 12}}],
      "update_horizontal_line_font_size": 16,
      "update_vertical_line_font_size": 14,
      "update_band_font_size": 12,
      "remove_annotations": ["description"]
    }},
    "font_updates": {{
      "axis_label": 12,
      "axis_title": 14,
      "legend": 11
    }},
    "font_color_updates": {{
      "axis_label": "#000000",
      "axis_title": "#000000"
    }},
    "grid_updates": {{
      "color": "#cccccc",
      "show": true
    }},
    "data_table_updates": {{
      "show": true,
      "position": "bottom_right",
      "periods": 3,
      "font_size": 12
    }},
    "axis_style_updates": {{
      "line_color": "#000000",
      "line_width": 2
    }}
  }}
}}

If you can't parse the request, return: {{"error": "Could not understand the request"}}

Return ONLY valid JSON:"""

    try:
        response = client.generate_text(prompt=prompt, temperature=0.3)
        
        # Try to parse JSON
        import re
        json_match = re.search(r'\{[\s\S]*\}', response)
        if json_match:
            result = json.loads(json_match.group(0))
            
            # If no modifications but has changes, it means user is confirming current settings
            if result.get("modifications") == {} and result.get("changes"):
                return result
            
            return result
        
        return {"error": "Could not parse modification request"}
    except Exception as e:
        return {"error": f"Error parsing request: {str(e)}"}
        import re
        json_match = re.search(r'\{[\s\S]*\}', response)
        if json_match:
            return json.loads(json_match.group(0))
        
        return {"error": "Could not parse modification request"}
    except Exception as e:
        return {"error": f"Error parsing request: {str(e)}"}


def apply_modifications_to_proposal(proposal: dict, modifications: dict) -> dict:
    """
    Apply modifications to the proposal.
    
    Args:
        proposal: Current proposal
        modifications: Modifications to apply
        
    Returns:
        Updated proposal
    """
    import copy
    updated = copy.deepcopy(proposal)
    
    mods = modifications.get("modifications", {})
    
    # Update legend
    if "legend_type" in mods:
        updated["visual_config"]["legend"]["type"] = mods["legend_type"]
    if "legend_position" in mods:
        updated["visual_config"]["legend"]["position"] = mods["legend_position"]
    
    # Update label positions (for inline_middle type)
    if "label_positions" in mods:
        if "label_positions" not in updated["visual_config"]:
            updated["visual_config"]["label_positions"] = {}
        updated["visual_config"]["label_positions"] = mods["label_positions"]
    
    # Update all series line style if specified
    if "all_series_line_style" in mods:
        for series in updated["data_mapping"]["series"]:
            series["line_style"] = mods["all_series_line_style"]
    
    # Update all series line width if specified
    if "all_series_line_width" in mods:
        for series in updated["data_mapping"]["series"]:
            series["line_width"] = mods["all_series_line_width"]
    
    # Update series
    for series_update in mods.get("series_updates", []):
        idx = series_update.get("index", 0)
        if idx < len(updated["data_mapping"]["series"]):
            series = updated["data_mapping"]["series"][idx]
            if "color" in series_update:
                series["color"] = series_update["color"]
            if "name" in series_update:
                series["series_name"] = series_update["name"]
            if "line_style" in series_update:
                series["line_style"] = series_update["line_style"]
            if "line_width" in series_update:
                series["line_width"] = series_update["line_width"]
    
    # Update annotations
    ann_updates = mods.get("annotation_updates", {})
    if "add_horizontal_lines" in ann_updates:
        updated["visual_config"]["annotations"]["horizontal_lines"].extend(
            ann_updates["add_horizontal_lines"]
        )
    if "add_vertical_lines" in ann_updates:
        updated["visual_config"]["annotations"]["vertical_lines"].extend(
            ann_updates["add_vertical_lines"]
        )
    if "add_bands" in ann_updates:
        updated["visual_config"]["annotations"]["bands"].extend(
            ann_updates["add_bands"]
        )
    
    # Update font sizes for existing annotations
    if "update_horizontal_line_font_size" in ann_updates:
        font_size = ann_updates["update_horizontal_line_font_size"]
        for hline in updated["visual_config"]["annotations"]["horizontal_lines"]:
            hline["font_size"] = font_size
    
    if "update_vertical_line_font_size" in ann_updates:
        font_size = ann_updates["update_vertical_line_font_size"]
        for vline in updated["visual_config"]["annotations"]["vertical_lines"]:
            vline["font_size"] = font_size
    
    if "update_band_font_size" in ann_updates:
        font_size = ann_updates["update_band_font_size"]
        for band in updated["visual_config"]["annotations"]["bands"]:
            band["font_size"] = font_size
    
    # Update fonts
    font_updates = mods.get("font_updates", {})
    for key, value in font_updates.items():
        if key in updated["visual_config"]["fonts"]:
            updated["visual_config"]["fonts"][key] = value
    
    # Update font colors
    font_color_updates = mods.get("font_color_updates", {})
    if font_color_updates:
        if "font_colors" not in updated["visual_config"]:
            updated["visual_config"]["font_colors"] = {}
        for key, value in font_color_updates.items():
            updated["visual_config"]["font_colors"][key] = value
    
    # Update grid
    grid_updates = mods.get("grid_updates", {})
    if grid_updates:
        if "grid" not in updated["visual_config"]:
            updated["visual_config"]["grid"] = {}
        for key, value in grid_updates.items():
            updated["visual_config"]["grid"][key] = value
    
    # Update data table
    data_table_updates = mods.get("data_table_updates", {})
    if data_table_updates:
        if "data_table" not in updated["visual_config"]:
            updated["visual_config"]["data_table"] = {}
        for key, value in data_table_updates.items():
            updated["visual_config"]["data_table"][key] = value
    
    # Update axis style
    axis_style_updates = mods.get("axis_style_updates", {})
    if axis_style_updates:
        if "axis_style" not in updated["visual_config"]:
            updated["visual_config"]["axis_style"] = {}
        for key, value in axis_style_updates.items():
            updated["visual_config"]["axis_style"][key] = value
    
    return updated


def generate_chart_from_proposal():
    """Generate chart from the approved proposal."""
    try:
        proposal = st.session_state.get("current_proposal")
        if not proposal:
            st.session_state.chat_history.append({
                "role": "assistant",
                "content": "⚠️ No proposal found.",
                "metadata": {"type": "text", "timestamp": datetime.now()}
            })
            return
        
        # Show progress indicator
        with st.spinner("📊 Generating your chart..."):
            # Convert proposal to chart JSON
            try:
                chart_json = convert_proposal_to_chart_json(
                    proposal,
                    st.session_state.uploaded_csv
                )
            except Exception as e:
                # Log the error with more details
                import traceback
                error_details = traceback.format_exc()
                st.session_state.chat_history.append({
                    "role": "assistant",
                    "content": f"⚠️ Error generating chart: {str(e)}\n\nDetails:\n```\n{error_details}\n```",
                    "metadata": {"type": "text", "timestamp": datetime.now()}
                })
                return
            
            # Store chart
            st.session_state.chart_json = chart_json
            st.session_state.csv_data = st.session_state.uploaded_csv
            st.session_state.png_image = st.session_state.uploaded_png
        
        # Add chart to chat
        st.session_state.chat_history.append({
            "role": "assistant",
            "content": "✅ **Chart Generated Successfully!**\n\nYour chart is ready. You can ask me to make changes or download it.",
            "metadata": {
                "type": "chart",
                "chart_json": chart_json,
                "timestamp": datetime.now()
            }
        })
        
        # Update phase
        st.session_state.conversation_phase = "generation"
        
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        st.session_state.chat_history.append({
            "role": "assistant",
            "content": f"⚠️ Error in chart generation: {str(e)}\n\nDetails:\n```\n{error_details}\n```",
            "metadata": {"type": "text", "timestamp": datetime.now()}
        })


def handle_export_request(message: str):
    """
    Handle user request to export chart.
    
    Args:
        message: User's export request
    """
    try:
        # Get current chart and data
        chart_json = st.session_state.get("chart_json")
        csv_data = st.session_state.get("csv_data")
        proposal = st.session_state.get("current_proposal")
        
        # Check if we have the required data (proper DataFrame check)
        if chart_json is None or csv_data is None or csv_data.empty or proposal is None:
            st.session_state.chat_history.append({
                "role": "assistant",
                "content": "⚠️ No chart found. Please generate a chart first.",
                "metadata": {"type": "text", "timestamp": datetime.now()}
            })
            return
        
        # Determine export type
        message_lower = message.lower()
        
        # Show progress
        with st.spinner("📦 Creating export package..."):
            if "html" in message_lower:
                # Export as HTML
                export_type = "HTML"
                # Recreate Plotly figure
                if chart_json.get("type") == "plotly":
                    import plotly.graph_objects as go
                    fig = go.Figure(chart_json["figure"])
                else:
                    # Convert ECharts to Plotly for export
                    fig = generate_plotly_chart(proposal, csv_data)
                
                zip_path = export_to_html(fig, csv_data, proposal)
                
            elif "python" in message_lower or "py" in message_lower:
                # Export as Python
                export_type = "Python"
                # Recreate Plotly figure
                if chart_json.get("type") == "plotly":
                    import plotly.graph_objects as go
                    fig = go.Figure(chart_json["figure"])
                else:
                    fig = generate_plotly_chart(proposal, csv_data)
                
                zip_path = export_to_python(fig, csv_data, proposal)
                
            else:
                # Default to HTML
                export_type = "HTML"
                if chart_json.get("type") == "plotly":
                    import plotly.graph_objects as go
                    fig = go.Figure(chart_json["figure"])
                else:
                    fig = generate_plotly_chart(proposal, csv_data)
                
                zip_path = export_to_html(fig, csv_data, proposal)
        
        # Success message
        response = f"""✅ **{export_type} Export Created!**

Your chart has been exported to:
`{zip_path}`

The zip file contains:
- Chart file ({'chart.html' if export_type == 'HTML' else 'chart.py'})
- Source data (data.csv)
- README with instructions

You can find it in the `downloads` folder.

{'Open chart.html in any web browser - no installation needed!' if export_type == 'HTML' else 'Run the Python script with: python chart.py'}
"""
        
        st.session_state.chat_history.append({
            "role": "assistant",
            "content": response,
            "metadata": {"type": "text", "timestamp": datetime.now()}
        })
        
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        st.session_state.chat_history.append({
            "role": "assistant",
            "content": f"⚠️ Error creating export: {str(e)}\n\nDetails:\n```\n{error_details}\n```",
            "metadata": {"type": "text", "timestamp": datetime.now()}
        })


def handle_chart_modification(message: str):
    """
    Handle user request to modify the generated chart.
    
    Args:
        message: User's modification request
    """
    try:
        # Get current chart and proposal
        chart_json = st.session_state.get("chart_json")
        proposal = st.session_state.get("current_proposal")
        
        if not chart_json or not proposal:
            st.session_state.chat_history.append({
                "role": "assistant",
                "content": "⚠️ No chart found. Please generate a chart first.",
                "metadata": {"type": "text", "timestamp": datetime.now()}
            })
            return
        
        # Show progress indicator
        with st.spinner("🔄 Updating your chart..."):
            # Parse modification request
            client = get_ai_client(st.session_state.ai_provider)
            modifications = parse_modification_request(client, message, proposal)
            
            if modifications.get("error"):
                st.session_state.chat_history.append({
                    "role": "assistant",
                    "content": f"⚠️ {modifications['error']}\n\nCould you please rephrase your request?",
                    "metadata": {"type": "text", "timestamp": datetime.now()}
                })
                return
            
            # Apply modifications to proposal
            updated_proposal = apply_modifications_to_proposal(proposal, modifications)
            st.session_state.current_proposal = updated_proposal
            
            # Regenerate chart with updated proposal
            updated_chart_json = convert_proposal_to_chart_json(
                updated_proposal,
                st.session_state.csv_data
            )
            st.session_state.chart_json = updated_chart_json
        
        # Add confirmation and updated chart to chat
        confirmation = "✅ **Chart Updated**\n\n"
        confirmation += f"I've made the following changes:\n"
        for change in modifications.get("changes", []):
            confirmation += f"- {change}\n"
        confirmation += "\nHere's your updated chart:"
        
        st.session_state.chat_history.append({
            "role": "assistant",
            "content": confirmation,
            "metadata": {
                "type": "chart",
                "chart_json": updated_chart_json,
                "timestamp": datetime.now()
            }
        })
        
    except Exception as e:
        st.session_state.chat_history.append({
            "role": "assistant",
            "content": f"⚠️ Error modifying chart: {str(e)}",
            "metadata": {"type": "text", "timestamp": datetime.now()}
        })


def convert_proposal_to_chart_json(proposal: dict, csv_data: pd.DataFrame) -> dict:
    """
    Convert proposal to chart JSON configuration.
    Uses Plotly for inline_middle labels, ECharts for others.
    
    Args:
        proposal: Approved proposal
        csv_data: CSV DataFrame
        
    Returns:
        Chart configuration dict with type indicator
    """
    legend_type = proposal["visual_config"]["legend"]["type"]
    
    # Use Plotly for inline_middle (labels in middle of lines)
    if legend_type == "inline_middle":
        fig = generate_plotly_chart(proposal, csv_data)
        return {
            "type": "plotly",
            "figure": convert_plotly_to_json(fig)
        }
    
    # Use ECharts for other types
    return {
        "type": "echarts",
        "options": _generate_echarts_config(proposal, csv_data)
    }


def _generate_echarts_config(proposal: dict, csv_data: pd.DataFrame) -> dict:
    """Generate ECharts configuration (original implementation)."""
    # Pivot data if needed
    if 'key' in csv_data.columns and 'value' in csv_data.columns:
        csv_data = csv_data.pivot(index='date', columns='key', values='value').reset_index()
    
    # Get x-axis data
    x_col = proposal["data_mapping"]["x_axis_column"]
    x_data = csv_data[x_col].tolist()
    
    # Get legend configuration
    legend_type = proposal["visual_config"]["legend"]["type"]
    label_positions = proposal["visual_config"].get("label_positions", {})
    
    # Build series
    series = []
    
    for series_info in proposal["data_mapping"]["series"]:
        csv_col = series_info["csv_column"]
        series_data = csv_data[csv_col].tolist()
        series_name = series_info["series_name"]
        
        series_config = {
            "name": series_name,
            "type": "line",
            "data": series_data,
            "smooth": series_info["line_style"] == "smooth",
            "smoothMonotone": "x" if series_info["line_style"] == "smooth" else None,
            "itemStyle": {"color": series_info["color"]},
            "lineStyle": {"width": series_info["line_width"]}
        }
        
        # Add endLabel for both inline types
        if legend_type in ["inline", "inline_middle"]:
            series_config["endLabel"] = {
                "show": True,
                "formatter": "{a}",
                "fontSize": proposal["visual_config"]["fonts"]["legend"],
                "distance": 10,
                "fontWeight": "bold"
            }
        
        series.append(series_config)
    
    # Add annotations to first series
    if series and proposal["visual_config"]["annotations"]:
        annotations = proposal["visual_config"]["annotations"]
        mark_data = []
        
        # Horizontal lines
        for hline in annotations.get("horizontal_lines", []):
            mark_data.append({
                "yAxis": hline.get("value"),
                "label": {"formatter": hline.get("label", "")},
                "lineStyle": {
                    "type": hline.get("style", "dashed"),
                    "color": hline.get("color", "#000000")
                }
            })
        
        # Vertical lines
        for vline in annotations.get("vertical_lines", []):
            mark_data.append({
                "xAxis": vline.get("value"),
                "label": {"formatter": vline.get("label", "")},
                "lineStyle": {
                    "type": vline.get("style", "solid"),
                    "color": vline.get("color", "#cccccc")
                }
            })
        
        if mark_data:
            series[0]["markLine"] = {"data": mark_data}
    
    # Build chart
    chart = {
        "tooltip": {"trigger": "axis"},
        "toolbox": {"feature": {"saveAsImage": {"title": "Save as PNG"}}},
        "xAxis": {
            "type": "category",
            "data": x_data,
            "boundaryGap": False,
            "axisLabel": {"fontSize": proposal["visual_config"]["fonts"]["axis_label"]}
        },
        "yAxis": {
            "type": "value",
            "axisLabel": {"fontSize": proposal["visual_config"]["fonts"]["axis_label"]}
        },
        "series": series,
        "grid": {
            "left": "8%",
            "right": "25%" if proposal["visual_config"]["legend"]["type"] == "inline" else "8%",
            "top": "8%",
            "bottom": "8%",
            "containLabel": True
        }
    }
    
    # Add legend box if not inline
    if proposal["visual_config"]["legend"]["type"] == "box":
        chart["legend"] = {
            "data": [s["name"] for s in series],
            "top": "5%",
            proposal["visual_config"]["legend"]["position"]: "5%"
        }
    
    return chart


# ============================================================================
# Phase 2: Analysis & Proposal Generation
# ============================================================================

def generate_and_present_proposal():
    """Generate analysis and proposal, then present to user."""
    try:
        # Show progress status
        with st.status("🔍 Analyzing your files...", expanded=True) as status:
            st.write("📊 Reading CSV data...")
            st.write("🖼️ Processing reference image...")
            
            # Get AI client
            client = get_ai_client(st.session_state.ai_provider)
            
            st.write("🤖 Running AI vision analysis...")
            # Encode image
            image_base64 = encode_image_to_base64(st.session_state.uploaded_png)
            
            # Run vision analysis
            analysis = analyze_chart_image(client, image_base64)
            
            # Check for errors
            if isinstance(analysis, dict) and "error" in analysis:
                error_msg = f"⚠️ Analysis error: {analysis.get('error')}"
                if "fallback_analysis" in analysis:
                    error_msg += "\n\nUsing fallback analysis to continue."
                    analysis = analysis["fallback_analysis"]
                else:
                    status.update(label="❌ Analysis failed", state="error")
                    st.session_state.chat_history.append({
                        "role": "assistant",
                        "content": error_msg,
                        "metadata": {"type": "text", "timestamp": datetime.now()}
                    })
                    st.session_state.conversation_phase = "idle"
                    return
            
            st.write("📋 Creating chart proposal...")
            # Store analysis
            st.session_state.chart_analysis = analysis
            
            # Create proposal from analysis
            proposal = create_proposal_from_analysis(analysis, st.session_state.uploaded_csv)
            st.session_state.current_proposal = proposal
            
            # Format proposal for display
            proposal_text = format_proposal_for_display(proposal)
            
            status.update(label="✅ Analysis complete!", state="complete")
        
        # Add proposal to chat
        st.session_state.chat_history.append({
            "role": "assistant",
            "content": proposal_text,
            "metadata": {
                "type": "proposal",
                "proposal": proposal,
                "timestamp": datetime.now()
            }
        })
        
        # Update phase to review
        st.session_state.conversation_phase = "review"
        
    except Exception as e:
        st.session_state.chat_history.append({
            "role": "assistant",
            "content": f"⚠️ Error generating proposal: {str(e)}",
            "metadata": {"type": "text", "timestamp": datetime.now()}
        })
        st.session_state.conversation_phase = "idle"


def create_proposal_from_analysis(analysis: dict, csv_data: pd.DataFrame) -> dict:
    """
    Create a structured proposal from vision analysis and CSV data.
    
    Args:
        analysis: Vision analysis result
        csv_data: CSV DataFrame
        
    Returns:
        Proposal dict with data mapping and visual configuration
    """
    # Pivot data if in long format
    if 'key' in csv_data.columns and 'value' in csv_data.columns:
        csv_data_wide = csv_data.pivot(index='date', columns='key', values='value').reset_index()
    else:
        csv_data_wide = csv_data
    
    # Extract series info from analysis
    series_from_analysis = analysis.get("series", [])
    colors_from_analysis = analysis.get("colors", ["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728"])
    
    # Map CSV columns to series
    data_columns = [col for col in csv_data_wide.columns if col != csv_data_wide.columns[0]]
    
    series_mappings = []
    for i, col in enumerate(data_columns):
        # Get series config from analysis if available
        series_config = series_from_analysis[i] if i < len(series_from_analysis) else {}
        
        # Get sample values
        sample_values = csv_data_wide[col].head(3).tolist()
        
        # Use the CSV column name as the series name (more reliable than vision analysis)
        # Extract a clean name from the column (e.g., "YoY_pce_headline" -> "Headline")
        series_name = col
        if "_" in col:
            # Try to extract meaningful name from column
            parts = col.split("_")
            if len(parts) > 1:
                # Take the last part and capitalize it
                series_name = parts[-1].capitalize()
        
        series_mappings.append({
            "csv_column": col,
            "series_name": series_name,
            "color": series_config.get("color", colors_from_analysis[i % len(colors_from_analysis)]),
            "line_style": "smooth" if series_config.get("smooth", True) else "straight",
            "line_width": series_config.get("line_width", 2),
            "sample_values": sample_values
        })
    
    # Extract visual configuration
    legend_info = analysis.get("legend", {})
    annotations = analysis.get("annotations", {})
    font_sizes = analysis.get("font_sizes", {})
    
    proposal = {
        "chart_type": analysis.get("chart_type", "line") or "line",
        "data_mapping": {
            "x_axis_column": csv_data_wide.columns[0],
            "series": series_mappings
        },
        "visual_config": {
            "legend": {
                "type": legend_info.get("type", "inline") if isinstance(legend_info, dict) else "inline",
                "position": (legend_info.get("position") or "right") if isinstance(legend_info, dict) else "right"
            },
            "annotations": {
                "horizontal_lines": annotations.get("horizontal_lines", []) if isinstance(annotations, dict) else [],
                "vertical_lines": annotations.get("vertical_lines", []) if isinstance(annotations, dict) else [],
                "bands": annotations.get("bands", []) if isinstance(annotations, dict) else []
            },
            "fonts": {
                "axis_label": font_sizes.get("axis_label", 11) if isinstance(font_sizes, dict) else 11,
                "axis_title": font_sizes.get("axis_title", 13) if isinstance(font_sizes, dict) else 13,
                "legend": font_sizes.get("legend", 12) if isinstance(font_sizes, dict) else 12
            },
            "font_colors": {
                "axis_label": "#666666",
                "axis_title": "#333333"
            },
            "grid": {
                "show": analysis.get("grid", {"show": True}).get("show", True) if isinstance(analysis.get("grid"), dict) else True,
                "color": "#e0e0e0"
            },
            "axis_style": {
                "line_color": "#999999",
                "line_width": 1
            },
            "data_table": analysis.get("data_table", {
                "show": False,
                "position": "bottom_right",
                "periods": 2,
                "metrics": ["value", "change_pct"],
                "series_names": [],
                "font_size": 10,
                "font_family": "Arial"
            }) if isinstance(analysis.get("data_table"), dict) else {
                "show": False,
                "position": "bottom_right",
                "periods": 2,
                "metrics": ["value", "change_pct"],
                "series_names": [],
                "font_size": 10,
                "font_family": "Arial"
            }
        }
    }
    
    return proposal


def format_proposal_for_display(proposal: dict) -> str:
    """
    Format proposal as human-readable text for chat display.
    
    Args:
        proposal: Proposal dict
        
    Returns:
        Formatted markdown string
    """
    text = "## 📋 Chart Generation Proposal\n\n"
    text += "I've analyzed your files. Here's how I plan to create your chart:\n\n"
    
    # Chart type
    text += f"### Chart Type\n"
    chart_type = proposal.get('chart_type', 'line') or 'line'
    text += f"**{chart_type.title()}** chart\n\n"
    
    # Data mapping
    text += f"### Data Mapping\n"
    text += f"**X-Axis:** `{proposal['data_mapping']['x_axis_column']}`\n\n"
    text += f"**Series ({len(proposal['data_mapping']['series'])}):**\n"
    
    for i, series in enumerate(proposal['data_mapping']['series'], 1):
        text += f"{i}. **{series['series_name']}**\n"
        text += f"   - CSV Column: `{series['csv_column']}`\n"
        text += f"   - Color: {series['color']}\n"
        text += f"   - Line Style: {series['line_style']}\n"
        text += f"   - Sample Values: {', '.join(str(v) for v in series['sample_values'])}\n\n"
    
    # Visual configuration
    text += f"### Visual Configuration\n\n"
    
    # Legend
    legend = proposal['visual_config']['legend']
    text += f"**Legend:**\n"
    legend_position = legend.get('position', 'right') or 'right'
    legend_type = legend.get('type', 'inline')
    
    if legend_type == 'inline':
        text += f"- Type: Labels at line ends (right edge of chart)\n"
        text += f"- Position: {legend_position.title()}\n\n"
    elif legend_type == 'inline_middle':
        text += f"- Type: Labels on lines (in middle of chart)\n"
        # Show label positions if specified
        label_positions = proposal['visual_config'].get('label_positions', {})
        if label_positions:
            text += f"- Label Positions:\n"
            for series_name, position in label_positions.items():
                text += f"  - {series_name}: {position}\n"
        text += "\n"
    else:
        text += f"- Type: Separate legend box\n"
        text += f"- Position: {legend_position.title()}\n\n"
    
    # Annotations
    annotations = proposal['visual_config']['annotations']
    h_lines = annotations['horizontal_lines']
    v_lines = annotations['vertical_lines']
    bands = annotations['bands']
    
    if h_lines or v_lines or bands:
        text += f"**Annotations:**\n"
        if h_lines:
            text += f"- {len(h_lines)} horizontal line(s):\n"
            for line in h_lines:
                text += f"  - At y={line.get('value')}: {line.get('label', 'No label')}\n"
        if v_lines:
            text += f"- {len(v_lines)} vertical line(s):\n"
            for line in v_lines:
                text += f"  - At x={line.get('value')}: {line.get('label', 'No label')}\n"
        if bands:
            text += f"- {len(bands)} shaded band(s)\n"
        text += "\n"
    
    # Fonts
    fonts = proposal['visual_config']['fonts']
    text += f"**Fonts:**\n"
    text += f"- Axis Labels: {fonts['axis_label']}px\n"
    text += f"- Axis Titles: {fonts['axis_title']}px\n"
    text += f"- Legend: {fonts['legend']}px\n\n"
    
    # Call to action
    text += "---\n\n"
    text += "**What would you like to do?**\n"
    text += "- Say **'looks good'** or **'generate'** to create the chart\n"
    text += "- Ask me to change anything (e.g., 'change the first series color to red')\n"
    text += "- Ask questions about the proposal\n"
    
    return text


# ============================================================================
# Old Main Area (kept for backward compatibility)
# ============================================================================
    
    # Sample data section
    with st.expander("📚 Load Sample Data"):
        st.markdown("Try the app with sample data:")
        sample_options = list_samples()
        sample_choice = st.selectbox(
            "Choose a sample dataset:",
            options=list(sample_options.keys()),
            format_func=lambda x: f"{x}: {sample_options[x]}",
            key="sample_selector"
        )
        
        if st.button("Load Sample Data", key="load_sample_btn"):
            df, filename, desc = get_sample_data(sample_choice)
            st.session_state.csv_data = df
            st.session_state.csv_filename = filename
            st.session_state.csv_file = None  # Clear uploaded file
            st.success(f"✅ Loaded sample: {filename}")
            st.rerun()
    
    st.markdown("---")
    
    # Create two columns for file uploaders
    col1, col2 = st.columns(2)
    
    # CSV Uploader
    with col1:
        st.subheader("📄 Upload CSV Data")
        csv_file = st.file_uploader(
            "Choose a CSV file",
            type=["csv"],
            help="Upload your data file in CSV format",
            key="csv_uploader"
        )
        
        if csv_file is not None:
            st.session_state.csv_file = csv_file
            st.session_state.csv_filename = csv_file.name
            
            # Load CSV data (Phase 2)
            if st.session_state.csv_data is None:
                with st.spinner("Loading CSV data..."):
                    df = load_csv_data(csv_file)
                    st.session_state.csv_data = df
            
            st.success(f"✅ Loaded: {csv_file.name}")
            
            # Show data preview (Phase 2)
            if st.session_state.csv_data is not None:
                render_data_preview(st.session_state.csv_data)
        else:
            st.info("👆 Upload a CSV file to begin")
            st.session_state.csv_file = None
            st.session_state.csv_filename = None
            st.session_state.csv_data = None
    
    # PNG Uploader
    with col2:
        st.subheader("🖼️ Upload Reference Chart")
        png_file = st.file_uploader(
            "Choose a reference PNG image",
            type=["png", "jpg", "jpeg"],
            help="Upload a screenshot or image of the chart you want to replicate",
            key="png_uploader"
        )
        
        if png_file is not None:
            st.session_state.png_file = png_file
            st.session_state.png_filename = png_file.name
            st.success(f"✅ Loaded: {png_file.name}")
            
            # Show image preview
            from PIL import Image
            image = Image.open(png_file)
            st.session_state.png_image = image
            st.image(image, caption="Reference Chart", width=400)
        else:
            st.info("👆 Upload a reference chart image")
            st.session_state.png_file = None
            st.session_state.png_filename = None
            st.session_state.png_image = None
    
    st.markdown("---")
    
    # Generate Button
    st.subheader("🚀 Generate Chart")
    
    can_generate = (
        st.session_state.csv_file is not None and 
        st.session_state.png_file is not None
    )
    
    if can_generate:
        st.success("✅ Ready to generate! Click the button below.")
    else:
        st.warning("⚠️ Please upload both CSV and PNG files to generate a chart.")
    
    if st.button(
        "Generate Chart",
        type="primary",
        disabled=not can_generate,
        help="Analyze the reference chart and generate a visualization from your CSV data"
    ):
        # Run vision analysis for all chart types
        with st.spinner("🔍 Analyzing reference chart..."):
            analysis = run_vision_analysis()
        
        if analysis and "error" not in analysis:
            st.session_state.chart_analysis = analysis
            st.session_state.ready_to_generate = True
            
            # Show analysis results (collapsible)
            with st.expander("🔍 Vision Analysis Results", expanded=False):
                st.json(analysis)
                chart_type = analysis.get("chart_type", "unknown")
                st.success(f"✅ Detected chart type: **{chart_type}**")
                
                # Show legend type
                legend_info = analysis.get("legend", {})
                if isinstance(legend_info, dict):
                    legend_type = legend_info.get("type", "unknown")
                    st.info(f"📊 Legend type: **{legend_type}**")
                
                # Show annotations
                annotations = analysis.get("annotations", {})
                if isinstance(annotations, dict):
                    h_lines = annotations.get("horizontal_lines", [])
                    v_lines = annotations.get("vertical_lines", [])
                    bands = annotations.get("bands", [])
                    if h_lines or v_lines or bands:
                        st.warning(f"📍 Annotations detected: {len(h_lines)} horizontal lines, {len(v_lines)} vertical lines, {len(bands)} bands")
                    else:
                        st.info("📍 No annotations detected in reference chart")
            
            # Run chart generation
            chart_json = run_chart_generation()
            
            if chart_json:
                is_mismatch = isinstance(chart_json, dict) and chart_json.get("mismatch")
                
                if not is_mismatch:
                    st.session_state.chart_json = chart_json
                    
                    # Render the chart
                    st.markdown("---")
                    render_chart(chart_json)
                    
                    # Generate summary
                    summary = run_summary_generation()
                    
                    if summary:
                        st.session_state.summary_text = summary
                        
                        # Render summary
                        st.markdown("---")
                        render_summary(summary)
                else:
                    # Show mismatch message
                    render_chart(chart_json)
        elif analysis and "error" in analysis:
            st.error(f"Vision analysis failed: {analysis.get('error')}")
        else:
            st.error("Failed to analyze the reference chart. Please try again.")
    
    # Show chart if already generated (but not just generated above)
    elif st.session_state.chart_json is not None:
        st.markdown("---")
        st.subheader("📈 Generated Chart")
        render_chart(st.session_state.chart_json)
        
        # Show summary if already generated
        if st.session_state.summary_text is not None:
            st.markdown("---")
            render_summary(st.session_state.summary_text)
    
    # Show vision analysis results if already done
    if st.session_state.chart_analysis is not None:
        with st.expander("🔍 View Vision Analysis Details"):
            st.json(st.session_state.chart_analysis)


# ============================================================================
# Main Entry Point
# ============================================================================

def main():
    """Main application entry point."""
    # Initialize database
    init_database()
    
    # Initialize session state
    init_session_state()
    
    # Load .env file
    from dotenv import load_dotenv
    load_dotenv()
    
    # Render UI
    render_sidebar()
    render_main()
    # render_floating_chat()  # Removed - using main chat interface instead


if __name__ == "__main__":
    main()
