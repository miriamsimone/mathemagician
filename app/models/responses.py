"""Response models"""
from pydantic import BaseModel, Field
from typing import Optional
from enum import Enum


class JobStatus(str, Enum):
    """Job status enumeration"""
    QUEUED = "queued"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class GenerateResponse(BaseModel):
    """Response from generate endpoint"""
    job_id: str = Field(..., description="Unique job identifier")
    status: JobStatus = Field(..., description="Current job status")
    message: str = Field(..., description="Human-readable message")

    class Config:
        json_schema_extra = {
            "example": {
                "job_id": "abc123-def456-ghi789",
                "status": "queued",
                "message": "Job queued successfully. Use /status/{job_id} to check progress."
            }
        }


class StatusResponse(BaseModel):
    """Response from status endpoint"""
    job_id: str = Field(..., description="Unique job identifier")
    status: JobStatus = Field(..., description="Current job status")
    message: str = Field(..., description="Human-readable status message")
    video_url: Optional[str] = Field(None, description="Signed URL to download video (if completed)")
    thumbnail_url: Optional[str] = Field(None, description="Signed URL to download thumbnail (if completed)")
    error: Optional[str] = Field(None, description="Error message (if failed)")
    created_at: Optional[str] = Field(None, description="Job creation timestamp")
    completed_at: Optional[str] = Field(None, description="Job completion timestamp")

    class Config:
        json_schema_extra = {
            "example": {
                "job_id": "abc123-def456-ghi789",
                "status": "completed",
                "message": "Rendering completed successfully",
                "video_url": "https://storage.googleapis.com/...",
                "thumbnail_url": "https://storage.googleapis.com/...",
                "created_at": "2024-01-01T12:00:00Z",
                "completed_at": "2024-01-01T12:01:30Z"
            }
        }


class HealthResponse(BaseModel):
    """Response from health check endpoint"""
    status: str = Field(..., description="Health status")
    version: str = Field(..., description="API version")
    environment: str = Field(..., description="Current environment")
