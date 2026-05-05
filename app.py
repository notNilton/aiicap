"""
Gradio web interface for the Pixel Art restoration pipeline.

Side-by-side preview: the restored image is processed at the target sprite
resolution and then upscaled back to the original size using Nearest-Neighbour
so both panels share the same dimensions.
"""

import gradio as gr

from database.session import init_db
from image_correction.corrector import ImageCorrector


def restore_image(input_image, target_w, target_h, palette_size, alpha_threshold):
    if input_image is None:
        return None, "Upload an image first."

    corr = ImageCorrector(auto_save_db=False)
    corr.set_image(input_image)

    result = corr.restore(
        target_size=(int(target_w), int(target_h)),
        palette_size=int(palette_size),
        alpha_threshold=int(alpha_threshold),
        return_original_size=True,
    )

    metrics = corr.get_metrics() or {}
    metrics_text = "\n".join(f"{k}: {v}" for k, v in metrics.items())

    return result, metrics_text


def restore_and_download(input_image, target_w, target_h, palette_size, alpha_threshold):
    """Return the actual sprite (small resolution) for download."""
    if input_image is None:
        return None, "Upload an image first."

    corr = ImageCorrector(auto_save_db=False)
    corr.set_image(input_image)

    result = corr.restore(
        target_size=(int(target_w), int(target_h)),
        palette_size=int(palette_size),
        alpha_threshold=int(alpha_threshold),
        return_original_size=False,
    )

    metrics = corr.get_metrics() or {}
    metrics_text = "\n".join(f"{k}: {v}" for k, v in metrics.items())

    return result, metrics_text


def build_ui() -> gr.Blocks:
    with gr.Blocks(title="AIICAP - Pixel Art Restoration Pipeline") as demo:
        gr.Markdown(
            """
            # AIICAP - Pixel Art Restoration Pipeline
            Deterministic correction architecture from the article:
            **Geometric Reconstruction → Chromatic Quantization → Alpha Binarization**
            """
        )

        with gr.Row():
            with gr.Column():
                input_img = gr.Image(
                    type="pil",
                    label="Upload Image",
                    image_mode="RGBA",
                )

                with gr.Row():
                    target_w = gr.Number(value=64, label="Target Width", precision=0)
                    target_h = gr.Number(value=64, label="Target Height", precision=0)

                palette_size = gr.Slider(
                    minimum=2, maximum=64, step=1, value=16, label="Palette Size (K)"
                )
                alpha_threshold = gr.Slider(
                    minimum=0, maximum=255, step=1, value=128, label="Alpha Threshold (τ)"
                )

                with gr.Row():
                    preview_btn = gr.Button("✨ Preview Restored", variant="primary")
                    download_btn = gr.Button("🔽 Generate Sprite (actual size)")

            with gr.Column():
                with gr.Row():
                    original_preview = gr.Image(
                        type="pil", label="Original", interactive=False
                    )
                    restored_preview = gr.Image(
                        type="pil", label="Restored (Preview)", interactive=False
                    )

                metrics_box = gr.Textbox(
                    label="Metrics", lines=8, interactive=False
                )

        # Wire events
        input_img.change(
            fn=lambda img: img,
            inputs=input_img,
            outputs=original_preview,
        )

        preview_btn.click(
            fn=restore_image,
            inputs=[input_img, target_w, target_h, palette_size, alpha_threshold],
            outputs=[restored_preview, metrics_box],
        )

        download_btn.click(
            fn=restore_and_download,
            inputs=[input_img, target_w, target_h, palette_size, alpha_threshold],
            outputs=[restored_preview, metrics_box],
        )

    return demo


def main():
    init_db()
    app = build_ui()
    app.launch(share=False)


if __name__ == "__main__":
    main()
