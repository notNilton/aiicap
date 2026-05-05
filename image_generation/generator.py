"""
Image Generator using ChatGPT API (DALL-E) with PostgreSQL storage

This module provides functionality to generate images using LLM-based
image generation APIs like OpenAI's DALL-E, and automatically saves
them to PostgreSQL database.
"""

import io
import os
import time
from typing import Any, Dict, Literal, Optional

from PIL import Image

from database import get_session
from database.repository import ImageRepository


class ImageGenerator:
    """
    AI-powered image generator using ChatGPT API (DALL-E).

    Automatically saves all generated images to PostgreSQL database
    with metadata (prompt, date, model, etc.).
    """

    def __init__(self, api_key: Optional[str] = None, auto_save_db: bool = True):
        """
        Initialize the image generator.

        Args:
            api_key: Optional OpenAI API key. If not provided, will look for
                    OPENAI_API_KEY environment variable.
            auto_save_db: If True, automatically save generated images to database
        """
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.auto_save_db = auto_save_db
        self.last_generated_image: Optional[Image.Image] = None
        self.last_prompt: Optional[str] = None
        self.last_db_id: Optional[int] = None

    def generate(
        self,
        prompt: str,
        size: Literal["256x256", "512x512", "1024x1024", "1792x1024", "1024x1792"] = "1024x1024",
        quality: Literal["standard", "hd"] = "standard",
        n: int = 1,
        model: str = "dall-e-3",
    ) -> Image.Image:
        """
        Generate an image from a text prompt using DALL-E API.

        The generated image is automatically saved to PostgreSQL database.

        Args:
            prompt: Text description of the image to generate
            size: Image size (default: "1024x1024")
            quality: Image quality - "standard" or "hd" (default: "standard")
            n: Number of images to generate (default: 1)
            model: Model to use - "dall-e-3" or "dall-e-2" (default: "dall-e-3")

        Returns:
            Generated PIL Image

        Raises:
            ValueError: If API key is not set
            Exception: If API call fails

        Note:
            This is a placeholder implementation. Full implementation requires:
            - OpenAI Python SDK: pip install openai
            - Valid OpenAI API key
        """
        if not self.api_key:
            raise ValueError("API key not set. Please set OPENAI_API_KEY environment variable.")

        start_time = time.time()

        try:
            import requests
            from openai import OpenAI

            client = OpenAI(api_key=self.api_key)

            print(f"Generating image with prompt: {prompt[:50]}...")

            response = client.images.generate(
                model=model,
                prompt=prompt,
                size=size,
                quality=quality,
                n=n,
            )

            image_url = response.data[0].url
            # Download and convert to PIL Image
            image_data = requests.get(image_url).content
            self.last_generated_image = Image.open(io.BytesIO(image_data))
            self.last_prompt = prompt

            generation_time = time.time() - start_time

            # Save to database
            if self.auto_save_db:
                with get_session() as session:
                    db_image = ImageRepository.save_generated_image(
                        session=session,
                        image=self.last_generated_image,
                        prompt=prompt,
                        model=model,
                        size=size,
                        quality=quality,
                        generation_time=generation_time,
                        metadata={"n": n},
                    )
                    self.last_db_id = db_image.id
                    print(f"✓ Image saved to database with ID: {db_image.id}")

            return self.last_generated_image

        except ImportError:
            raise ImportError("Please install 'openai' and 'requests' packages")
        except Exception as e:
            print(f"Error generating image: {e}")
            raise e

    def generate_variation(
        self,
        image: Image.Image,
        n: int = 1,
        size: Literal["256x256", "512x512", "1024x1024"] = "1024x1024",
    ) -> Image.Image:
        """
        Create a variation of an existing image.

        The generated variation is automatically saved to database.

        Args:
            image: Source PIL Image
            n: Number of variations to generate (default: 1)
            size: Size of generated variations

        Returns:
            Generated variation as PIL Image

        Note:
            This is a placeholder implementation.
        """
        if not self.api_key:
            raise ValueError("API key not set")

        # TODO: Implement variation generation with database save
        raise NotImplementedError("Variation generation not yet implemented")

    def edit(
        self,
        image: Image.Image,
        mask: Image.Image,
        prompt: str,
        n: int = 1,
        size: Literal["256x256", "512x512", "1024x1024"] = "1024x1024",
    ) -> Image.Image:
        """
        Edit an image using a mask and prompt.

        The edited image is automatically saved to database.

        Args:
            image: Source PIL Image
            mask: Mask image (transparent areas will be edited)
            prompt: Text description of the edit
            n: Number of edited images to generate
            size: Size of generated images

        Returns:
            Edited PIL Image

        Note:
            This is a placeholder implementation.
        """
        if not self.api_key:
            raise ValueError("API key not set")

        # TODO: Implement image editing with database save
        raise NotImplementedError("Image editing not yet implemented")

    def get_last_image(self) -> Optional[Image.Image]:
        """
        Get the last generated image.

        Returns:
            Last generated PIL Image or None
        """
        return self.last_generated_image

    def get_last_prompt(self) -> Optional[str]:
        """
        Get the prompt used for the last generation.

        Returns:
            Last prompt string or None
        """
        return self.last_prompt

    def get_last_db_id(self) -> Optional[int]:
        """
        Get the database ID of the last generated image.

        Returns:
            Database ID or None
        """
        return self.last_db_id

    def load_from_database(self, image_id: int) -> Image.Image:
        """
        Load a previously generated image from the database.

        Args:
            image_id: Database ID of the image

        Returns:
            PIL Image object

        Raises:
            ValueError: If image not found
        """
        with get_session() as session:
            db_image = ImageRepository.get_generated_image(session, image_id)
            if not db_image:
                raise ValueError(f"Image with ID {image_id} not found in database")

            self.last_generated_image = ImageRepository.load_image_from_db(db_image)
            self.last_prompt = db_image.prompt
            self.last_db_id = db_image.id

            return self.last_generated_image

    def get_all_generated_images(self, limit: int = 100) -> list:
        """
        Get all generated images from database.

        Args:
            limit: Maximum number of images to return

        Returns:
            List of image metadata dictionaries
        """
        with get_session() as session:
            images = ImageRepository.get_all_generated_images(session, limit=limit)
            return [img.to_dict() for img in images]

    def search_by_prompt(self, search_term: str) -> list:
        """
        Search generated images by prompt.

        Args:
            search_term: Text to search for in prompts

        Returns:
            List of matching image metadata dictionaries
        """
        with get_session() as session:
            images = ImageRepository.search_by_prompt(session, search_term)
            return [img.to_dict() for img in images]


# Example usage documentation
__doc__ += """

Example Usage:
-------------

# Set up database first
from modules.database import init_db
init_db()

# Basic image generation (saves to PostgreSQL automatically)
generator = ImageGenerator(api_key="your-api-key")
image = generator.generate(
    prompt="A serene medieval landscape with mountains",
    size="1024x1024",
    quality="hd"
)
db_id = generator.get_last_db_id()  # Get database ID

# Load previously generated image
loaded_image = generator.load_from_database(db_id)

# Search by prompt
results = generator.search_by_prompt("medieval")
for result in results:
    print(f"ID: {result['id']}, Prompt: {result['prompt']}")
"""
