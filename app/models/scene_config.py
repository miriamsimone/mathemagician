"""Scene configuration models"""
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any


class SceneConfig(BaseModel):
    """Configuration for a Manim scene"""
    scene_type: str = Field(..., description="Type of scene (e.g., 'function_graph', 'geometric', 'vector')")
    parameters: Dict[str, Any] = Field(..., description="Scene-specific parameters")

    class Config:
        json_schema_extra = {
            "example": {
                "scene_type": "function_graph",
                "parameters": {
                    "function": "sin(x)",
                    "x_range": [-5, 5],
                    "y_range": [-2, 2],
                    "color": "#58C4DD",
                    "show_grid": True
                }
            }
        }


class FunctionGraphConfig(BaseModel):
    """Configuration for function graph scene"""
    function: str = Field(..., description="Mathematical function string")
    x_range: List[float] = Field(..., description="X-axis range [min, max]")
    y_range: Optional[List[float]] = Field(None, description="Y-axis range (auto if None)")
    color: str = Field("#58C4DD", description="Line color (hex)")
    show_grid: bool = Field(True, description="Show grid background")
    show_labels: bool = Field(True, description="Show axis labels")
    label_text: Optional[str] = Field(None, description="Custom function label")
