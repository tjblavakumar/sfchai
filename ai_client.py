"""
SF CHAI - AI Client Module
Handles AWS Bedrock (Claude) and OpenAI (GPT-4o) API calls.
"""

import base64
import json
import os
from pathlib import Path
from typing import Optional

import boto3
from botocore.config import Config
from openai import OpenAI
from PIL import Image
import io
import pandas as pd


# ============================================================================
# Configuration
# ============================================================================

def get_aws_config() -> dict:
    """Get AWS configuration from environment variables."""
    return {
        "aws_access_key_id": os.environ.get("AWS_ACCESS_KEY_ID", ""),
        "aws_secret_access_key": os.environ.get("AWS_SECRET_ACCESS_KEY", ""),
        "aws_session_token": os.environ.get("AWS_SESSION_TOKEN", ""),
        "aws_region": os.environ.get("AWS_REGION", "us-east-1"),
    }


def get_openai_config() -> dict:
    """Get OpenAI configuration from environment variables."""
    return {
        "api_key": os.environ.get("OPENAI_API_KEY", ""),
    }


# ============================================================================
# Image Encoding
# ============================================================================

def encode_image_to_base64(image: Image.Image, format: str = "PNG") -> str:
    """
    Encode a PIL Image to base64 string.
    
    Args:
        image: PIL Image object
        format: Image format (PNG, JPEG, etc.)
        
    Returns:
        Base64 encoded string
    """
    buffered = io.BytesIO()
    image.save(buffered, format=format)
    img_bytes = buffered.getvalue()
    return base64.b64encode(img_bytes).decode("utf-8")


def encode_image_file_to_base64(image_path: Path) -> str:
    """
    Encode an image file to base64 string.
    
    Args:
        image_path: Path to the image file
        
    Returns:
        Base64 encoded string
    """
    with Image.open(image_path) as img:
        # Determine format from extension
        ext = image_path.suffix.lower()
        img_format = "JPEG" if ext in [".jpg", ".jpeg"] else "PNG"
        return encode_image_to_base64(img, img_format)


# ============================================================================
# AWS Bedrock Client
# ============================================================================

class BedrockClient:
    """AWS Bedrock client for Claude vision models."""
    
    def __init__(self, config: dict):
        """
        Initialize Bedrock client.
        
        Args:
            config: AWS configuration dict
        """
        self.config = config
        # Use default credential chain if no explicit credentials
        if config["aws_access_key_id"] and config["aws_secret_access_key"]:
            kwargs = {
                "aws_access_key_id": config["aws_access_key_id"],
                "aws_secret_access_key": config["aws_secret_access_key"],
                "region_name": config["aws_region"],
            }
            if config.get("aws_session_token"):
                kwargs["aws_session_token"] = config["aws_session_token"]
        else:
            # Use default credential chain (SSO, instance profile, etc.)
            kwargs = {"region_name": config["aws_region"]}
        
        kwargs["config"] = Config(connect_timeout=30, read_timeout=60)
        self.client = boto3.client("bedrock-runtime", **kwargs)
    
    def analyze_image(
        self,
        image_base64: str,
        prompt: str,
        model_id: str = "us.anthropic.claude-3-5-sonnet-20241022-v2:0"
    ) -> dict:
        """
        Analyze an image using Claude vision model.
        
        Args:
            image_base64: Base64 encoded image
            prompt: Text prompt for analysis
            model_id: Bedrock model ID
            
        Returns:
            Parsed JSON response
        """
        # Claude 3.5 Sonnet vision payload
        payload = {
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 4000,
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image",
                            "source": {
                                "type": "base64",
                                "media_type": "image/png",
                                "data": image_base64
                            }
                        },
                        {
                            "type": "text",
                            "text": prompt
                        }
                    ]
                }
            ]
        }
        
        # Invoke model
        response = self.client.invoke_model(
            modelId=model_id,
            body=json.dumps(payload),
            accept="application/json",
            contentType="application/json"
        )
        
        # Parse response
        response_body = json.loads(response["body"].read())
        
        # Extract text content
        text_content = ""
        for content_block in response_body.get("content", []):
            if content_block.get("type") == "text":
                text_content = content_block.get("text", "")
                break
        
        # Try to parse as JSON
        try:
            return json.loads(text_content)
        except json.JSONDecodeError:
            # Try to extract JSON from markdown code blocks
            import re
            json_match = re.search(r'```(?:json)?\s*(\{[\s\S]*?\})\s*```', text_content)
            if json_match:
                try:
                    return json.loads(json_match.group(1))
                except json.JSONDecodeError:
                    pass
            
            # Try to find JSON object in text
            json_match = re.search(r'(\{[\s\S]*\})', text_content)
            if json_match:
                try:
                    return json.loads(json_match.group(1))
                except json.JSONDecodeError:
                    pass
            
            # Return as raw text if not JSON
            return {"raw_text": text_content, "error": "Response was not valid JSON"}
    
    def generate_text(
        self,
        prompt: str,
        system_prompt: str = "",
        model_id: str = "us.anthropic.claude-3-5-sonnet-20241022-v2:0",
        temperature: float = 0.7,
        max_tokens: int = 4000
    ) -> str:
        """
        Generate text using Claude model.
        
        Args:
            prompt: User prompt
            system_prompt: System prompt
            model_id: Bedrock model ID
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            
        Returns:
            Generated text
        """
        messages = [{"role": "user", "content": prompt}]
        
        payload = {
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": max_tokens,
            "temperature": temperature,
            "messages": messages
        }
        
        # Add system prompt if provided
        if system_prompt:
            payload["system"] = system_prompt
        
        response = self.client.invoke_model(
            modelId=model_id,
            body=json.dumps(payload),
            accept="application/json",
            contentType="application/json"
        )
        
        response_body = json.loads(response["body"].read())
        
        # Extract text
        text_content = ""
        for content_block in response_body.get("content", []):
            if content_block.get("type") == "text":
                text_content = content_block.get("text", "")
                break
        
        return text_content


