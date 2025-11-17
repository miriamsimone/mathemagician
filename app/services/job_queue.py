"""Job queue service using Redis"""
import json
import logging
from datetime import datetime
from typing import Optional, Dict, Any
from redis import Redis
from app.config import settings
from app.models.responses import JobStatus

logger = logging.getLogger(__name__)


class JobQueue:
    """Redis-based job queue"""

    def __init__(self):
        """Initialize Redis connection"""
        try:
            self.redis = Redis(
                host=settings.redis_host,
                port=settings.redis_port,
                password=settings.redis_password if settings.redis_password else None,
                decode_responses=True
            )
            # Test connection
            self.redis.ping()
            logger.info(f"Connected to Redis at {settings.redis_host}:{settings.redis_port}")
        except Exception as e:
            logger.error(f"Failed to connect to Redis: {e}")
            self.redis = None

    def create_job(self, job_id: str, job_data: Dict[str, Any]) -> bool:
        """
        Create a new job in the queue

        Args:
            job_id: Unique job identifier
            job_data: Job configuration and parameters

        Returns:
            True if job was created successfully
        """
        if not self.redis:
            logger.error("Redis not available")
            return False

        try:
            job = {
                "job_id": job_id,
                "status": JobStatus.QUEUED,
                "created_at": datetime.utcnow().isoformat(),
                "data": job_data,
            }

            # Store job metadata
            self.redis.setex(
                f"job:{job_id}",
                settings.job_ttl,
                json.dumps(job)
            )

            # Add to processing queue
            self.redis.lpush("job_queue", job_id)

            logger.info(f"Created job {job_id}")
            return True

        except Exception as e:
            logger.error(f"Failed to create job {job_id}: {e}")
            return False

    def get_job(self, job_id: str) -> Optional[Dict[str, Any]]:
        """
        Get job information

        Args:
            job_id: Job identifier

        Returns:
            Job data or None if not found
        """
        if not self.redis:
            return None

        try:
            job_json = self.redis.get(f"job:{job_id}")
            if job_json:
                return json.loads(job_json)
            return None

        except Exception as e:
            logger.error(f"Failed to get job {job_id}: {e}")
            return None

    def update_job_status(
        self,
        job_id: str,
        status: JobStatus,
        **kwargs
    ) -> bool:
        """
        Update job status and optionally add more fields

        Args:
            job_id: Job identifier
            status: New job status
            **kwargs: Additional fields to update (video_url, error, etc.)

        Returns:
            True if update was successful
        """
        if not self.redis:
            return False

        try:
            job = self.get_job(job_id)
            if not job:
                logger.error(f"Job {job_id} not found")
                return False

            job["status"] = status
            job.update(kwargs)

            if status == JobStatus.COMPLETED:
                job["completed_at"] = datetime.utcnow().isoformat()

            self.redis.setex(
                f"job:{job_id}",
                settings.job_ttl,
                json.dumps(job)
            )

            logger.info(f"Updated job {job_id} status to {status}")
            return True

        except Exception as e:
            logger.error(f"Failed to update job {job_id}: {e}")
            return False

    def get_next_job(self, timeout: int = 0) -> Optional[str]:
        """
        Get next job from the queue (blocking)

        Args:
            timeout: Timeout in seconds (0 = non-blocking)

        Returns:
            Job ID or None
        """
        if not self.redis:
            return None

        try:
            if timeout > 0:
                result = self.redis.brpop("job_queue", timeout=timeout)
                if result:
                    _, job_id = result
                    return job_id
            else:
                job_id = self.redis.rpop("job_queue")
                return job_id

        except Exception as e:
            logger.error(f"Failed to get next job: {e}")
            return None

        return None

    def is_healthy(self) -> bool:
        """Check if Redis connection is healthy"""
        if not self.redis:
            return False
        try:
            self.redis.ping()
            return True
        except:
            return False


# Global job queue instance
job_queue = JobQueue()
