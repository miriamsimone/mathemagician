"""Google Cloud Storage service"""
import logging
from pathlib import Path
from datetime import timedelta
from typing import Optional
from google.cloud import storage
from google.oauth2 import service_account
from app.config import settings

logger = logging.getLogger(__name__)


class GCSStorage:
    """Google Cloud Storage helper"""

    def __init__(self):
        """Initialize GCS client"""
        self.client = None
        self.bucket = None

        # Only initialize if credentials are provided
        if settings.google_application_credentials and Path(settings.google_application_credentials).exists():
            try:
                credentials = service_account.Credentials.from_service_account_file(
                    settings.google_application_credentials
                )
                self.client = storage.Client(
                    project=settings.gcp_project_id,
                    credentials=credentials
                )
                self.bucket = self.client.bucket(settings.gcs_bucket)
                logger.info(f"Connected to GCS bucket: {settings.gcs_bucket}")
            except Exception as e:
                logger.warning(f"Failed to initialize GCS: {e}")
        else:
            # Try default credentials (useful for Cloud Run)
            try:
                self.client = storage.Client(project=settings.gcp_project_id)
                self.bucket = self.client.bucket(settings.gcs_bucket)
                logger.info(f"Connected to GCS using default credentials: {settings.gcs_bucket}")
            except Exception as e:
                logger.warning(f"GCS not available: {e}")

    def upload_file(
        self,
        local_path: str,
        remote_path: str,
        content_type: Optional[str] = None
    ) -> bool:
        """
        Upload file to GCS

        Args:
            local_path: Local file path
            remote_path: Remote path in bucket
            content_type: MIME content type

        Returns:
            True if upload was successful
        """
        if not self.bucket:
            logger.error("GCS not initialized")
            return False

        try:
            blob = self.bucket.blob(remote_path)

            if content_type:
                blob.upload_from_filename(
                    local_path,
                    content_type=content_type
                )
            else:
                blob.upload_from_filename(local_path)

            logger.info(f"Uploaded {local_path} to gs://{settings.gcs_bucket}/{remote_path}")
            return True

        except Exception as e:
            logger.error(f"Failed to upload {local_path}: {e}")
            return False

    def get_signed_url(
        self,
        remote_path: str,
        expiration_days: int = 7
    ) -> Optional[str]:
        """
        Generate signed URL for file

        Args:
            remote_path: Remote path in bucket
            expiration_days: URL expiration in days

        Returns:
            Signed URL or None
        """
        if not self.bucket:
            logger.error("GCS not initialized")
            return None

        try:
            blob = self.bucket.blob(remote_path)

            url = blob.generate_signed_url(
                version="v4",
                expiration=timedelta(days=expiration_days),
                method="GET"
            )

            logger.info(f"Generated signed URL for {remote_path}")
            return url

        except Exception as e:
            logger.error(f"Failed to generate signed URL for {remote_path}: {e}")
            return None

    def delete_file(self, remote_path: str) -> bool:
        """
        Delete file from GCS

        Args:
            remote_path: Remote path in bucket

        Returns:
            True if deletion was successful
        """
        if not self.bucket:
            logger.error("GCS not initialized")
            return False

        try:
            blob = self.bucket.blob(remote_path)
            blob.delete()
            logger.info(f"Deleted gs://{settings.gcs_bucket}/{remote_path}")
            return True

        except Exception as e:
            logger.error(f"Failed to delete {remote_path}: {e}")
            return False

    def is_available(self) -> bool:
        """Check if GCS is available"""
        return self.bucket is not None


# Global GCS storage instance
gcs_storage = GCSStorage()