# ============================================================================
# OpenAI Client
# ============================================================================

class OpenAIClient:
    """OpenAI client for GPT-4o vision models."""
    
    def __init__(self, config: dict):
        """
        Initialize OpenAI client.
        
        Args:
            config: OpenAI configuration dict
        """
        self.client = OpenAI(api_key=config["api_key"])
    
    def analyze_image(
        self,
        image_base64: str,
        prompt: str,
        model: str = "gpt-4o"
    ) -> dict:
        """
        Analyze an image using GPT-4o vision model.
        
        Args:
            image_base64: Base64 encoded image
            prompt: Text prompt for analysis
            model: OpenAI model name
            
        Returns:
            Parsed JSON response
        """
        response = self.client.chat.completions.create(
            model=model,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/png;base64,{image_base64}"
                            }
                        },
                        {
                            "type": "text",
                            "text": prompt
                        }
                    ]
                }
            ],
            max_tokens=4000,
            response_format={"type": "json_object"}
        )
        
        # Extract content
        content = response.choices[0].message.content
        
        # Parse as JSON
        try:
            return json.loads(content)
        except json.JSONDecodeError:
            return {"raw_text": content, "error": "Response was not valid JSON"}
    
    def generate_text(
        self,
        prompt: str,
        system_prompt: str = "",
        model: str = "gpt-4o",
        temperature: float = 0.7,
        max_tokens: int = 4000
    ) -> str:
        """
        Generate text using GPT-4o model.
        
        Args:
            prompt: User prompt
            system_prompt: System prompt
            model: OpenAI model name
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            
        Returns:
            Generated text
        """
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        
        response = self.client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            response_format={"type": "text"}
        )
        
        return response.choices[0].message.content


# ============================================================================
# Factory Function
# ============================================================================

def get_ai_client(provider: str = "bedrock"):
    """
    Get the appropriate AI client based on provider.
    
    Args:
        provider: "bedrock" or "openai"
        
    Returns:
        BedrockClient or OpenAIClient instance
        
    Raises:
        ValueError: If provider is invalid or credentials missing
    """
    if provider == "bedrock":
        config = get_aws_config()
        # Allow empty credentials to use default credential chain (SSO)
        return BedrockClient(config)
    elif provider == "openai":
        config = get_openai_config()
        if not config["api_key"]:
            raise ValueError("OpenAI API key not configured. Set OPENAI_API_KEY in .env")
        return OpenAIClient(config)
    else:
        raise ValueError(f"Unknown AI provider: {provider}")


# ============================================================================
# Vision Analysis Prompt
# ============================================================================

