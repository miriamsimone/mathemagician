"""Edit endpoint"""
import logging
import uuid
from fastapi import APIRouter, HTTPException
from app.models.requests import EditRequest
from app.models.responses import GenerateResponse, JobStatus
from app.services.job_queue import job_queue
from app.services.claude_service import claude_service

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/edit", response_model=GenerateResponse)
async def edit_visualization(request: EditRequest):
    """
    Edit an existing visualization using natural language

    Args:
        request: Edit request with job_id and edit description

    Returns:
        New job information with job_id for tracking
    """
    try:
        # Get the original job
        original_job = job_queue.get_job(request.job_id)
        if not original_job:
            raise HTTPException(
                status_code=404,
                detail=f"Job {request.job_id} not found"
            )

        # Extract original parameters
        original_data = original_job.get("data", {})
        scene_type = original_data.get("scene_type", "function_graph")

        # Build original params based on scene type
        if scene_type == "bar_chart":
            original_params = {
                "scene_type": "bar_chart",
                "categories": original_data.get("categories"),
                "values": original_data.get("values"),
                "color": original_data.get("color"),
                "title": original_data.get("title"),
                "background_color": original_data.get("background_color", "transparent")
            }
        elif scene_type == "surface_plot":
            original_params = {
                "scene_type": "surface_plot",
                "function": original_data.get("function"),
                "x_range": original_data.get("x_range"),
                "y_range": original_data.get("y_range"),
                "color": original_data.get("color"),
                "title": original_data.get("title"),
                "background_color": original_data.get("background_color", "transparent")
            }
        else:  # function_graph
            original_params = {
                "scene_type": "function_graph",
                "function": original_data.get("function"),
                "x_range": original_data.get("x_range"),
                "y_range": original_data.get("y_range"),
                "color": original_data.get("color"),
                "label": original_data.get("label"),
                "show_axis_labels": original_data.get("show_axis_labels", True),
                "show_tick_marks": original_data.get("show_tick_marks", True),
                "background_color": original_data.get("background_color", "transparent")
            }

        # Use Claude to interpret the edit
        logger.info(f"Interpreting edit for job {request.job_id}: {request.edit_description}")
        updated_params = await claude_service.interpret_edit(
            original_params,
            request.edit_description
        )

        # Validate required fields based on scene type
        updated_scene_type = updated_params.get("scene_type", scene_type)

        if updated_scene_type == "bar_chart":
            categories = updated_params.get("categories")
            values = updated_params.get("values")
            if not categories or not values:
                raise HTTPException(
                    status_code=400,
                    detail="Could not extract categories and values from edit description"
                )

            # Create new job ID
            new_job_id = str(uuid.uuid4())

            # Prepare job data with updated parameters
            job_data = {
                "scene_type": "bar_chart",
                "categories": categories,
                "values": values,
                "color": updated_params.get("color"),
                "title": updated_params.get("title"),
                "background_color": updated_params.get("background_color", "transparent"),
                "edited_from": request.job_id
            }
        elif updated_scene_type == "surface_plot":
            function = updated_params.get("function")
            x_range = updated_params.get("x_range")
            y_range = updated_params.get("y_range")
            if not function or not x_range or not y_range:
                raise HTTPException(
                    status_code=400,
                    detail="Could not extract function, x_range, and y_range from edit description"
                )

            # Create new job ID
            new_job_id = str(uuid.uuid4())

            # Prepare job data with updated parameters
            job_data = {
                "scene_type": "surface_plot",
                "function": function,
                "x_range": x_range,
                "y_range": y_range,
                "color": updated_params.get("color"),
                "title": updated_params.get("title"),
                "background_color": updated_params.get("background_color", "transparent"),
                "edited_from": request.job_id
            }
        else:  # function_graph
            function = updated_params.get("function")
            x_range = updated_params.get("x_range")
            if not function or not x_range:
                raise HTTPException(
                    status_code=400,
                    detail="Could not extract function and x_range from edit description"
                )

            # Create new job ID
            new_job_id = str(uuid.uuid4())

            # Prepare job data with updated parameters
            job_data = {
                "scene_type": "function_graph",
                "function": function,
                "x_range": x_range,
                "y_range": updated_params.get("y_range"),
                "color": updated_params.get("color"),
                "label": updated_params.get("label"),
                "show_axis_labels": updated_params.get("show_axis_labels", True),
                "show_tick_marks": updated_params.get("show_tick_marks", True),
                "background_color": updated_params.get("background_color", "transparent"),
                "edited_from": request.job_id
            }

        # Queue the job
        success = job_queue.create_job(new_job_id, job_data)

        if not success:
            raise HTTPException(
                status_code=503,
                detail="Failed to queue job. Please try again."
            )

        logger.info(f"Created edit job {new_job_id} from {request.job_id}")

        return GenerateResponse(
            job_id=new_job_id,
            status=JobStatus.QUEUED,
            message=f"Edit job queued successfully. Check status at /status/{new_job_id}"
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error editing visualization: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )
