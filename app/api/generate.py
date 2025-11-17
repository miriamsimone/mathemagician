"""Generate endpoint"""
import logging
import uuid
from fastapi import APIRouter, HTTPException
from app.models.requests import GenerateRequest
from app.models.responses import GenerateResponse, JobStatus
from app.services.job_queue import job_queue

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/generate", response_model=GenerateResponse)
async def generate_visualization(request: GenerateRequest):
    """
    Generate a math visualization

    Args:
        request: Generation request with function and parameters

    Returns:
        Job information with job_id for tracking
    """
    try:
        # Validate function (basic safety check)
        _validate_function(request.function)

        # Create job ID
        job_id = str(uuid.uuid4())

        # Prepare job data
        job_data = {
            "function": request.function,
            "x_range": request.x_range,
            "y_range": request.y_range,
            "scene_type": "function_graph"
        }

        # Queue the job
        success = job_queue.create_job(job_id, job_data)

        if not success:
            raise HTTPException(
                status_code=503,
                detail="Failed to queue job. Please try again."
            )

        logger.info(f"Created visualization job {job_id} for function: {request.function}")

        return GenerateResponse(
            job_id=job_id,
            status=JobStatus.QUEUED,
            message=f"Job queued successfully. Check status at /status/{job_id}"
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating visualization: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )


def _validate_function(function: str) -> None:
    """
    Validate function string for basic safety

    Args:
        function: Function string to validate

    Raises:
        HTTPException if function is invalid
    """
    # Check for dangerous patterns
    dangerous_patterns = [
        "import",
        "exec",
        "eval",
        "__",
        "open",
        "file",
        "os.",
        "sys.",
        "subprocess"
    ]

    function_lower = function.lower()
    for pattern in dangerous_patterns:
        if pattern in function_lower:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid function: contains forbidden pattern '{pattern}'"
            )

    # Check length
    if len(function) > 500:
        raise HTTPException(
            status_code=400,
            detail="Function string too long (max 500 characters)"
        )

    # Basic validation - must contain 'x'
    if 'x' not in function_lower:
        raise HTTPException(
            status_code=400,
            detail="Function must contain variable 'x'"
        )

    logger.debug(f"Function validated: {function}")