VISION_ANALYSIS_PROMPT = """Analyze this chart image and return a JSON description. Respond with ONLY valid JSON - no markdown, no explanations.

Extract these elements:
1. chart_type: line, bar, stacked_bar, pie, scatter, area
2. title: Chart title (null if none)
3. x_axis: Type (category/value/time), label, font size
4. y_axis: Type, label, font size
5. legend: 
   - "inline": Labels at line ends (no legend box)
   - "box": Separate legend box with position
6. series: Array with name, type, color (hex), smooth (true/false), line_width
7. colors: Array of hex colors in order
8. grid: Grid visibility
9. annotations:
   - horizontal_lines: [{value, label, color, style}] for horizontal reference lines
   - vertical_lines: [{value, label, color, style}] for vertical reference lines
   - bands: [{start, end, label, color}] for shaded regions
10. tooltips: Tooltip config
11. data_labels: Boolean
12. font_sizes: {axis_label, axis_title, legend}

IMPORTANT: Look carefully for:
- Text labels at line ends = "inline" legend
- Separate box with series names = "box" legend
- Horizontal/vertical lines that aren't data = annotations
- Exact colors of each series

Return ONLY this JSON (no code blocks):
{
  "chart_type": "line",
  "title": null,
  "x_axis": {"type": "time", "name": null, "font_size": 11},
  "y_axis": {"type": "value", "name": null, "font_size": 11},
  "legend": {"type": "inline", "position": "right"},
  "series": [
    {"name": "Series1", "type": "line", "color": "#1f77b4", "smooth": true, "line_width": 2}
  ],
  "colors": ["#1f77b4", "#ff7f0e"],
  "grid": {"show": true},
  "annotations": {
    "horizontal_lines": [{"value": 2.0, "label": "Target", "color": "#000000", "style": "dashed"}],
    "vertical_lines": [],
    "bands": []
  },
  "tooltips": {"trigger": "axis"},
  "data_labels": false,
  "font_sizes": {"axis_label": 11, "axis_title": 13, "legend": 12}
}
"""


def analyze_chart_image(client, image_base64: str) -> dict:
    """
    Analyze a chart image using the AI client.
    
    Args:
        client: AI client (BedrockClient or OpenAIClient)
        image_base64: Base64 encoded image
        
    Returns:
        Chart analysis as dict
    """
    result = client.analyze_image(
        image_base64=image_base64,
        prompt=VISION_ANALYSIS_PROMPT
    )
    
    # If result has error, try to extract JSON from raw_text
    if isinstance(result, dict) and result.get("error") == "Response was not valid JSON":
        raw_text = result.get("raw_text", "")
        
        # Try to extract JSON from markdown code blocks
        import re
        json_match = re.search(r'```(?:json)?\s*(\{[\s\S]*?\})\s*```', raw_text)
        if json_match:
            try:
                return json.loads(json_match.group(1))
            except json.JSONDecodeError:
                pass
        
        # Try to find JSON object in text
        json_match = re.search(r'(\{[\s\S]*\})', raw_text)
        if json_match:
            try:
                return json.loads(json_match.group(1))
            except json.JSONDecodeError:
                pass
        
        # Create a basic fallback analysis
        fallback = {
            "chart_type": "line",
            "title": None,
            "x_axis": {"type": "time", "name": None, "font_size": 11},
            "y_axis": {"type": "value", "name": None, "font_size": 11},
            "legend": {"type": "inline", "position": "right"},
            "series": [
                {"name": "Series 1", "type": "line", "color": "#1f77b4", "smooth": True, "line_width": 2},
                {"name": "Series 2", "type": "line", "color": "#ff7f0e", "smooth": True, "line_width": 2}
            ],
            "colors": ["#1f77b4", "#ff7f0e"],
            "grid": {"show": True},
            "annotations": {
                "horizontal_lines": [],
                "vertical_lines": [],
                "bands": []
            },
            "tooltips": {"trigger": "axis"},
            "data_labels": False,
            "font_sizes": {"axis_label": 11, "axis_title": 13, "legend": 12},
            "_fallback": True,
            "_note": "Using fallback analysis - AI response could not be parsed"
        }
        
        # Return error with fallback
        return {
            "error": "Could not parse JSON from response - using fallback analysis",
            "raw_text": raw_text[:500] if len(raw_text) > 500 else raw_text,
            "fallback_analysis": fallback
        }
    
    return result


# ============================================================================
# Chart Generation Prompt
# ============================================================================

