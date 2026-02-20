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

# Import direct chart generator
from chart_generator import generate_pce_yoy_chart

# For ECharts rendering
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
        
        # File uploads
        "csv_file": None,
        "csv_filename": None,
        "csv_data": None,  # pandas DataFrame
        
        "png_file": None,
        "png_filename": None,
        "png_image": None,  # PIL Image
        
        # Analysis results
        "chart_analysis": None,  # Vision LLM output
        "chart_json": None,  # ECharts option JSON
        "summary_text": None,  # Executive summary
        
        # Chat
        "chat_history": [],
        
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
# Chat Interface
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


def render_chat():
    """Render the chat interface in the sidebar."""
    st.sidebar.markdown("---")
    st.sidebar.subheader("💬 Chat")
    
    # Check if we have data to chat about
    if st.session_state.csv_data is None:
        st.sidebar.info("Upload a CSV file to start chatting")
        return
    
    # Show chat history
    for message in st.session_state.chat_history:
        with st.sidebar.chat_message(message["role"]):
            st.markdown(message["content"])
    
    # Chat input
    user_input = st.sidebar.chat_input(
        "Ask about your data or request chart changes...",
        key="chat_input"
    )
    
    if user_input:
        # Add user message to history
        st.session_state.chat_history.append({
            "role": "user",
            "content": user_input
        })
        
        # Show user message
        with st.sidebar.chat_message("user"):
            st.markdown(user_input)
        
        # Process message
        with st.sidebar.chat_message("assistant"):
            with st.spinner("Thinking..."):
                response = run_chat(user_input)
                
                # Handle response
                if response.get("action") == "text":
                    st.markdown(response.get("response", ""))
                    
                    # Add to history
                    st.session_state.chat_history.append({
                        "role": "assistant",
                        "content": response.get("response", "")
                    })
                    
                elif response.get("action") == "modify_chart":
                    # Handle chart modification
                    changes = response.get("changes", {})
                    st.success("Chart modification requested!")
                    st.json(changes)
                    
                    # Add to history
                    st.session_state.chat_history.append({
                        "role": "assistant",
                        "content": f"Chart modified: {json.dumps(changes)}"
                    })
                    
                elif response.get("action") == "regenerate_summary":
                    # Regenerate summary
                    with st.spinner("Regenerating summary..."):
                        new_summary = run_summary_generation()
                        if new_summary:
                            st.session_state.summary_text = new_summary
                            st.success("Summary regenerated!")
                    
                    # Add to history
                    st.session_state.chat_history.append({
                        "role": "assistant",
                        "content": "Executive summary has been regenerated."
                    })
    
    # Clear chat button
    if st.session_state.chat_history and st.sidebar.button("Clear Chat", key="clear_chat_btn"):
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
        
        return analysis
        
    except Exception as e:
        st.error(f"Vision analysis failed: {e}")
        return None


# ============================================================================
# Chart Generation
# ============================================================================

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
        # Check if this is PCE YoY data (use direct generator)
        csv_data = st.session_state.csv_data
        if 'key' in csv_data.columns and 'YoY_pce_headline' in csv_data['key'].values:
            with st.spinner("🎨 Generating chart..."):
                chart_json = generate_pce_yoy_chart(csv_data)
            return chart_json
        
        # Otherwise use AI generation
        client = get_ai_client(st.session_state.ai_provider)
        csv_info = get_csv_info(st.session_state.csv_data)
        
        with st.spinner("🎨 Generating chart..."):
            chart_json = generate_chart_json(
                client, 
                st.session_state.chart_analysis, 
                st.session_state.csv_data,
                csv_info
            )
        
        return chart_json
        
    except Exception as e:
        st.error(f"Chart generation failed: {e}")
        return {"mismatch": True, "reason": str(e)}


