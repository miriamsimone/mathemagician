"""Function graph Manim scene"""
try:
    from manim import *
    MANIM_AVAILABLE = True
except ImportError:
    # Mock for development without Manim installed
    MANIM_AVAILABLE = False
    print("Warning: Manim not available, using mock")


if MANIM_AVAILABLE:
    class FunctionGraphScene(Scene):
        """Scene for plotting mathematical functions"""

        def __init__(self, function_str, x_range, y_range=None, color="#58C4DD", **kwargs):
            super().__init__(**kwargs)
            self.function_str = function_str
            self.x_range = x_range
            self.y_range = y_range or [-8, 8]
            self.color_hex = color

        def construct(self):
            """Construct the function graph scene"""
            # Create axes
            axes = Axes(
                x_range=[self.x_range[0], self.x_range[1], 1],
                y_range=[self.y_range[0], self.y_range[1], 1],
                x_length=10,
                y_length=6,
                axis_config={"color": BLUE},
                tips=False,
            )

            # Add grid
            axes.add_coordinates()

            # Parse and create function
            # Safety: eval with controlled namespace
            def safe_function(x):
                import numpy as np
                import math
                # Allow only math functions and numpy
                safe_dict = {
                    'x': x,
                    'sin': np.sin,
                    'cos': np.cos,
                    'tan': np.tan,
                    'exp': np.exp,
                    'log': np.log,
                    'sqrt': np.sqrt,
                    'abs': np.abs,
                    'pi': np.pi,
                    'e': np.e,
                    'np': np,
                    'math': math,
                }
                return eval(self.function_str, {"__builtins__": {}}, safe_dict)

            # Create the graph
            try:
                graph = axes.plot(safe_function, color=self.color_hex)

                # Create label
                label = MathTex(f"f(x) = {self.function_str}")
                label.to_edge(UP)

                # Animate
                self.play(Create(axes), run_time=1)
                self.play(Create(graph), run_time=2)
                self.play(Write(label), run_time=1)
                self.wait(1)

            except Exception as e:
                # If function is invalid, show error
                error_text = Text(f"Invalid function: {str(e)}", color=RED)
                self.play(Write(error_text))
                self.wait(2)


def create_function_graph_scene(function_str, x_range, y_range=None, color="#58C4DD", output_file="function_graph.mp4"):
    """
    Helper function to create and render a function graph

    Args:
        function_str: Mathematical function as string (e.g., "sin(x)", "x**2")
        x_range: List of [min, max] for x-axis
        y_range: Optional list of [min, max] for y-axis
        color: Hex color for the function graph
        output_file: Output filename

    Returns:
        Path to rendered video file
    """
    if not MANIM_AVAILABLE:
        raise RuntimeError("Manim is not installed. Please install with: pip install manim")

    # This will be called by the render service
    scene = FunctionGraphScene(function_str, x_range, y_range, color)
    return scene
