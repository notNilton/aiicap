"""
Color processing strategies for image correction
"""

from enum import Enum


class Strategies(Enum):
    """
    Available strategies for color processing in image correction.
    
    String values represent named strategies:
    - MAJORITY: Use the most common color in a block
    - AVERAGE: Use arithmetic mean of colors
    - HARMONIC: Use harmonic mean of colors
    - GEOMETRIC: Use geometric mean of colors
    - MIDRANGE: Use midpoint between min and max colors
    - QUADRATIC: Use quadratic mean (RMS) of colors
    - CUBIC: Use cubic mean of colors
    
    Float values represent algorithm-based strategies with coverage thresholds:
    - ALG05 through ALG90: Use majority if coverage >= threshold, else average
    """
    MAJORITY = "majority"
    AVERAGE = "average"
    HARMONIC = "harmonic"
    GEOMETRIC = "geometric"
    MIDRANGE = "midrange"
    QUADRATIC = "quadratic"
    CUBIC = "cubic"
    ALG05 = 0.05
    ALG10 = 0.1
    ALG20 = 0.2
    ALG30 = 0.3
    ALG40 = 0.4
    ALG50 = 0.5
    ALG60 = 0.6
    ALG70 = 0.7
    ALG80 = 0.8
    ALG90 = 0.9