CHART_GENERATION_PROMPT = """Generate an ECharts v5 option JSON that matches the reference chart using the CSV data.

Reference Chart Analysis:
{analysis_json}

CSV Data:
{csv_info}

CRITICAL Requirements:
1. Include ALL series from CSV
2. Use exact colors from reference
3. Set smooth:true and smoothMonotone:"x" for line charts
4. Legend type:
   - "inline" → add endLabel to each series with distance:10, NO legend component
   - "box" → add legend component, NO endLabel
5. Annotations (IMPORTANT - correct placement):
   - horizontal_lines → Add to series[0].markLine.data with yAxis
   - vertical_lines → Add to series[0].markLine.data with xAxis
   - bands → Add to series[0].markArea.data
6. Grid margins: left:"8%", right:"25%", top:"8%", bottom:"8%"
7. Include ALL data points (don't truncate)

Return ONLY valid JSON (no markdown, no code blocks):
{{
  "tooltip": {{"trigger": "axis"}},
  "toolbox": {{"feature": {{"saveAsImage": {{}}}}}},
  "xAxis": {{
    "type": "category",
    "data": [/* ALL dates */],
    "boundaryGap": false
  }},
  "yAxis": {{"type": "value"}},
  "series": [
    {{
      "name": "Series1",
      "type": "line",
      "data": [/* ALL values */],
      "smooth": true,
      "smoothMonotone": "x",
      "itemStyle": {{"color": "#5470c6"}},
      "endLabel": {{"show": true, "formatter": "{{{{a}}}}", "fontSize": 12, "distance": 10}},
      "markLine": {{
        "data": [
          {{"yAxis": 2.0, "label": {{"formatter": "2%"}}, "lineStyle": {{"type": "dashed", "color": "#000000"}}}},
          {{"xAxis": "2020-01-01", "lineStyle": {{"color": "#cccccc", "type": "solid"}}}}
        ]
      }}
    }}
  ],
  "grid": {{"left": "8%", "right": "25%", "top": "8%", "bottom": "8%"}}
}}
"""


def generate_chart_json(client, analysis: dict, csv_data, csv_info: str) -> dict:
    """
    Generate ECharts JSON from vision analysis and CSV data.
    
    Args:
        client: AI client (BedrockClient or OpenAIClient)
        analysis: Vision analysis result from analyze_chart_image()
        csv_data: pandas DataFrame with CSV data
        csv_info: String with CSV column info
        
    Returns:
        ECharts option JSON or mismatch object
    """
    try:
        # Pivot data if in long format
        if 'key' in csv_data.columns and 'value' in csv_data.columns:
            csv_data = csv_data.pivot(index='date', columns='key', values='value').reset_index()
        
        # Format the prompt with analysis and CSV info
        prompt = CHART_GENERATION_PROMPT.format(
            analysis_json=json.dumps(analysis),
            csv_info=csv_info
        )
        
        # Generate chart JSON using text-only model
        result = client.generate_text(prompt=prompt)
        
        # Try to parse the result as JSON
        try:
            chart_json = json.loads(result)
            return chart_json
        except json.JSONDecodeError:
            pass
        
        # Try to extract JSON from response
        import re
        json_match = re.search(r'```(?:json)?\s*(\{[\s\S]*?\})\s*```', result)
        if json_match:
            try:
                chart_json = json.loads(json_match.group(1))
                return chart_json
            except (json.JSONDecodeError, IndexError):
                pass
        
        # Try without code blocks
        json_match = re.search(r'(\{[\s\S]*\})', result)
        if json_match:
            try:
                chart_json = json.loads(json_match.group(1))
                return chart_json
            except (json.JSONDecodeError, IndexError):
                pass
        
        # Fallback chart
        try:
            fallback_chart = create_fallback_chart(analysis, csv_data)
            if fallback_chart:
                return fallback_chart
        except Exception as fallback_error:
            pass
        
        return {
            "mismatch": True,
            "reason": f"AI returned non-JSON response.",
            "clarifying_questions": ["Try uploading a simpler reference chart."],
            "raw_response": result[:1000] if len(result) > 1000 else result
        }
    except Exception as e:
        return {
            "mismatch": True,
            "reason": f"Error generating chart: {str(e)}",
            "clarifying_questions": ["Check your data format and try again."],
            "raw_response": ""
        }


