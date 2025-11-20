"""Claude API service for natural language interpretation"""
import json
import logging
from typing import Dict, Any, Optional
from anthropic import Anthropic
from app.config import settings

logger = logging.getLogger(__name__)


class ClaudeService:
    """Service for interpreting natural language into visualization parameters"""

    def __init__(self):
        self.client = None
        if settings.anthropic_api_key and settings.anthropic_api_key != "sk-ant-placeholder":
            try:
                self.client = Anthropic(api_key=settings.anthropic_api_key)
                logger.info("Claude API client initialized")
            except Exception as e:
                logger.warning(f"Failed to initialize Claude API: {e}")

    def is_available(self) -> bool:
        """Check if Claude API is available"""
        return self.client is not None

    async def interpret_description(self, description: str) -> Dict[str, Any]:
        """
        Interpret a natural language description into visualization parameters

        Args:
            description: Natural language description of desired visualization

        Returns:
            Dictionary with function, x_range, and optional styling parameters
        """
        if not self.is_available():
            raise ValueError("Claude API is not configured. Please set ANTHROPIC_API_KEY in .env")

        system_prompt = """You are a math visualization assistant. Convert natural language descriptions into JSON parameters for creating mathematical visualizations.

Your output must be valid JSON with these fields:

For FUNCTION GRAPHS:
- scene_type: "function_graph"
- function: Mathematical function as a string (use Python syntax: **, sin, cos, tan, exp, log, sqrt, etc.)
- x_range: Array of two numbers [min, max] for the x-axis range
- color: (optional) Color name or hex code (default: BLUE)
- label: (optional) Custom label for the function
- show_axis_labels: (optional) Boolean (default: true)
- show_tick_marks: (optional) Boolean (default: true)
- background_color: (optional) Color or "transparent" (default: "transparent")

For BAR CHARTS:
- scene_type: "bar_chart"
- categories: Array of category names (strings)
- values: Array of numbers (percentages or absolute values)
- color: (optional) Bar color (default: BLUE)
- title: (optional) Chart title
- background_color: (optional) Color or "transparent" (default: "transparent")

For 3D SURFACE PLOTS:
- scene_type: "surface_plot"
- function: Mathematical function z=f(x,y) as a string (use Python syntax)
- x_range: Array of two numbers [min, max] for x-axis
- y_range: Array of two numbers [min, max] for y-axis
- color: (optional) Surface color (default: BLUE)
- title: (optional) Surface title
- background_color: (optional) Color or "transparent" (default: "transparent")

Examples:
Input: "Show me a sine wave"
Output: {"scene_type": "function_graph", "function": "sin(x)", "x_range": [-6.28, 6.28], "label": "sin(x)"}

Input: "bar chart with three bars, animal vegetable mineral and they're set to 40% 40% 20%"
Output: {"scene_type": "bar_chart", "categories": ["Animal", "Vegetable", "Mineral"], "values": [40, 40, 20]}

Input: "A red cosine wave"
Output: {"scene_type": "function_graph", "function": "cos(x)", "x_range": [-6.28, 6.28], "color": "RED", "label": "cos(x)"}

Input: "bar chart showing sales with title Sales Report: Q1 100, Q2 150, Q3 200, Q4 180"
Output: {"scene_type": "bar_chart", "categories": ["Q1", "Q2", "Q3", "Q4"], "values": [100, 150, 200, 180], "title": "Sales Report"}

Input: "sine wave with clean axes"
Output: {"scene_type": "function_graph", "function": "sin(x)", "x_range": [-6.28, 6.28], "label": "sin(x)", "show_tick_marks": false}

Input: "bar chart with red background: apples 50, oranges 30"
Output: {"scene_type": "bar_chart", "categories": ["Apples", "Oranges"], "values": [50, 30], "background_color": "RED"}

Input: "3D ripple surface with title Ripple Effect"
Output: {"scene_type": "surface_plot", "function": "sin(sqrt(x**2 + y**2))", "x_range": [-5, 5], "y_range": [-5, 5], "title": "Ripple Effect"}

Input: "saddle surface"
Output: {"scene_type": "surface_plot", "function": "x**2 - y**2", "x_range": [-3, 3], "y_range": [-3, 3]}

Input: "3D surface of z = x squared minus y squared"
Output: {"scene_type": "surface_plot", "function": "x**2 - y**2", "x_range": [-3, 3], "y_range": [-3, 3]}

Only output valid JSON, nothing else."""

        try:
            response = self.client.messages.create(
                model="claude-3-haiku-20240307",
                max_tokens=500,
                system=system_prompt,
                messages=[{
                    "role": "user",
                    "content": description
                }]
            )

            # Extract the text content
            result_text = response.content[0].text.strip()

            # Parse JSON response
            try:
                params = json.loads(result_text)
                logger.info(f"Interpreted '{description}' as: {params}")
                return params
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse Claude response as JSON: {result_text}")
                raise ValueError(f"Failed to interpret description: {e}")

        except Exception as e:
            logger.error(f"Claude API error: {e}")
            raise ValueError(f"Failed to interpret description: {str(e)}")

    async def interpret_edit(self, original_params: Dict[str, Any], edit_description: str) -> Dict[str, Any]:
        """
        Interpret an edit description and apply it to existing parameters

        Args:
            original_params: Original visualization parameters
            edit_description: Natural language description of desired changes

        Returns:
            Updated parameters dictionary
        """
        if not self.is_available():
            raise ValueError("Claude API is not configured. Please set ANTHROPIC_API_KEY in .env")

        system_prompt = """You are a math visualization assistant. Given existing visualization parameters and a natural language edit request, output the updated parameters as JSON.

Your output must be valid JSON preserving the scene_type and updating the relevant fields.

For FUNCTION GRAPHS (scene_type: "function_graph"):
- function, x_range, color, label, show_axis_labels, show_tick_marks, background_color

For BAR CHARTS (scene_type: "bar_chart"):
- categories, values, color, title, background_color

For 3D SURFACE PLOTS (scene_type: "surface_plot"):
- function, x_range, y_range, color, title, background_color

Examples:
Original: {"scene_type": "function_graph", "function": "sin(x)", "x_range": [-6.28, 6.28]}
Edit: "Make it blue"
Output: {"scene_type": "function_graph", "function": "sin(x)", "x_range": [-6.28, 6.28], "color": "BLUE"}

Original: {"scene_type": "bar_chart", "categories": ["A", "B", "C"], "values": [10, 20, 30]}
Edit: "Change values to 50, 60, 70"
Output: {"scene_type": "bar_chart", "categories": ["A", "B", "C"], "values": [50, 60, 70]}

Original: {"scene_type": "bar_chart", "categories": ["Animal", "Vegetable", "Mineral"], "values": [40, 40, 20]}
Edit: "Make the background red"
Output: {"scene_type": "bar_chart", "categories": ["Animal", "Vegetable", "Mineral"], "values": [40, 40, 20], "background_color": "RED"}

Original: {"scene_type": "function_graph", "function": "sin(x)", "x_range": [-6.28, 6.28]}
Edit: "Remove the axis labels"
Output: {"scene_type": "function_graph", "function": "sin(x)", "x_range": [-6.28, 6.28], "show_axis_labels": false}

Original: {"scene_type": "bar_chart", "categories": ["Q1", "Q2"], "values": [100, 150], "background_color": "RED"}
Edit: "Make background transparent"
Output: {"scene_type": "bar_chart", "categories": ["Q1", "Q2"], "values": [100, 150], "background_color": "transparent"}

Original: {"scene_type": "surface_plot", "function": "sin(sqrt(x**2 + y**2))", "x_range": [-5, 5], "y_range": [-5, 5]}
Edit: "Change to saddle surface"
Output: {"scene_type": "surface_plot", "function": "x**2 - y**2", "x_range": [-5, 5], "y_range": [-5, 5]}

Original: {"scene_type": "surface_plot", "function": "x**2 - y**2", "x_range": [-3, 3], "y_range": [-3, 3]}
Edit: "Make the range bigger, -5 to 5"
Output: {"scene_type": "surface_plot", "function": "x**2 - y**2", "x_range": [-5, 5], "y_range": [-5, 5]}

Only output valid JSON, nothing else."""

        try:
            response = self.client.messages.create(
                model="claude-3-haiku-20240307",
                max_tokens=500,
                system=system_prompt,
                messages=[{
                    "role": "user",
                    "content": f"Original parameters: {json.dumps(original_params)}\n\nEdit request: {edit_description}"
                }]
            )

            # Extract the text content
            result_text = response.content[0].text.strip()

            # Parse JSON response
            try:
                params = json.loads(result_text)
                logger.info(f"Applied edit '{edit_description}' to get: {params}")
                return params
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse Claude response as JSON: {result_text}")
                raise ValueError(f"Failed to interpret edit: {e}")

        except Exception as e:
            logger.error(f"Claude API error: {e}")
            raise ValueError(f"Failed to interpret edit: {str(e)}")


# Singleton instance
claude_service = ClaudeService()
