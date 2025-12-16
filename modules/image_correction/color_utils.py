"""
Color calculation utilities for image correction
"""

import numpy as np
from typing import List, Tuple
from collections import defaultdict

Pixel = List[int]


def get_average_of_colors(pixels: np.ndarray) -> Pixel:
    """
    Calculate the arithmetic mean color of a pixel array.
    
    Args:
        pixels: numpy array of pixel values
    
    Returns:
        Average color as a list of integers
    """
    return np.round(np.mean(pixels, axis=0)).astype(int).tolist()


def get_harmonic_mean_of_colors(pixels: np.ndarray) -> Pixel:
    """
    Calculate the harmonic mean color of a pixel array.
    
    Args:
        pixels: numpy array of pixel values
    
    Returns:
        Harmonic mean color as a list of integers
    """
    harmonic = len(pixels) / np.sum(1.0 / np.maximum(pixels, 1e-6), axis=0)
    return np.round(harmonic).astype(int).tolist()


def get_geometric_mean_of_colors(pixels: np.ndarray) -> Pixel:
    """
    Calculate the geometric mean color of a pixel array.
    
    Args:
        pixels: numpy array of pixel values
    
    Returns:
        Geometric mean color as a list of integers
    """
    geometric = np.prod(np.maximum(pixels, 1), axis=0) ** (1.0 / len(pixels))
    return np.round(geometric).astype(int).tolist()


def get_midrange_of_colors(pixels: np.ndarray) -> Pixel:
    """
    Calculate the midrange color (average of min and max) of a pixel array.
    
    Args:
        pixels: numpy array of pixel values
    
    Returns:
        Midrange color as a list of integers
    """
    min_vals = np.min(pixels, axis=0)
    max_vals = np.max(pixels, axis=0)
    return np.round((min_vals + max_vals) / 2).astype(int).tolist()


def get_quadratic_mean_of_colors(pixels: np.ndarray) -> Pixel:
    """
    Calculate the quadratic mean (RMS) color of a pixel array.
    
    Args:
        pixels: numpy array of pixel values
    
    Returns:
        Quadratic mean color as a list of integers
    """
    quadratic = np.sqrt(np.mean(np.square(pixels), axis=0))
    return np.round(quadratic).astype(int).tolist()


def get_cubic_mean_of_colors(pixels: np.ndarray) -> Pixel:
    """
    Calculate the cubic mean color of a pixel array.
    
    Args:
        pixels: numpy array of pixel values
    
    Returns:
        Cubic mean color as a list of integers
    """
    cubic = np.cbrt(np.mean(np.power(pixels, 3), axis=0))
    return np.round(cubic).astype(int).tolist()


def get_majority_color(pixels: np.ndarray, tolerance: int = 1) -> Tuple[Pixel, int]:
    """
    Find the most common color within a tolerance threshold.
    
    Args:
        pixels: numpy array of pixel values
        tolerance: color matching tolerance (default: 1)
    
    Returns:
        Tuple of (majority_color, occurrences)
    """
    color_counts = defaultdict(int)
    
    for pixel in pixels:
        found = False
        for color in color_counts:
            if all(abs(pixel[i] - color[i]) <= tolerance for i in range(len(pixel))):
                color_counts[color] += 1
                found = True
                break
        if not found:
            color_counts[tuple(pixel)] = 1
    
    majority_color = max(color_counts.items(), key=lambda x: x[1])
    return list(majority_color[0]), majority_color[1]
