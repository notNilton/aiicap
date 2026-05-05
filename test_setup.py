import os
import sys

from database import init_db
from image_correction.corrector import ImageCorrector
from image_generation.generator import ImageGenerator


def main():
    print("Initializing database...")
    init_db()

    print("Checking ImageGenerator...")
    gen = ImageGenerator(auto_save_db=False)
    print("ImageGenerator created successfully.")

    print("Checking ImageCorrector...")
    corr = ImageCorrector(auto_save_db=False)
    print("ImageCorrector created successfully.")

    print("All modules imported and initialized correctly!")


if __name__ == "__main__":
    main()
