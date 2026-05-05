"""
AIICAP Image Corrector GUI using Gradio.

Run with:
    python gui_corrector.py
    or
    make gui
"""

from typing import Tuple

import gradio as gr
from PIL import Image

from database.session import init_db
from image_correction.corrector import ImageCorrector


def restore_image(
    image: Image.Image | None,
    target_size: int,
    palette_size: int,
    alpha_threshold: int,
):
    """Run the restoration pipeline and return previews + metrics."""
    if image is None:
        return None, None, "No image uploaded.", ""

    size_val = target_size
    target_size = (target_size, target_size)

    corrector = ImageCorrector(auto_save_db=False)
    corrector.set_image(image)

    try:
        restored = corrector.restore(
            target_size=target_size,
            palette_size=palette_size,
            alpha_threshold=alpha_threshold,
        )

        # Upscale restored image to original dimensions for preview
        restored_preview = restored.resize(image.size, Image.Resampling.NEAREST)

        metrics = corrector.get_metrics()
        metrics_text = ""
        if metrics:
            metrics_text = "\n".join(
                f"{k}: {v:.4f}" if isinstance(v, float) else f"{k}: {v}"
                for k, v in metrics.items()
            )

        status = f"Done: {size_val}x{size_val}, K={palette_size}"
        return image, restored_preview, status, metrics_text
    except Exception as e:
        return image, None, f"Error: {e}", ""


def main():
    init_db()

    with gr.Blocks(title="AIICAP - Image Corrector") as demo:
        gr.Markdown("# AIICAP - Image Corrector")

        with gr.Row():
            with gr.Column(scale=1):
                input_img = gr.Image(
                    label="Upload Image",
                    type="pil",
                )
                target_size = gr.Slider(
                    minimum=8,
                    maximum=512,
                    value=64,
                    step=1,
                    label="Target Size (square)",
                )
                palette_size = gr.Slider(
                    minimum=2,
                    maximum=256,
                    value=16,
                    step=1,
                    label="Palette Size (K)",
                )
                alpha_threshold = gr.Slider(
                    minimum=0,
                    maximum=255,
                    value=128,
                    step=1,
                    label="Alpha Threshold",
                )
                restore_btn = gr.Button(
                    "Restore Pipeline",
                    variant="primary",
                )
                status = gr.Textbox(
                    label="Status",
                    value="Ready",
                    interactive=False,
                )
                metrics = gr.Textbox(
                    label="Metrics",
                    lines=6,
                    interactive=False,
                )

            with gr.Column(scale=2):
                with gr.Row():
                    orig_out = gr.Image(
                        label="Original",
                        interactive=False,
                    )
                    restored_out = gr.Image(
                        label="Restored",
                        interactive=False,
                    )

        restore_btn.click(
            fn=restore_image,
            inputs=[
                input_img,
                target_size,
                palette_size,
                alpha_threshold,
            ],
            outputs=[orig_out, restored_out, status, metrics],
        )

    demo.launch()


if __name__ == "__main__":
    main()
