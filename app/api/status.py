"""Status endpoint"""
import logging
from fastapi import APIRouter, HTTPException
from app.models.responses import StatusResponse, JobStatus
from app.services.job_queue import job_queue

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/status/{job_id}", response_model=StatusResponse)
async def get_job_status(job_id: str):
    """
    Get status of a visualization job

    Args:
        job_id: Unique job identifier

    Returns:
        Current job status and results if available
    """
    try:
        # Get job from queue
        job = job_queue.get_job(job_id)

        if not job:
            raise HTTPException(
                status_code=404,
                detail=f"Job {job_id} not found"
            )

        # Build response
        response = StatusResponse(
            job_id=job_id,
            status=job["status"],
            message=_get_status_message(job["status"]),
            created_at=job.get("created_at"),
            completed_at=job.get("completed_at")
        )

        # Add URLs if completed
        if job["status"] == JobStatus.COMPLETED:
            response.video_url = job.get("video_url")
            response.thumbnail_url = job.get("thumbnail_url")

        # Add error if failed
        if job["status"] == JobStatus.FAILED:
            response.error = job.get("error", "Unknown error")

        logger.debug(f"Status check for job {job_id}: {job['status']}")

        return response

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting job status: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )


def _get_status_message(status: str) -> str:
    """Get human-readable status message"""
    messages = {
        JobStatus.QUEUED: "Job is queued and waiting to be processed",
        JobStatus.PROCESSING: "Job is currently being rendered",
        JobStatus.COMPLETED: "Rendering completed successfully",
        JobStatus.FAILED: "Rendering failed"
    }
    return messages.get(status, "Unknown status")
