"""Manim rendering service"""
import logging
import os
import subprocess
from pathlib import Path
from typing import Optional, Tuple
from PIL import Image

logger = logging.getLogger(__name__)


class RenderService:
    """Service for rendering Manim scenes"""

    def __init__(self, output_dir: str = "outputs"):
        """
        Initialize render service

        Args:
            output_dir: Directory for output files
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)

    def render_function_graph(
        self,
        job_id: str,
        function: str,
        x_range: list,
        y_range: Optional[list] = None,
        color: str = "#58C4DD"
    ) -> Tuple[bool, Optional[str], Optional[str], Optional[str]]:
        """
        Render a function graph using Manim

        Args:
            job_id: Unique job identifier
            function: Mathematical function string
            x_range: X-axis range [min, max]
            y_range: Y-axis range [min, max] (optional)
            color: Hex color for graph

        Returns:
            Tuple of (success, video_path, thumbnail_path, error_message)
        """
        try:
            # Create job output directory
            job_dir = self.output_dir / job_id
            job_dir.mkdir(exist_ok=True)

            # Create a temporary Python file with the scene
            scene_file = job_dir / "scene.py"
            scene_code = self._generate_scene_code(function, x_range, y_range, color)

            with open(scene_file, "w") as f:
                f.write(scene_code)

            # Run Manim
            output_video = job_dir / "FunctionGraphScene.mp4"
            media_dir = job_dir / "media"

            cmd = [
                "manim",
                "-ql",  # Low quality for faster rendering (change to -qh for high quality)
                "--output_file", str(output_video),
                "--media_dir", str(media_dir),
                str(scene_file),
                "FunctionGraphScene"
            ]

            logger.info(f"Rendering job {job_id}: {' '.join(cmd)}")

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout
            )

            if result.returncode != 0:
                error_msg = f"Manim rendering failed: {result.stderr}"
                logger.error(error_msg)
                return False, None, None, error_msg

            # Find the actual output file (Manim creates it in media/videos/...)
            video_files = list(media_dir.glob("**/*.mp4"))
            if not video_files:
                error_msg = "No video file generated"
                logger.error(error_msg)
                return False, None, None, error_msg

            actual_video = video_files[0]
            final_video = job_dir / "video.mp4"
            actual_video.rename(final_video)

            # Generate thumbnail
            thumbnail_path = self._generate_thumbnail(final_video, job_dir)

            logger.info(f"Successfully rendered job {job_id}")
            return True, str(final_video), str(thumbnail_path), None

        except subprocess.TimeoutExpired:
            error_msg = f"Rendering timeout for job {job_id}"
            logger.error(error_msg)
            return False, None, None, error_msg

        except Exception as e:
            error_msg = f"Rendering error for job {job_id}: {str(e)}"
            logger.error(error_msg)
            return False, None, None, error_msg

    def _generate_scene_code(
        self,
        function: str,
        x_range: list,
        y_range: Optional[list],
        color: str
    ) -> str:
        """Generate Python code for Manim scene"""
        y_range_str = str(y_range) if y_range else "[-8, 8]"

        return f'''from manim import *
import numpy as np

class FunctionGraphScene(Scene):
    def construct(self):
        # Create axes
        axes = Axes(
            x_range=[{x_range[0]}, {x_range[1]}, 1],
            y_range={y_range_str},
            x_length=10,
            y_length=6,
            axis_config={{"color": BLUE}},
            tips=False,
        )

        # Add coordinates
        axes.add_coordinates()

        # Labels
        x_label = axes.get_x_axis_label("x")
        y_label = axes.get_y_axis_label("y")

        # Define function safely
        def f(x):
            import math
            # Create safe namespace
            safe_dict = {{
                'x': x,
                'sin': np.sin,
                'cos': np.cos,
                'tan': np.tan,
                'exp': np.exp,
                'log': np.log,
                'log10': np.log10,
                'sqrt': np.sqrt,
                'abs': np.abs,
                'pi': np.pi,
                'e': np.e,
            }}
            try:
                return eval("{function}", {{"__builtins__": {{}}}}, safe_dict)
            except:
                return 0

        # Create graph
        graph = axes.plot(f, color="{color}")

        # Create label
        func_label = MathTex(r"f(x) = {function.replace('**', '^')}")
        func_label.to_edge(UP)

        # Animate
        self.play(Create(axes), Write(x_label), Write(y_label), run_time=1)
        self.play(Create(graph), run_time=2)
        self.play(Write(func_label), run_time=1)
        self.wait(1)
'''

    def _generate_thumbnail(self, video_path: Path, output_dir: Path) -> Optional[str]:
        """
        Generate thumbnail from video

        Args:
            video_path: Path to video file
            output_dir: Output directory

        Returns:
            Path to thumbnail or None
        """
        try:
            thumbnail_path = output_dir / "thumbnail.png"

            # Use ffmpeg to extract first frame
            cmd = [
                "ffmpeg",
                "-i", str(video_path),
                "-vframes", "1",
                "-y",  # Overwrite output file
                str(thumbnail_path)
            ]

            result = subprocess.run(
                cmd,
                capture_output=True,
                timeout=30
            )

            if result.returncode == 0 and thumbnail_path.exists():
                # Resize thumbnail
                with Image.open(thumbnail_path) as img:
                    img.thumbnail((640, 480))
                    img.save(thumbnail_path)

                return str(thumbnail_path)

            return None

        except Exception as e:
            logger.error(f"Failed to generate thumbnail: {e}")
            return None


# Global render service instance
render_service = RenderService()