def render_chart(chart_json):
    """
    Render the chart (Plotly or ECharts).
    
    Args:
        chart_json: Plotly Figure or ECharts option JSON
    """
    if chart_json is None:
        return
    
    # Check if it's a Plotly figure
    import plotly.graph_objects as go
    if isinstance(chart_json, go.Figure):
        st.markdown("### 📈 Generated Chart")
        st.plotly_chart(chart_json, use_container_width=True)
        return
    
    # Check for mismatch (ECharts)
    if isinstance(chart_json, dict) and chart_json.get("mismatch"):
        st.error("⚠️ Chart Mapping Issue Detected")
        st.markdown(f"**Reason:** {chart_json.get('reason', 'Unknown issue')}")
        
        # Show clarifying questions
        questions = chart_json.get("clarifying_questions", [])
        if questions:
            st.markdown("**Clarifying Questions:**")
            for q in questions:
                st.markdown(f"- {q}")
        
        # Show raw response if available (for debugging)
        if chart_json.get("raw_response"):
            with st.expander("🔧 Debug: Raw AI Response"):
                st.code(chart_json["raw_response"])
        
        # Show chart analysis for reference
        if st.session_state.chart_analysis:
            with st.expander("📊 Reference Chart Analysis"):
                st.json(st.session_state.chart_analysis)
        
        # Show CSV data info
        if st.session_state.csv_data is not None:
            with st.expander("📄 CSV Data Info"):
                st.markdown(f"**Rows:** {st.session_state.csv_data.shape[0]}")
                st.markdown(f"**Columns:** {st.session_state.csv_data.shape[1]}")
                st.markdown("**Column Names:**")
                st.code(", ".join(st.session_state.csv_data.columns.tolist()))
        
        return
    
    # Render the chart
    st.markdown("### 📈 Generated Chart")
    
    try:
        # Set height and enable toolbox
        options = chart_json.copy()
        
        # Ensure toolbox has saveAsImage
        if "toolbox" not in options:
            options["toolbox"] = {
                "feature": {
                    "saveAsImage": {"title": "Save as PNG"}
                }
            }
        
        # Render with st_echarts - use light theme to match reference
        st_echarts(
            options=options,
            height="500px",
            theme="light"
        )
        
        # Debug: Show chart JSON
        with st.expander("🔍 Debug: Chart JSON"):
            st.json(chart_json)
        
    except Exception as e:
        st.error(f"Error rendering chart: {e}")
        st.json(chart_json)


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
# Main Area - File Uploaders
# ============================================================================

def render_main():
    """Render the main content area with file uploaders."""
    
    st.title("📊 SF CHAI")
    st.markdown("**S**treamlit + **F**Charts + **C**harts + **H**elper + **AI**")
    st.markdown("Upload a CSV file and a reference chart PNG to generate an interactive ECharts visualization.")
    
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
        # Check if this is PCE YoY data (skip vision analysis)
        csv_data = st.session_state.csv_data
        if 'key' in csv_data.columns and 'YoY_pce_headline' in csv_data['key'].values:
            # Direct generation for PCE data
            st.info("✅ Detected PCE YoY data - using direct chart generator")
            
            # Run chart generation directly
            chart_json = run_chart_generation()
            
            if chart_json:
                st.session_state.chart_json = chart_json
                
                # Render the chart
                st.markdown("---")
                render_chart(chart_json)
                
                st.info("💡 Summary generation skipped for Plotly charts. Use chat to ask questions about the data.")
        else:
            # Run vision analysis for other chart types
            with st.spinner("🔍 Analyzing reference chart..."):
                analysis = run_vision_analysis()
            
            if analysis and "error" not in analysis:
                st.session_state.chart_analysis = analysis
                st.session_state.ready_to_generate = True
            
            if analysis and "error" not in analysis:
                st.session_state.chart_analysis = analysis
                st.session_state.ready_to_generate = True
                
                # Show analysis results (collapsible)
                with st.expander("🔍 Vision Analysis Results", expanded=False):
                    st.json(analysis)
                    chart_type = analysis.get("chart_type", "unknown")
                    st.success(f"✅ Detected chart type: **{chart_type}**")
                
                # Run chart generation (Phase 3)
                chart_json = run_chart_generation()
                
                if chart_json:
                    # Check if it's a Plotly figure or ECharts dict
                    import plotly.graph_objects as go
                    is_plotly = isinstance(chart_json, go.Figure)
                    is_mismatch = isinstance(chart_json, dict) and chart_json.get("mismatch")
                    
                    if not is_mismatch:
                        st.session_state.chart_json = chart_json
                        
                        # Render the chart
                        st.markdown("---")
                        render_chart(chart_json)
                        
                        # Generate summary (Phase 4) - Skip for Plotly charts
                        if not is_plotly:
                            summary = run_summary_generation()
                            
                            if summary:
                                st.session_state.summary_text = summary
                                
                                # Render summary
                                st.markdown("---")
                                render_summary(summary)
                        else:
                            st.info("💡 Summary generation skipped for Plotly charts. Use chat to ask questions about the data.")
                    elif is_mismatch:
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
    render_chat()
    render_main()


if __name__ == "__main__":
    main()