def create_fallback_chart(analysis: dict, csv_data) -> dict:
    """
    Create a simple fallback chart when AI fails to generate proper JSON.
    
    Args:
        analysis: Vision analysis result
        csv_data: pandas DataFrame
        
    Returns:
        Simple ECharts option JSON or None
    """
    if csv_data is None or len(csv_data) == 0:
        return None
    
    # Check if data is in long format and pivot
    if 'key' in csv_data.columns and 'value' in csv_data.columns:
        csv_data = csv_data.pivot(index='date', columns='key', values='value').reset_index()
    
    # Get chart type from analysis
    chart_type = analysis.get("chart_type", "line")
    if chart_type not in ["line", "bar", "stacked_bar"]:
        chart_type = "line"
    
    # Get column names
    columns = list(csv_data.columns)
    if len(columns) < 2:
        return None
    
    # First column is typically x-axis
    x_col = columns[0]
    x_data = csv_data[x_col].tolist()
    
    # Get colors from analysis or use defaults
    colors = analysis.get("colors", ["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728", "#9467bd"])
    
    # Get legend type from analysis
    legend_info = analysis.get("legend", {})
    use_inline_labels = legend_info.get("type") == "inline" if isinstance(legend_info, dict) else True
    
    # Get annotations from analysis
    annotations = analysis.get("annotations", {})
    horizontal_lines = annotations.get("horizontal_lines", []) if isinstance(annotations, dict) else []
    
    # Other columns are series
    series = []
    for i, col in enumerate(columns[1:]):
        if pd.api.types.is_numeric_dtype(csv_data[col]):
            series_config = {
                "name": col,
                "type": "bar" if chart_type == "bar" else "line",
                "data": csv_data[col].tolist(),
                "itemStyle": {"color": colors[i % len(colors)]},
                "lineStyle": {"width": 2},
                "smooth": True,
                "smoothMonotone": "x"
            }
            # Add endLabel for line charts if using inline labels
            if chart_type == "line" and use_inline_labels:
                series_config["endLabel"] = {
                    "show": True,
                    "formatter": "{a}",
                    "fontSize": 12,
                    "distance": 5
                }
            # Add markLine to first series if horizontal lines exist
            if i == 0 and horizontal_lines:
                mark_data = []
                for hline in horizontal_lines:
                    mark_data.append({
                        "yAxis": hline.get("value"),
                        "name": hline.get("label", ""),
                        "lineStyle": {
                            "color": hline.get("color", "#ff0000"),
                            "type": hline.get("style", "dashed"),
                            "width": 2
                        },
                        "label": {
                            "show": True,
                            "position": "end",
                            "formatter": "{b}: {c}"
                        }
                    })
                series_config["markLine"] = {
                    "silent": True,
                    "data": mark_data
                }
            series.append(series_config)
    
    # Build chart
    chart = {
        "tooltip": {
            "trigger": "axis",
            "axisPointer": {"type": "line"}
        },
        "toolbox": {
            "feature": {
                "saveAsImage": {"title": "Save as PNG"}
            }
        },
        "xAxis": {
            "type": "category",
            "data": x_data,
            "boundaryGap": False,
            "axisLabel": {"fontSize": 11}
        },
        "yAxis": {
            "type": "value",
            "axisLabel": {"fontSize": 11}
        },
        "series": series,
        "grid": {
            "left": "8%",
            "right": "22%" if use_inline_labels else "8%",
            "top": "8%",
            "bottom": "8%",
            "containLabel": True
        }
    }
    
    # Add legend box if not using inline labels
    if not use_inline_labels:
        chart["legend"] = {
            "data": [s["name"] for s in series],
            "top": "5%",
            "right": "5%"
        }
    
    return chart


# ============================================================================
# Executive Summary Generation
# ============================================================================

SUMMARY_PROMPT = """You are a professional business analyst. Write a 300-450 word executive summary based on the data and chart analysis.

## CSV Data Summary:
{csv_info}

## Chart Analysis:
{chart_analysis}

## Generated Chart Configuration:
{chart_config}

## Your Task:
Write a professional executive summary that includes:
1. **Key Insights**: Main trends and patterns in the data
2. **Data Highlights**: Notable numbers, peaks, valleys, averages
3. **Anomalies**: Any unusual patterns or outliers
4. **Recommendations**: Actionable suggestions based on the data

## Style Guidelines:
- Professional business tone
- Concise sentences
- Use specific numbers from the data
- Avoid jargon
- 300-450 words
- No bullet points, flowing prose
- End with actionable recommendation

Write the executive summary now:
"""


