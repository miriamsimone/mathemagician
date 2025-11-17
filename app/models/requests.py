"""Request models"""
from pydantic import BaseModel, Field
from typing import List, Optional


class GenerateRequest(BaseModel):
    """Request to generate a visualization"""
    function: str = Field(..., description="Mathematical function to visualize (e.g., 'sin(x)', 'x**2')")
    x_range: List[float] = Field(..., description="X-axis range [min, max]", min_length=2, max_length=2)
    y_range: Optional[List[float]] = Field(None, description="Y-axis range [min, max] (auto if not provided)", min_length=2, max_length=2)

    class Config:
        json_schema_extra = {
            "example": {
                "function": "sin(x)",
                "x_range": [-5, 5]
            }
        }


class EditRequest(BaseModel):
    """Request to edit an existing visualization"""
    job_id: str = Field(..., description="Original job ID to edit")
    edit_description: str = Field(..., description="Natural language description of the edit")

    class Config:
        json_schema_extra = {
            "example": {
                "job_id": "abc123",
                "edit_description": "Change the color to blue and extend x range to -10 to 10"
            }
        }
