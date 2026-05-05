import argparse
import os
import sys

from database.session import init_db
from image_generation.generator import ImageGenerator


def main():
    parser = argparse.ArgumentParser(
        description="Generate an image using DALL-E and save it to the database."
    )
    parser.add_argument("prompt", help="Prompt for the image generation")
    parser.add_argument(
        "--size", default="1024x1024", help="Size of the image (default: 1024x1024)"
    )
    parser.add_argument("--no-db", action="store_true", help="Do not save to the database")
    args = parser.parse_args()

    if not args.no_db:
        init_db()

    gen = ImageGenerator(auto_save_db=not args.no_db)

    print(f"Generating image for prompt: '{args.prompt}'...")
    try:
        image = gen.generate(prompt=args.prompt, size=args.size)
        print("Image generated successfully!")

        if args.no_db:
            # If not saving to DB, save to a local file
            os.makedirs("output", exist_ok=True)
            output_path = "output/generated_image.png"
            image.save(output_path)
            print(f"Saved locally to {output_path}")

    except Exception as e:
        print(f"Error during generation: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
