"""Background worker for rendering jobs"""
import logging
import time
import threading
from pathlib import Path
from app.config import settings
from app.services.job_queue import job_queue
from app.services.renderer import render_service
from app.services.gcs_storage import gcs_storage
from app.models.responses import JobStatus

logger = logging.getLogger(__name__)


class RenderWorker:
    """Background worker for processing render jobs"""

    def __init__(self):
        self.running = False
        self.thread = None

    def start(self):
        """Start the worker in a background thread"""
        if self.running:
            logger.warning("Worker already running")
            return

        self.running = True
        self.thread = threading.Thread(target=self._worker_loop, daemon=True)
        self.thread.start()
        logger.info("Render worker started")

    def stop(self):
        """Stop the worker"""
        self.running = False
        if self.thread:
            self.thread.join(timeout=5)
        logger.info("Render worker stopped")

    def _worker_loop(self):
        """Main worker loop"""
        logger.info("Worker loop started")

        while self.running:
            try:
                # Get next job (non-blocking with 1 second timeout)
                job_id = job_queue.get_next_job(timeout=1)

                if job_id:
                    self._process_job(job_id)
                else:
                    # No jobs, sleep a bit
                    time.sleep(1)

            except Exception as e:
                logger.error(f"Worker loop error: {e}")
                time.sleep(5)  # Back off on error

    def _process_job(self, job_id: str):
        """
        Process a single job

        Args:
            job_id: Job identifier
        """
        try:
            logger.info(f"Processing job {job_id}")

            # Get job details
            job = job_queue.get_job(job_id)
            if not job:
                logger.error(f"Job {job_id} not found")
                return

            # Update status to processing
            job_queue.update_job_status(job_id, JobStatus.PROCESSING)

            # Extract job data
            job_data = job.get("data", {})
            function = job_data.get("function")
            x_range = job_data.get("x_range")
            y_range = job_data.get("y_range")

            # Render the visualization
            success, video_path, thumbnail_path, error = render_service.render_function_graph(
                job_id=job_id,
                function=function,
                x_range=x_range,
                y_range=y_range
            )

            if not success:
                # Mark as failed
                job_queue.update_job_status(
                    job_id,
                    JobStatus.FAILED,
                    error=error or "Rendering failed"
                )
                logger.error(f"Job {job_id} failed: {error}")
                return

            # Upload to GCS if available
            video_url = None
            thumbnail_url = None

            if gcs_storage.is_available():
                # Upload video
                video_remote_path = f"videos/{job_id}/video.mp4"
                if gcs_storage.upload_file(video_path, video_remote_path, "video/mp4"):
                    video_url = gcs_storage.get_signed_url(video_remote_path)

                # Upload thumbnail
                if thumbnail_path:
                    thumbnail_remote_path = f"videos/{job_id}/thumbnail.png"
                    if gcs_storage.upload_file(thumbnail_path, thumbnail_remote_path, "image/png"):
                        thumbnail_url = gcs_storage.get_signed_url(thumbnail_remote_path)

                # Clean up local files
                try:
                    Path(video_path).unlink()
                    if thumbnail_path:
                        Path(thumbnail_path).unlink()
                except:
                    pass
            else:
                # No GCS, use local paths (for development)
                logger.warning("GCS not available, using local paths")
                video_url = f"/outputs/{job_id}/video.mp4"
                thumbnail_url = f"/outputs/{job_id}/thumbnail.png" if thumbnail_path else None

            # Mark as completed
            job_queue.update_job_status(
                job_id,
                JobStatus.COMPLETED,
                video_url=video_url,
                thumbnail_url=thumbnail_url
            )

            logger.info(f"Job {job_id} completed successfully")

        except Exception as e:
            logger.error(f"Error processing job {job_id}: {e}")
            job_queue.update_job_status(
                job_id,
                JobStatus.FAILED,
                error=str(e)
            )


# Global worker instance
render_worker = RenderWorker()
