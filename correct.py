import argparse
import sys

from database.session import init_db
from image_correction.corrector import ImageCorrector


def parse_size(size_str: str) -> tuple[int, int]:
    """Parse a string like '64x64' into a (width, height) tuple."""
    try:
        w, h = size_str.lower().split("x")
        return int(w), int(h)
    except ValueError:
        raise argparse.ArgumentTypeError(
            f"Invalid size format: '{size_str}'. Expected WxH (e.g., 64x64)."
        )


def main():
    parser = argparse.ArgumentParser(
        description=(
            "Restore Pixel Art integrity using the article pipeline: "
            "geometric reconstruction → chromatic quantization → alpha binarization."
        )
    )
    parser.add_argument("input", help="Input image path")
    parser.add_argument("output", help="Output image path")
    parser.add_argument(
        "--target-size",
        type=parse_size,
        default="64x64",
        help="Target output resolution (default: 64x64)",
    )
    parser.add_argument(
        "--palette-size",
        type=int,
        default=16,
        help="Number of colours for K-Means quantization (default: 16)",
    )
    parser.add_argument(
        "--alpha-threshold",
        type=int,
        default=128,
        help="Alpha binarisation threshold (default: 128)",
    )
    parser.add_argument(
        "--no-db", action="store_true", help="Do not save to the database"
    )
    args = parser.parse_args()

    if not args.no_db:
        init_db()

    corr = ImageCorrector(auto_save_db=not args.no_db)

    print(f"Loading image from {args.input}...")
    try:
        corr.load_image(args.input)
    except Exception as e:
        print(f"Error loading image: {e}")
        sys.exit(1)

    print(
        f"Restoring image with target_size={args.target_size}, "
        f"palette_size={args.palette_size}, alpha_threshold={args.alpha_threshold}..."
    )
    try:
        corr.restore(
            target_size=args.target_size,
            palette_size=args.palette_size,
            alpha_threshold=args.alpha_threshold,
        )

        output_image = corr.current_image
        output_image.save(args.output)
        print(f"Saved restored image to {args.output}")

        metrics = corr.get_metrics()
        if metrics:
            print("Metrics:")
            for k, v in metrics.items():
                print(f"  {k}: {v}")

    except Exception as e:
        print(f"Error during restoration: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