def generate_summary(client, csv_data, chart_analysis: dict, chart_config: dict) -> str:
    """
    Generate an executive summary from data and chart analysis.
    
    Args:
        client: AI client (BedrockClient or OpenAIClient)
        csv_data: pandas DataFrame with CSV data
        chart_analysis: Vision analysis result
        chart_config: Generated ECharts configuration
        
    Returns:
        Executive summary text
    """
    # Get CSV info
    csv_info = _get_csv_info_for_summary(csv_data)
    
    # Format the prompt
    prompt = SUMMARY_PROMPT.format(
        csv_info=csv_info,
        chart_analysis=json.dumps(chart_analysis) if chart_analysis else "None",
        chart_config=json.dumps(chart_config) if chart_config else "None"
    )
    
    # Generate summary
    result = client.generate_text(
        prompt=prompt,
        temperature=0.5,  # Lower temperature for more focused output
        max_tokens=1000
    )
    
    return result.strip()


def _get_csv_info_for_summary(df) -> str:
    """Get CSV info for summary generation."""
    if df is None:
        return "No data"
    
    info = f"Dataset: {df.shape[0]} rows, {df.shape[1]} columns\n"
    
    # Basic stats for numeric columns
    numeric_cols = df.select_dtypes(include=['number']).columns
    for col in numeric_cols:
        info += f"- {col}: min={df[col].min():.2f}, max={df[col].max():.2f}, mean={df[col].mean():.2f}\n"
    
    # Sample of categorical data
    cat_cols = df.select_dtypes(include=['object']).columns
    for col in cat_cols:
        top_values = df[col].value_counts().head(3)
        info += f"- {col}: {dict(top_values)}\n"
    
    return info


# ============================================================================
# Chat Interface
# ============================================================================

CHAT_SYSTEM_PROMPT = """You are a chart customization assistant. Help users modify their ECharts visualization.

Context:
- CSV Data: {csv_info}
- Chart Analysis: {chart_analysis}
- Current Chart: {chart_config}

Actions you can take:

1. Regenerate Summary:
{{"action": "regenerate_summary"}}

2. Modify Chart:
{{"action": "modify_chart", "changes": {{...}}}}

3. Answer Questions:
{{"action": "text", "response": "..."}}

Common Modifications:

Colors: series[0].itemStyle.color = "#ff0000"
Fonts: xAxis.axisLabel.fontSize = 14
Legend: legend.position = "bottom"

Annotations:
- Vertical line: series[0].markLine.data = [{{"xAxis": "2020-01-01"}}]
- Horizontal line: series[0].markLine.data = [{{"yAxis": 2.0}}]
- Shaded band: series[0].markArea.data = [[{{"xAxis": "2020-03"}}, {{"xAxis": "2020-10"}}]]

IMPORTANT:
- markLine = single line (vertical or horizontal)
- markArea = shaded region/band
- "Add vertical line at 2020" → use markLine with xAxis
- "Add band from 2020 to 2021" → use markArea

User: {user_message}

Respond with JSON only:
"""


def process_chat_message(client, user_message: str, csv_data, chart_analysis: dict, chart_config: dict, summary: str) -> dict:
    """
    Process a chat message and return a response.
    
    Args:
        client: AI client
        user_message: User's chat message
        csv_data: pandas DataFrame
        chart_analysis: Vision analysis result
        chart_config: Current ECharts config
        summary: Current executive summary
        
    Returns:
        Dict with response and optional chart changes
    """
    # Get CSV info
    csv_info = _get_csv_info_for_summary(csv_data)
    
    # Format the prompt
    prompt = CHAT_SYSTEM_PROMPT.format(
        csv_info=csv_info,
        chart_analysis=json.dumps(chart_analysis) if chart_analysis else "None",
        chart_config=json.dumps(chart_config) if chart_config else "None",
        summary=summary if summary else "None",
        user_message=user_message
    )
    
    # Generate response
    result = client.generate_text(
        prompt=prompt,
        temperature=0.7,
        max_tokens=2000
    )
    
    # Try to parse as JSON (for chart modifications)
    try:
        response_data = json.loads(result)
        if isinstance(response_data, dict) and "action" in response_data:
            return response_data
    except json.JSONDecodeError:
        pass
    
    # Try to extract JSON from markdown code blocks
    import re
    json_match = re.search(r'```(?:json)?\s*(\{[\s\S]*?\})\s*```', result)
    if json_match:
        try:
            response_data = json.loads(json_match.group(1))
            if isinstance(response_data, dict) and "action" in response_data:
                return response_data
        except json.JSONDecodeError:
            pass
    
    # Return as text response
    return {
        "action": "text",
        "response": result
    }
