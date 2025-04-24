#%%
# Import the 'csv' module for working with CSV files.
import csv
# Import the 'os' module for interacting with the operating system, like file paths.
import os
# Import the 'sys' module for system-specific parameters and functions, like standard error output.
import sys
# Import the 're' module for regular expression operations (though not used in the final version).
import re
# Import the 'tempfile' module for creating temporary files and directories.
import tempfile
# Import 'BytesIO' from the 'io' module to handle binary data (like images) in memory.
from io import BytesIO
# Import the 'json' module for working with JSON data, used here for debugging output.
import json # Import json for better debugging output

import openai
openai.api_key = "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"


# Roboflow SDK Import - Attempt to import, provide instructions if missing
# Start a try block to handle potential import errors if the SDK isn't installed.
try:
    # Attempt to import the InferenceHTTPClient class from the inference_sdk library.
    from inference_sdk import InferenceHTTPClient
# If an ImportError occurs (meaning the library is not found).
except ImportError:
    # Print an error message to standard error explaining how to install the SDK.
    print("ERROR: Roboflow Inference SDK not found. Please install it using: pip install inference_sdk", file=sys.stderr)
    # Exit the script with a non-zero status code to indicate failure.
    sys.exit(1)

# --- Conversion Factors Dictionary ---
# Define a dictionary holding various unit conversions to grams for different food items.
# Note: This dictionary is large and contains many approximate conversions.
CONVERSIONS = {
    # Section for liquid conversions.
    # == Liquids & Beverages (Density approx 1g/ml unless noted) ==
    # Conversion factors for water: ounce, glass, bottle, cup to grams.
    "water":      {"oz": 29.57, "glass": 237.0, "bottle": 500.0, "cup": 237.0}, # Standard 8oz glass/cup
    # Conversion factors for coffee: ounce, mug, cup to grams.
    "coffee":     {"oz": 29.57, "mug": 355.0, "cup": 237.0}, # Typical mug size
    # Conversion factors for black coffee: ounce, mug, cup to grams.
    "coffee black": {"oz": 29.57, "mug": 355.0, "cup": 237.0},
    # Conversion factors for tea: ounce, mug, cup to grams.
    "tea":        {"oz": 29.57, "mug": 355.0, "cup": 237.0},
    # Conversion factors for black tea: ounce, mug, cup to grams.
    "tea black":  {"oz": 29.57, "mug": 355.0, "cup": 237.0},
    # Conversion factors for generic milk: splash, teaspoon, tablespoon, ounce, cup to grams.
    "milk":       {"splash": 30.0, "tsp": 4.9, "tbsp": 14.8, "oz": 29.57, "cup": 240.0}, # Slightly denser
    # Conversion factors for whole milk: splash, teaspoon, tablespoon, ounce, cup to grams.
    "milk whole": {"splash": 30.0, "tsp": 4.9, "tbsp": 14.8, "oz": 29.57, "cup": 244.0},
    # Conversion factors for 2% milk: splash, teaspoon, tablespoon, ounce, cup to grams.
    "milk 2 percent": {"splash": 30.0, "tsp": 4.9, "tbsp": 14.8, "oz": 29.57, "cup": 245.0},
    # Conversion factors for 1% milk: splash, teaspoon, tablespoon, ounce, cup to grams.
    "milk 1 percent": {"splash": 30.0, "tsp": 4.9, "tbsp": 14.8, "oz": 29.57, "cup": 245.0},
    # Conversion factors for skim milk: splash, teaspoon, tablespoon, ounce, cup to grams.
    "milk skim":  {"splash": 30.0, "tsp": 5.0, "tbsp": 15.0, "oz": 29.57, "cup": 245.0},
    # Conversion factors for soy milk: splash, teaspoon, tablespoon, ounce, cup to grams.
    "soy milk":   {"splash": 30.0, "tsp": 5.0, "tbsp": 15.0, "oz": 29.57, "cup": 243.0},
    # Conversion factors for almond milk: splash, teaspoon, tablespoon, ounce, cup to grams.
    "almond milk": {"splash": 30.0, "tsp": 5.0, "tbsp": 15.0, "oz": 29.57, "cup": 240.0}, # Varies
    # Conversion factors for oat milk: splash, teaspoon, tablespoon, ounce, cup to grams.
    "oat milk":   {"splash": 30.0, "tsp": 5.0, "tbsp": 15.0, "oz": 29.57, "cup": 240.0}, # Varies
    # Conversion factors for evaporated milk: teaspoon, tablespoon, ounce, can to grams.
    "evaporated milk": {"tsp": 5.5, "tbsp": 16.5, "oz": 33.5, "can": 354.0}, # Standard can (12 fl oz volume, denser)
    # Conversion factors for condensed milk: teaspoon, tablespoon, ounce to grams.
    "condensed milk": {"tsp": 10.2, "tbsp": 30.6, "oz": 30.6}, # Very dense, often sold by weight oz (~396g/14oz can)
    # Conversion factors for generic juice: ounce, glass, cup to grams.
    "juice":      {"oz": 29.57, "glass": 237.0, "cup": 240.0}, # Generic fruit juice
    # Conversion factors for orange juice: ounce, glass, cup to grams.
    "orange juice": {"oz": 29.57, "glass": 237.0, "cup": 248.0},
    # Conversion factors for apple juice: ounce, glass, cup to grams.
    "apple juice": {"oz": 29.57, "glass": 237.0, "cup": 248.0},
    # Conversion factors for grape juice: ounce, glass, cup to grams.
    "grape juice": {"oz": 29.57, "glass": 237.0, "cup": 253.0},
    # Conversion factors for cranberry juice cocktail: ounce, glass, cup to grams.
    "cranberry juice cocktail": {"oz": 29.57, "glass": 237.0, "cup": 253.0},
    # Conversion factors for tomato juice: ounce, glass, cup to grams.
    "tomato juice": {"oz": 29.57, "glass": 237.0, "cup": 243.0},
    # Conversion factors for lemonade: ounce, glass, cup to grams.
    "lemonade":   {"oz": 29.57, "glass": 237.0, "cup": 240.0}, # Varies greatly
    # Conversion factors for iced tea: ounce, glass, cup to grams.
    "iced tea":   {"oz": 29.57, "glass": 355.0, "cup": 240.0}, # Often larger glass
    # Conversion factors for generic soda: ounce, can, bottle to grams.
    "soda":       {"oz": 29.57, "can": 355.0, "bottle": 500.0}, # Standard 12oz can, 500ml bottle
    # Conversion factors for cola soda: ounce, can, bottle to grams.
    "cola soda":  {"oz": 29.57, "can": 355.0, "bottle": 500.0},
    # Conversion factors for lemon lime soda: ounce, can, bottle to grams.
    "lemon lime soda": {"oz": 29.57, "can": 355.0, "bottle": 500.0},
    # Conversion factors for ginger ale: ounce, can, bottle to grams.
    "ginger ale": {"oz": 29.57, "can": 355.0, "bottle": 500.0},
    # Conversion factors for diet soda: ounce, can, bottle to grams.
    "diet soda":  {"oz": 29.57, "can": 355.0, "bottle": 500.0},
    # Conversion factors for sports drink: ounce, bottle to grams.
    "sports drink": {"oz": 29.57, "bottle": 500.0}, # Assumed 500ml
    # Conversion factors for energy drink: ounce, can to grams.
    "energy drink": {"oz": 29.57, "can": 250.0}, # Assumed 250ml
    # Conversion factors for generic beer: ounce, can, bottle, pint to grams.
    "beer":       {"oz": 29.57, "can": 355.0, "bottle": 355.0, "pint": 473.0}, # US Pint (16 fl oz)
    # Conversion factors for regular beer: ounce, can, bottle, pint to grams.
    "beer regular": {"oz": 29.57, "can": 355.0, "bottle": 355.0, "pint": 473.0},
    # Conversion factors for light beer: ounce, can, bottle, pint to grams.
    "beer light": {"oz": 29.57, "can": 355.0, "bottle": 355.0, "pint": 473.0},
    # Conversion factors for generic wine: glass, bottle, ounce to grams.
    "wine":       {"glass": 148.0, "bottle": 750.0, "oz": 29.57}, # Standard 5oz pour (148ml)
    # Conversion factors for red wine: glass, bottle, ounce to grams.
    "wine red":   {"glass": 148.0, "bottle": 750.0, "oz": 29.57},
    # Conversion factors for white wine: glass, bottle, ounce to grams.
    "wine white": {"glass": 148.0, "bottle": 750.0, "oz": 29.57},
    # Conversion factors for liquor: shot, ounce to grams.
    "liquor":     {"shot": 44.0, "oz": 29.57}, # Standard 1.5oz shot (44ml)
    # Conversion factors for generic smoothie: ounce, glass, cup to grams.
    "smoothie":   {"oz": 29.57, "glass": 473.0, "cup": 300.0}, # Typical large glass/serving (16oz)
    # Conversion factors for fruit smoothie: ounce, glass, cup to grams.
    "smoothie fruit": {"oz": 29.57, "glass": 473.0, "cup": 300.0},
    # Conversion factors for generic milkshake: ounce, glass, cup to grams.
    "milkshake":  {"oz": 29.57, "glass": 473.0, "cup": 350.0}, # Often large
    # Conversion factors for vanilla milkshake: ounce, glass, cup to grams.
    "milkshake vanilla": {"oz": 29.57, "glass": 473.0, "cup": 350.0},

    # Section for soup and stew conversions.
    # == Soups & Stews (Use S/M/L for serving size via CSV, bowl/cup is reference) ==
    # Conversion factors for generic soup: bowl, teaspoon, tablespoon, ounce, cup to grams.
    "soup":       {"bowl": 300.0, "tsp": 5.0, "tbsp": 15.0, "oz": 29.57, "cup": 245.0}, # Bowl/Cup=reference volume weight avg
    # Conversion factors for tomato soup: bowl, teaspoon, tablespoon, ounce, cup to grams.
    "tomato soup": {"bowl": 300.0, "tsp": 5.0, "tbsp": 15.0, "oz": 29.57, "cup": 244.0},
    # Conversion factors for chicken noodle soup: bowl, teaspoon, tablespoon, ounce, cup to grams.
    "chicken noodle soup": {"bowl": 300.0, "tsp": 5.0, "tbsp": 15.0, "oz": 29.57, "cup": 241.0},
    # Conversion factors for lentil soup: bowl, teaspoon, tablespoon, ounce, cup to grams.
    "lentil soup": {"bowl": 300.0, "tsp": 5.5, "tbsp": 16.5, "oz": 29.57, "cup": 250.0}, # Denser
    # Conversion factors for minestrone soup: bowl, teaspoon, tablespoon, ounce, cup to grams.
    "minestrone soup": {"bowl": 300.0, "tsp": 5.0, "tbsp": 15.0, "oz": 29.57, "cup": 240.0}, # Varies
    # Conversion factors for vegetable soup: bowl, teaspoon, tablespoon, ounce, cup to grams.
    "vegetable soup": {"bowl": 300.0, "tsp": 5.0, "tbsp": 15.0, "oz": 29.57, "cup": 240.0}, # Varies
    # Conversion factors for cream of mushroom soup: bowl, teaspoon, tablespoon, ounce, cup to grams.
    "cream of mushroom soup": {"bowl": 300.0, "tsp": 5.0, "tbsp": 15.0, "oz": 29.57, "cup": 248.0}, # Condensed diluted
    # Conversion factors for cream of chicken soup: bowl, teaspoon, tablespoon, ounce, cup to grams.
    "cream of chicken soup": {"bowl": 300.0, "tsp": 5.0, "tbsp": 15.0, "oz": 29.57, "cup": 248.0},
    # Conversion factors for cream of tomato soup: bowl, teaspoon, tablespoon, ounce, cup to grams.
    "cream of tomato soup": {"bowl": 300.0, "tsp": 5.0, "tbsp": 15.0, "oz": 29.57, "cup": 248.0},
    # Conversion factors for french onion soup: bowl, ounce, cup to grams.
    "french onion soup": {"bowl": 350.0, "oz": 29.57, "cup": 240.0}, # Broth based, bowl reference
    # Conversion factors for generic clam chowder: bowl, teaspoon, tablespoon, ounce, cup to grams.
    "clam chowder": {"bowl": 300.0, "tsp": 5.0, "tbsp": 15.0, "oz": 29.57, "cup": 245.0}, # Creamy
    # Conversion factors for New England clam chowder: bowl, teaspoon, tablespoon, ounce, cup to grams.
    "clam chowder new england": {"bowl": 300.0, "tsp": 5.0, "tbsp": 15.0, "oz": 29.57, "cup": 245.0},
    # Conversion factors for Manhattan clam chowder: bowl, teaspoon, tablespoon, ounce, cup to grams.
    "clam chowder manhattan": {"bowl": 300.0, "tsp": 5.0, "tbsp": 15.0, "oz": 29.57, "cup": 240.0}, # Broth based
    # Conversion factors for pho soup: bowl, ounce, cup to grams.
    "pho soup":   {"bowl": 500.0, "oz": 29.57, "cup": 240.0}, # Large serving reference
    # Conversion factors for ramen noodles: bowl, ounce, cup to grams.
    "ramen noodles": {"bowl": 450.0, "oz": 28.35, "cup": 140.0}, # Cooked noodles + broth ref
    # Conversion factors for generic stew: bowl, teaspoon, tablespoon, ounce, cup to grams.
    "stew":       {"bowl": 350.0, "tsp": 5.5, "tbsp": 16.5, "oz": 28.35, "cup": 250.0}, # Dense serving reference
    # Conversion factors for beef stew: bowl, teaspoon, tablespoon, ounce, cup to grams.
    "beef stew":  {"bowl": 350.0, "tsp": 5.5, "tbsp": 16.5, "oz": 28.35, "cup": 255.0},
    # Conversion factors for chili: bowl, teaspoon, tablespoon, ounce, cup to grams.
    "chili":      {"bowl": 350.0, "tsp": 5.5, "tbsp": 16.5, "oz": 28.35, "cup": 255.0}, # Dense serving reference

    # Section for fat, oil, and spread conversions.
    # == Fats, Oils, Spreads ==
    # Conversion factors for generic oil: teaspoon, tablespoon, drizzle, ounce to grams.
    "oil":        {"tsp": 4.5, "tbsp": 13.6, "drizzle": 7.0, "oz": 28.35}, # Generic oil ~0.92 g/ml
    # Conversion factors for olive oil: teaspoon, tablespoon, drizzle, ounce to grams.
    "oil olive":  {"tsp": 4.5, "tbsp": 13.5, "drizzle": 7.0, "oz": 28.35}, # ~0.91 g/ml
    # Conversion factors for vegetable oil: teaspoon, tablespoon, drizzle, ounce to grams.
    "oil vegetable": {"tsp": 4.5, "tbsp": 13.6, "drizzle": 7.0, "oz": 28.35}, # ~0.92 g/ml
    # Conversion factors for coconut oil: teaspoon, tablespoon, drizzle, ounce to grams.
    "oil coconut": {"tsp": 4.3, "tbsp": 13.0, "drizzle": 6.5, "oz": 28.35}, # ~0.92 g/ml, solid below 76F
    # Conversion factors for avocado oil: teaspoon, tablespoon, drizzle, ounce to grams.
    "oil avocado": {"tsp": 4.5, "tbsp": 13.6, "drizzle": 7.0, "oz": 28.35}, # ~0.91 g/ml
    # Conversion factors for peanut oil: teaspoon, tablespoon, drizzle, ounce to grams.
    "oil peanut": {"tsp": 4.5, "tbsp": 13.6, "drizzle": 7.0, "oz": 28.35}, # ~0.91 g/ml
    # Conversion factors for sesame oil: teaspoon, tablespoon, drizzle, ounce to grams.
    "oil sesame": {"tsp": 4.5, "tbsp": 13.6, "drizzle": 7.0, "oz": 28.35}, # ~0.92 g/ml
    # Conversion factors for generic butter: teaspoon, tablespoon, pat, stick, ounce to grams.
    "butter":     {"tsp": 4.7, "tbsp": 14.2, "pat": 5.0, "stick": 113.0, "oz": 28.35}, # Standard US stick=1/2 cup=113g
    # Conversion factors for salted butter: teaspoon, tablespoon, pat, stick, ounce to grams.
    "butter salted": {"tsp": 4.7, "tbsp": 14.2, "pat": 5.0, "stick": 113.0, "oz": 28.35},
    # Conversion factors for unsalted butter: teaspoon, tablespoon, pat, stick, ounce to grams.
    "butter unsalted": {"tsp": 4.7, "tbsp": 14.2, "pat": 5.0, "stick": 113.0, "oz": 28.35},
    # Conversion factors for generic margarine: teaspoon, tablespoon, pat, stick, ounce to grams.
    "margarine":  {"tsp": 4.7, "tbsp": 14.2, "pat": 5.0, "stick": 113.0, "oz": 28.35},
    # Conversion factors for stick margarine: teaspoon, tablespoon, pat, stick, ounce to grams.
    "margarine stick": {"tsp": 4.7, "tbsp": 14.2, "pat": 5.0, "stick": 113.0, "oz": 28.35},
    # Conversion factors for tub margarine: teaspoon, tablespoon, ounce to grams.
    "margarine tub": {"tsp": 4.7, "tbsp": 14.2, "oz": 28.35}, # Assume similar density
    # Conversion factors for lard: teaspoon, tablespoon, ounce to grams.
    "lard":       {"tsp": 4.5, "tbsp": 12.8, "oz": 28.35}, # ~0.9 g/ml
    # Conversion factors for ghee: teaspoon, tablespoon, ounce to grams.
    "ghee":       {"tsp": 4.6, "tbsp": 13.8, "oz": 28.35}, # Slightly denser than oil
    # Conversion factors for generic shortening: teaspoon, tablespoon, ounce to grams.
    "shortening": {"tsp": 4.3, "tbsp": 12.8, "oz": 28.35}, # ~0.87 g/ml
    # Conversion factors for vegetable shortening: teaspoon, tablespoon, ounce to grams.
    "shortening vegetable": {"tsp": 4.3, "tbsp": 12.8, "oz": 28.35},
    # Conversion factors for cooking spray: teaspoon, tablespoon to grams (approximating a spray duration).
    "cooking spray": {"tsp": 0.27, "tbsp": 0.8}, # Weight per 1 sec spray approx
    # Conversion factors for generic mayonnaise: teaspoon, tablespoon, packet, ounce to grams.
    "mayonnaise": {"tsp": 4.6, "tbsp": 13.8, "packet": 10.0, "oz": 28.35}, # ~0.91 g/ml
    # Conversion factors for full fat mayonnaise: teaspoon, tablespoon, packet, ounce to grams.
    "mayonnaise full fat": {"tsp": 4.6, "tbsp": 13.8, "packet": 10.0, "oz": 28.35},
    # Conversion factors for light mayonnaise: teaspoon, tablespoon, packet, ounce to grams.
    "mayonnaise light": {"tsp": 4.8, "tbsp": 14.4, "packet": 10.0, "oz": 28.35}, # Often higher water content
    # Conversion factors for olive oil mayonnaise: teaspoon, tablespoon, packet, ounce to grams.
    "mayonnaise olive oil": {"tsp": 4.6, "tbsp": 13.8, "packet": 10.0, "oz": 28.35},
    # Conversion factors for aioli: teaspoon, tablespoon, ounce to grams.
    "aioli":      {"tsp": 4.6, "tbsp": 13.8, "oz": 28.35}, # Similar to mayo
    # Conversion factors for generic peanut butter: teaspoon, tablespoon, ounce to grams.
    "peanut butter": {"tsp": 5.3, "tbsp": 16.0, "oz": 28.35}, # USDA avg
    # Conversion factors for natural peanut butter: teaspoon, tablespoon, ounce to grams.
    "peanut butter natural": {"tsp": 5.3, "tbsp": 16.0, "oz": 28.35},
    # Conversion factors for regular peanut butter: teaspoon, tablespoon, ounce to grams.
    "peanut butter regular": {"tsp": 5.3, "tbsp": 16.0, "oz": 28.35},
    # Conversion factors for almond butter: teaspoon, tablespoon, ounce to grams.
    "almond butter": {"tsp": 5.3, "tbsp": 16.0, "oz": 28.35}, # Similar density
    # Conversion factors for cashew butter: teaspoon, tablespoon, ounce to grams.
    "cashew butter": {"tsp": 5.3, "tbsp": 16.0, "oz": 28.35},
    # Conversion factors for sunflower seed butter: teaspoon, tablespoon, ounce to grams.
    "sunflower seed butter": {"tsp": 5.3, "tbsp": 16.0, "oz": 28.35},
    # Conversion factors for generic jam: teaspoon, tablespoon, ounce to grams.
    "jam":        {"tsp": 6.7, "tbsp": 20.0, "oz": 28.35}, # Denser than water (~1.3 g/ml)
    # Conversion factors for generic jelly: teaspoon, tablespoon, ounce to grams.
    "jelly":      {"tsp": 6.7, "tbsp": 20.0, "oz": 28.35},
    # Conversion factors for marmalade: teaspoon, tablespoon, ounce to grams.
    "marmalade":  {"tsp": 6.7, "tbsp": 20.0, "oz": 28.35},
    # Conversion factors for apple butter: teaspoon, tablespoon, ounce to grams.
    "apple butter": {"tsp": 6.0, "tbsp": 18.0, "oz": 28.35}, # Less dense than jam
    # Conversion factors for nutella: teaspoon, tablespoon, packet, ounce to grams.
    "nutella":    {"tsp": 6.3, "tbsp": 19.0, "packet": 15.0, "oz": 28.35}, # ~1.26 g/ml
    # Conversion factors for nutella hazelnut spread: teaspoon, tablespoon, packet, ounce to grams.
    "nutella hazelnut spread": {"tsp": 6.3, "tbsp": 19.0, "packet": 15.0, "oz": 28.35},
    # Conversion factors for generic cream cheese: teaspoon, tablespoon, ounce to grams.
    "cream cheese": {"tsp": 4.9, "tbsp": 14.5, "oz": 28.35}, # USDA Block
    # Conversion factors for regular cream cheese: teaspoon, tablespoon, ounce to grams.
    "cream cheese regular": {"tsp": 4.9, "tbsp": 14.5, "oz": 28.35},
    # Conversion factors for light cream cheese: teaspoon, tablespoon, ounce to grams.
    "cream cheese light": {"tsp": 5.0, "tbsp": 15.0, "oz": 28.35}, # More water
    # Conversion factors for generic sour cream: teaspoon, tablespoon, ounce, dollop to grams.
    "sour cream": {"tsp": 5.0, "tbsp": 15.0, "oz": 28.35, "dollop": 25.0}, # Generous dollop ~1.0 g/ml
    # Conversion factors for regular sour cream: teaspoon, tablespoon, ounce, dollop to grams.
    "sour cream regular": {"tsp": 5.0, "tbsp": 15.0, "oz": 28.35, "dollop": 25.0},
    # Conversion factors for light sour cream: teaspoon, tablespoon, ounce, dollop to grams.
    "sour cream light": {"tsp": 5.0, "tbsp": 15.0, "oz": 28.35, "dollop": 25.0},
    # Conversion factors for generic cream: teaspoon, tablespoon, splash, ounce to grams.
    "cream":      {"tsp": 5.0, "tbsp": 15.0, "splash": 30.0, "oz": 29.57}, # Heavy cream ~1.0 g/ml
    # Conversion factors for heavy cream: teaspoon, tablespoon, splash, ounce to grams.
    "cream heavy": {"tsp": 5.0, "tbsp": 15.0, "splash": 30.0, "oz": 29.57},
    # Conversion factors for light cream: teaspoon, tablespoon, splash, ounce to grams.
    "cream light": {"tsp": 5.0, "tbsp": 15.0, "splash": 30.0, "oz": 29.57},
    # Conversion factors for half and half: teaspoon, tablespoon, splash, ounce to grams.
    "half and half": {"tsp": 5.0, "tbsp": 15.0, "splash": 30.0, "oz": 29.57}, # ~1.0 g/ml
    # Conversion factors for half and half cream: teaspoon, tablespoon, splash, ounce to grams.
    "half and half cream": {"tsp": 5.0, "tbsp": 15.0, "splash": 30.0, "oz": 29.57},
    # Conversion factors for mascarpone: teaspoon, tablespoon, ounce to grams.
    "mascarpone": {"tsp": 5.0, "tbsp": 15.0, "oz": 28.35}, # High fat, ~1.0 g/ml
    # Conversion factors for labneh: teaspoon, tablespoon, ounce to grams.
    "labneh":     {"tsp": 5.1, "tbsp": 15.3, "oz": 28.35}, # Strained yogurt
    # Conversion factors for generic pesto: teaspoon, tablespoon, ounce to grams.
    "pesto":      {"tsp": 4.8, "tbsp": 14.4, "oz": 28.35}, # Oil based, with solids
    # Conversion factors for basil pesto: teaspoon, tablespoon, ounce to grams.
    "pesto basil": {"tsp": 4.8, "tbsp": 14.4, "oz": 28.35},
    # Conversion factors for generic tapenade: teaspoon, tablespoon, ounce to grams.
    "tapenade":   {"tsp": 5.0, "tbsp": 15.0, "oz": 28.35}, # Olive based
    # Conversion factors for olive tapenade: teaspoon, tablespoon, ounce to grams.
    "tapenade olive": {"tsp": 5.0, "tbsp": 15.0, "oz": 28.35},
    # Conversion factors for generic tahini: teaspoon, tablespoon, ounce to grams.
    "tahini":     {"tsp": 5.0, "tbsp": 15.0, "oz": 28.35}, # Sesame paste, ~1.0 g/ml
    # Conversion factors for tahini paste: teaspoon, tablespoon, ounce to grams.
    "tahini paste": {"tsp": 5.0, "tbsp": 15.0, "oz": 28.35},
    # Conversion factors for hummus: teaspoon, tablespoon, ounce to grams.
    "hummus":     {"tsp": 5.1, "tbsp": 15.4, "oz": 28.35}, # ~1.03 g/ml
    # Conversion factors for guacamole: teaspoon, tablespoon, ounce to grams.
    "guacamole":  {"tsp": 5.0, "tbsp": 15.0, "oz": 28.35}, # Varies a lot, ~1.0 g/ml

    # Section for powder, spice, sugar, and baking ingredient conversions.
    # == Powders, Spices, Sugars, Baking (Densities vary greatly) ==
    # Conversion factors for generic flour: teaspoon, tablespoon, ounce, cup to grams.
    "flour":      {"tsp": 2.6, "tbsp": 8.0, "oz": 28.35, "cup": 120.0}, # All-purpose, sifted USDA
    # Conversion factors for all purpose white flour: teaspoon, tablespoon, ounce, cup to grams.
    "flour all purpose white": {"tsp": 2.6, "tbsp": 8.0, "oz": 28.35, "cup": 120.0},
    # Conversion factors for whole wheat flour: teaspoon, tablespoon, ounce, cup to grams.
    "flour whole wheat": {"tsp": 2.7, "tbsp": 8.1, "oz": 28.35, "cup": 120.0}, # Slightly denser
    # Conversion factors for almond flour: teaspoon, tablespoon, ounce, cup to grams.
    "flour almond": {"tsp": 2.5, "tbsp": 7.5, "oz": 28.35, "cup": 96.0}, # Lighter per cup
    # Conversion factors for coconut flour: teaspoon, tablespoon, ounce, cup to grams.
    "flour coconut": {"tsp": 2.3, "tbsp": 7.0, "oz": 28.35, "cup": 112.0}, # Absorbent
    # Conversion factors for generic sugar: teaspoon, tablespoon, packet, cube, ounce, cup to grams.
    "sugar":      {"tsp": 4.2, "tbsp": 12.5, "packet": 4.0, "cube": 2.5, "oz": 28.35, "cup": 200.0}, # Granulated white USDA
    # Conversion factors for white granulated sugar: teaspoon, tablespoon, packet, cube, ounce, cup to grams.
    "sugar white granulated": {"tsp": 4.2, "tbsp": 12.5, "packet": 4.0, "cube": 2.5, "oz": 28.35, "cup": 200.0},
    # Conversion factors for brown sugar: teaspoon, tablespoon, ounce, cup to grams.
    "brown sugar": {"tsp": 4.6, "tbsp": 13.8, "oz": 28.35, "cup": 213.0}, # Packed USDA
    # Conversion factors for powdered confectioners sugar: teaspoon, tablespoon, ounce, cup to grams.
    "sugar powdered confectioners": {"tsp": 2.5, "tbsp": 7.5, "oz": 28.35, "cup": 120.0}, # Unsifted USDA
    # Conversion factors for raw turbinado sugar: teaspoon, tablespoon, packet, ounce, cup to grams.
    "sugar raw turbinado": {"tsp": 4.0, "tbsp": 12.0, "packet": 4.0, "oz": 28.35, "cup": 190.0}, # Less dense than granulated
    # Conversion factors for coconut sugar: teaspoon, tablespoon, ounce, cup to grams.
    "coconut sugar": {"tsp": 3.5, "tbsp": 10.5, "oz": 28.35, "cup": 168.0}, # Lighter than brown sugar
    # Conversion factors for salt: teaspoon, tablespoon, pinch to grams.
    "salt":       {"tsp": 6.0, "tbsp": 18.0, "pinch": 0.35}, # Table salt USDA
    # Conversion factors for generic pepper: teaspoon, tablespoon, pinch to grams.
    "pepper":     {"tsp": 2.3, "tbsp": 7.0, "pinch": 0.2}, # Ground black pepper USDA
    # Conversion factors for black pepper: teaspoon, tablespoon, pinch to grams.
    "pepper black": {"tsp": 2.3, "tbsp": 7.0, "pinch": 0.2},
    # Conversion factors for generic spice: teaspoon, tablespoon, pinch to grams.
    "spice":      {"tsp": 2.0, "tbsp": 6.0, "pinch": 0.25}, # Generic ground spice avg
    # Conversion factors for generic dried herbs: teaspoon, tablespoon, pinch to grams.
    "dried herbs": {"tsp": 0.5, "tbsp": 1.5, "pinch": 0.15}, # Generic dried leaf herb avg (e.g., oregano, basil)
    # Conversion factors for generic herb: teaspoon, tablespoon, pinch to grams.
    "herb":       {"tsp": 0.5, "tbsp": 1.5, "pinch": 0.15},
    # Conversion factors for garlic powder: teaspoon, tablespoon to grams.
    "garlic powder": {"tsp": 3.1, "tbsp": 9.3}, # USDA
    # Conversion factors for onion powder: teaspoon, tablespoon to grams.
    "onion powder": {"tsp": 2.4, "tbsp": 7.2}, # USDA
    # Conversion factors for paprika: teaspoon, tablespoon to grams.
    "paprika":    {"tsp": 2.3, "tbsp": 6.9}, # USDA
    # Conversion factors for chili powder: teaspoon, tablespoon to grams.
    "chili powder": {"tsp": 2.5, "tbsp": 7.5}, # Blend, varies
    # Conversion factors for cumin: teaspoon, tablespoon to grams.
    "cumin":      {"tsp": 2.1, "tbsp": 6.2}, # Ground USDA
    # Conversion factors for cinnamon: teaspoon, tablespoon to grams.
    "cinnamon":   {"tsp": 2.6, "tbsp": 7.8}, # Ground USDA
    # Conversion factors for generic cocoa powder: teaspoon, tablespoon, ounce, cup to grams.
    "cocoa powder": {"tsp": 2.5, "tbsp": 7.5, "oz": 28.35, "cup": 86.0}, # Unsweetened USDA
    # Conversion factors for unsweetened cocoa powder: teaspoon, tablespoon, ounce, cup to grams.
    "cocoa powder unsweetened": {"tsp": 2.5, "tbsp": 7.5, "oz": 28.35, "cup": 86.0},
    # Conversion factors for corn starch: teaspoon, tablespoon, ounce, cup to grams.
    "corn starch": {"tsp": 2.6, "tbsp": 8.0, "oz": 28.35, "cup": 128.0}, # USDA
    # Conversion factors for baking soda: teaspoon, tablespoon to grams.
    "baking soda": {"tsp": 4.6, "tbsp": 13.8}, # USDA
    # Conversion factors for baking powder: teaspoon, tablespoon to grams.
    "baking powder": {"tsp": 3.8, "tbsp": 11.4}, # USDA double acting
    # Conversion factors for generic yeast: teaspoon, tablespoon, packet to grams.
    "yeast":      {"tsp": 2.8, "tbsp": 8.4, "packet": 7.0}, # Active dry USDA, packet=0.25oz
    # Conversion factors for active dry yeast: teaspoon, tablespoon, packet to grams.
    "yeast active dry": {"tsp": 2.8, "tbsp": 8.4, "packet": 7.0},
    # Conversion factors for generic protein powder: teaspoon, tablespoon, scoop, ounce to grams.
    "protein powder": {"tsp": 3.0, "tbsp": 9.0, "scoop": 30.0, "oz": 28.35}, # Scoop size varies wildly, 30g is common ref
    # Conversion factors for nutritional yeast: teaspoon, tablespoon, ounce to grams.
    "nutritional yeast": {"tsp": 2.0, "tbsp": 6.0, "oz": 28.35}, # Flakes are light
    # Conversion factors for generic gelatin: teaspoon, tablespoon, packet to grams.
    "gelatin":    {"tsp": 3.0, "tbsp": 9.0, "packet": 7.0}, # Unflavored powder, packet=0.25oz
    # Conversion factors for unflavored gelatin powder: teaspoon, tablespoon, packet to grams.
    "gelatin powder unflavored": {"tsp": 3.0, "tbsp": 9.0, "packet": 7.0},

    # Section for sauce and condiment conversions.
    # == Sauces & Condiments ==
    # Conversion factors for ketchup: teaspoon, tablespoon, packet, ounce to grams.
    "ketchup":    {"tsp": 5.7, "tbsp": 17.0, "packet": 9.0, "oz": 28.35}, # USDA
    # Conversion factors for generic mustard: teaspoon, tablespoon, packet, ounce to grams.
    "mustard":    {"tsp": 5.3, "tbsp": 16.0, "packet": 5.0, "oz": 28.35}, # Yellow mustard USDA
    # Conversion factors for yellow mustard: teaspoon, tablespoon, packet, ounce to grams.
    "mustard yellow": {"tsp": 5.3, "tbsp": 16.0, "packet": 5.0, "oz": 28.35},
    # Conversion factors for dijon mustard: teaspoon, tablespoon, packet, ounce to grams.
    "mustard dijon": {"tsp": 5.3, "tbsp": 16.0, "packet": 5.0, "oz": 28.35},
    # Conversion factors for stone ground mustard: teaspoon, tablespoon, packet, ounce to grams.
    "mustard stone ground": {"tsp": 5.3, "tbsp": 16.0, "packet": 5.0, "oz": 28.35},
    # Conversion factors for honey mustard: teaspoon, tablespoon, packet, ounce to grams.
    "mustard honey": {"tsp": 6.0, "tbsp": 18.0, "packet": 7.0, "oz": 28.35}, # Higher sugar
    # Conversion factors for generic relish: teaspoon, tablespoon, ounce to grams.
    "relish":     {"tsp": 5.0, "tbsp": 15.0, "oz": 28.35}, # Sweet pickle relish USDA
    # Conversion factors for sweet pickle relish: teaspoon, tablespoon, ounce to grams.
    "relish sweet pickle": {"tsp": 5.0, "tbsp": 15.0, "oz": 28.35},
    # Conversion factors for generic bbq sauce: teaspoon, tablespoon, ounce to grams.
    "bbq sauce":  {"tsp": 6.0, "tbsp": 18.0, "oz": 28.35}, # Varies, avg density ~1.2 g/ml
    # Conversion factors for original bbq sauce: teaspoon, tablespoon, ounce to grams.
    "bbq sauce original": {"tsp": 6.0, "tbsp": 18.0, "oz": 28.35},
    # Conversion factors for honey bbq sauce: teaspoon, tablespoon, ounce to grams.
    "bbq sauce honey": {"tsp": 6.0, "tbsp": 18.0, "oz": 28.35},
    # Conversion factors for generic hot sauce: teaspoon, tablespoon, ounce, dash to grams.
    "hot sauce":  {"tsp": 5.0, "tbsp": 15.0, "oz": 29.57, "dash": 1.0}, # Mostly liquid, e.g., Tabasco, Frank's
    # Conversion factors for cayenne pepper hot sauce: teaspoon, tablespoon, ounce, dash to grams.
    "hot sauce cayenne pepper": {"tsp": 5.0, "tbsp": 15.0, "oz": 29.57, "dash": 1.0},
    # Conversion factors for chipotle hot sauce: teaspoon, tablespoon, ounce, dash to grams.
    "hot sauce chipotle": {"tsp": 5.0, "tbsp": 15.0, "oz": 29.57, "dash": 1.0},
    # Conversion factors for sriracha: teaspoon, tablespoon, ounce to grams.
    "sriracha":   {"tsp": 5.5, "tbsp": 16.5, "oz": 28.35}, # Slightly thicker
    # Conversion factors for sriracha sauce: teaspoon, tablespoon, ounce to grams.
    "sriracha sauce": {"tsp": 5.5, "tbsp": 16.5, "oz": 28.35},
    # Conversion factors for gochujang: teaspoon, tablespoon, ounce to grams.
    "gochujang":  {"tsp": 6.0, "tbsp": 18.0, "oz": 28.35}, # Thick paste
    # Conversion factors for gochujang paste: teaspoon, tablespoon, ounce to grams.
    "gochujang paste": {"tsp": 6.0, "tbsp": 18.0, "oz": 28.35},
    # Conversion factors for generic chili sauce: teaspoon, tablespoon, ounce to grams.
    "chili sauce": {"tsp": 5.5, "tbsp": 16.5, "oz": 28.35}, # Generic chili garlic type
    # Conversion factors for sweet thai chili sauce: teaspoon, tablespoon, ounce to grams.
    "chili sauce sweet thai": {"tsp": 6.0, "tbsp": 18.0, "oz": 28.35}, # Higher sugar
    # Conversion factors for chili garlic sauce: teaspoon, tablespoon, ounce to grams.
    "chili garlic sauce": {"tsp": 5.5, "tbsp": 16.5, "oz": 28.35},
    # Conversion factors for generic soy sauce: teaspoon, tablespoon, packet, ounce to grams.
    "soy sauce":  {"tsp": 5.5, "tbsp": 16.5, "packet": 8.0, "oz": 29.57}, # ~1.1 g/ml USDA
    # Conversion factors for regular soy sauce: teaspoon, tablespoon, packet, ounce to grams.
    "soy sauce regular": {"tsp": 5.5, "tbsp": 16.5, "packet": 8.0, "oz": 29.57},
    # Conversion factors for low sodium soy sauce: teaspoon, tablespoon, packet, ounce to grams.
    "soy sauce low sodium": {"tsp": 5.5, "tbsp": 16.5, "packet": 8.0, "oz": 29.57},
    # Conversion factors for tamari: teaspoon, tablespoon, packet, ounce to grams.
    "tamari":     {"tsp": 5.5, "tbsp": 16.5, "packet": 8.0, "oz": 29.57}, # Similar to soy sauce
    # Conversion factors for teriyaki sauce: teaspoon, tablespoon, ounce to grams.
    "teriyaki sauce": {"tsp": 5.5, "tbsp": 16.5, "oz": 28.35}, # Varies, can be thick
    # Conversion factors for hoisin sauce: teaspoon, tablespoon, ounce to grams.
    "hoisin sauce": {"tsp": 6.0, "tbsp": 18.0, "oz": 28.35}, # Thick paste
    # Conversion factors for oyster sauce: teaspoon, tablespoon, ounce to grams.
    "oyster sauce": {"tsp": 5.8, "tbsp": 17.4, "oz": 28.35}, # Thick
    # Conversion factors for fish sauce: teaspoon, tablespoon, ounce to grams.
    "fish sauce": {"tsp": 5.2, "tbsp": 15.6, "oz": 29.57}, # Salty liquid
    # Conversion factors for worcestershire sauce: teaspoon, tablespoon, ounce to grams.
    "worcestershire sauce": {"tsp": 5.1, "tbsp": 15.3, "oz": 29.57}, # Liquid
    # Conversion factors for generic steak sauce: teaspoon, tablespoon, ounce to grams.
    "steak sauce": {"tsp": 5.5, "tbsp": 16.5, "oz": 28.35}, # E.g., A1 type
    # Conversion factors for generic salsa: teaspoon, tablespoon, ounce, cup to grams.
    "salsa":      {"tsp": 5.0, "tbsp": 15.0, "oz": 28.35, "cup": 240.0}, # Chunky varies, ~1.0 g/ml avg
    # Conversion factors for pico de gallo salsa: teaspoon, tablespoon, ounce, cup to grams.
    "salsa pico de gallo": {"tsp": 4.5, "tbsp": 13.5, "oz": 28.35, "cup": 220.0}, # Less liquid
    # Conversion factors for mild jarred salsa: teaspoon, tablespoon, ounce, cup to grams.
    "salsa jarred mild": {"tsp": 5.0, "tbsp": 15.0, "oz": 28.35, "cup": 240.0},
    # Conversion factors for salsa verde: teaspoon, tablespoon, ounce, cup to grams.
    "salsa verde": {"tsp": 5.0, "tbsp": 15.0, "oz": 28.35, "cup": 240.0},
    # Conversion factors for marinara sauce: teaspoon, tablespoon, ounce, cup to grams.
    "marinara sauce": {"tsp": 5.1, "tbsp": 15.3, "oz": 28.35, "cup": 245.0}, # USDA
    # Conversion factors for generic alfredo sauce: teaspoon, tablespoon, ounce, cup to grams.
    "alfredo sauce": {"tsp": 5.0, "tbsp": 15.0, "oz": 28.35, "cup": 240.0}, # Varies, ~1.0 g/ml avg
    # Conversion factors for jarred alfredo sauce: teaspoon, tablespoon, ounce, cup to grams.
    "alfredo sauce jarred": {"tsp": 5.0, "tbsp": 15.0, "oz": 28.35, "cup": 240.0},
    # Conversion factors for vodka sauce: teaspoon, tablespoon, ounce, cup to grams.
    "vodka sauce": {"tsp": 5.0, "tbsp": 15.0, "oz": 28.35, "cup": 240.0}, # Creamy tomato
    # Conversion factors for generic gravy: teaspoon, tablespoon, ounce, cup to grams.
    "gravy":      {"tsp": 5.0, "tbsp": 15.0, "oz": 28.35, "cup": 240.0}, # Canned/jarred avg
    # Conversion factors for brown gravy: teaspoon, tablespoon, ounce, cup to grams.
    "gravy brown": {"tsp": 5.0, "tbsp": 15.0, "oz": 28.35, "cup": 240.0},
    # Conversion factors for jarred brown gravy: teaspoon, tablespoon, ounce, cup to grams.
    "gravy brown jarred": {"tsp": 5.0, "tbsp": 15.0, "oz": 28.35, "cup": 240.0},
    # Conversion factors for chicken gravy: teaspoon, tablespoon, ounce, cup to grams.
    "gravy chicken": {"tsp": 5.0, "tbsp": 15.0, "oz": 28.35, "cup": 240.0},
    # Conversion factors for jarred chicken gravy: teaspoon, tablespoon, ounce, cup to grams.
    "gravy chicken jarred": {"tsp": 5.0, "tbsp": 15.0, "oz": 28.35, "cup": 240.0},
    # Conversion factors for country white gravy: teaspoon, tablespoon, ounce, cup to grams.
    "gravy country white": {"tsp": 5.0, "tbsp": 15.0, "oz": 28.35, "cup": 240.0}, # Milk based
    # Conversion factors for generic dressing: teaspoon, tablespoon, packet, ounce to grams.
    "dressing":   {"tsp": 4.8, "tbsp": 14.5, "packet": 28.0, "oz": 28.35}, # Generic avg
    # Conversion factors for ranch dressing: teaspoon, tablespoon, packet, ounce to grams.
    "ranch dressing": {"tsp": 4.8, "tbsp": 14.5, "packet": 28.0, "oz": 28.35}, # Regular USDA ~0.97 g/ml
    # Conversion factors for regular ranch dressing: teaspoon, tablespoon, packet, ounce to grams.
    "ranch dressing regular": {"tsp": 4.8, "tbsp": 14.5, "packet": 28.0, "oz": 28.35},
    # Conversion factors for light ranch dressing: teaspoon, tablespoon, packet, ounce to grams.
    "ranch dressing light": {"tsp": 4.9, "tbsp": 14.7, "packet": 28.0, "oz": 28.35}, # More water
    # Conversion factors for caesar dressing: teaspoon, tablespoon, packet, ounce to grams.
    "caesar dressing": {"tsp": 4.9, "tbsp": 14.7, "packet": 28.0, "oz": 28.35}, # Creamy USDA
    # Conversion factors for italian dressing: teaspoon, tablespoon, packet, ounce to grams.
    "italian dressing": {"tsp": 4.7, "tbsp": 14.0, "packet": 28.0, "oz": 28.35}, # Regular USDA ~0.94 g/ml
    # Conversion factors for generic vinaigrette: teaspoon, tablespoon, packet, ounce to grams.
    "vinaigrette": {"tsp": 4.7, "tbsp": 14.0, "packet": 28.0, "oz": 28.35}, # Generic oil/vinegar mix
    # Conversion factors for balsamic vinaigrette: teaspoon, tablespoon, packet, ounce to grams.
    "vinaigrette balsamic": {"tsp": 4.7, "tbsp": 14.0, "packet": 28.0, "oz": 28.35},
    # Conversion factors for blue cheese dressing: teaspoon, tablespoon, packet, ounce to grams.
    "blue cheese dressing": {"tsp": 4.9, "tbsp": 14.7, "packet": 28.0, "oz": 28.35}, # USDA
    # Conversion factors for thousand island dressing: teaspoon, tablespoon, packet, ounce to grams.
    "thousand island dressing": {"tsp": 5.1, "tbsp": 15.3, "packet": 28.0, "oz": 28.35}, # USDA
    # Conversion factors for french dressing: teaspoon, tablespoon, packet, ounce to grams.
    "french dressing": {"tsp": 5.0, "tbsp": 15.0, "packet": 28.0, "oz": 28.35}, # USDA
    # Conversion factors for honey dijon dressing: teaspoon, tablespoon, packet, ounce to grams.
    "honey dijon dressing": {"tsp": 5.2, "tbsp": 15.6, "packet": 28.0, "oz": 28.35}, # Higher sugar
    # Conversion factors for poppy seed dressing: teaspoon, tablespoon, packet, ounce to grams.
    "poppy seed dressing": {"tsp": 5.0, "tbsp": 15.0, "packet": 28.0, "oz": 28.35},
    # Conversion factors for sesame ginger dressing: teaspoon, tablespoon, packet, ounce to grams.
    "sesame ginger dressing": {"tsp": 4.9, "tbsp": 14.7, "packet": 28.0, "oz": 28.35},
    # Conversion factors for honey: teaspoon, tablespoon, packet, ounce to grams.
    "honey":      {"tsp": 7.0, "tbsp": 21.0, "packet": 7.0, "oz": 28.35}, # Dense ~1.4 g/ml USDA
    # Conversion factors for generic syrup: teaspoon, tablespoon, ounce to grams.
    "syrup":      {"tsp": 6.6, "tbsp": 20.0, "oz": 29.57}, # Generic pancake syrup ~1.3 g/ml
    # Conversion factors for maple syrup: teaspoon, tablespoon, ounce to grams.
    "maple syrup": {"tsp": 6.6, "tbsp": 20.0, "oz": 29.57}, # ~1.32 g/ml USDA
    # Conversion factors for pure maple syrup: teaspoon, tablespoon, ounce to grams.
    "maple syrup pure": {"tsp": 6.6, "tbsp": 20.0, "oz": 29.57},
    # Conversion factors for agave nectar: teaspoon, tablespoon, ounce to grams.
    "agave nectar": {"tsp": 6.9, "tbsp": 20.7, "oz": 28.35}, # Dense ~1.38 g/ml
    # Conversion factors for molasses: teaspoon, tablespoon, ounce to grams.
    "molasses":   {"tsp": 7.0, "tbsp": 21.0, "oz": 28.35}, # ~1.4 g/ml USDA
    # Conversion factors for generic corn syrup: teaspoon, tablespoon, ounce to grams.
    "corn syrup": {"tsp": 7.0, "tbsp": 21.0, "oz": 28.35}, # ~1.4 g/ml
    # Conversion factors for light corn syrup: teaspoon, tablespoon, ounce to grams.
    "corn syrup light": {"tsp": 7.0, "tbsp": 21.0, "oz": 28.35},
    # Conversion factors for simple syrup: teaspoon, tablespoon, ounce to grams.
    "simple syrup": {"tsp": 6.3, "tbsp": 18.9, "oz": 29.57}, # 1:1 ratio ~1.25 g/ml
    # Conversion factors for generic vinegar: teaspoon, tablespoon, ounce to grams.
    "vinegar":    {"tsp": 5.0, "tbsp": 15.0, "oz": 29.57}, # ~1.01 g/ml (White Distilled USDA)
    # Conversion factors for white vinegar: teaspoon, tablespoon, ounce to grams.
    "vinegar white": {"tsp": 5.0, "tbsp": 15.0, "oz": 29.57},
    # Conversion factors for apple cider vinegar: teaspoon, tablespoon, ounce to grams.
    "vinegar apple cider": {"tsp": 5.0, "tbsp": 15.0, "oz": 29.57}, # ~1.01 g/ml USDA
    # Conversion factors for balsamic vinegar: teaspoon, tablespoon, ounce to grams.
    "vinegar balsamic": {"tsp": 5.2, "tbsp": 15.6, "oz": 29.57}, # Slightly denser ~1.05 g/ml
    # Conversion factors for red wine vinegar: teaspoon, tablespoon, ounce to grams.
    "vinegar red wine": {"tsp": 5.0, "tbsp": 15.0, "oz": 29.57}, # ~1.01 g/ml USDA
    # Conversion factors for lemon juice: teaspoon, tablespoon, ounce to grams.
    "lemon juice": {"tsp": 5.0, "tbsp": 15.0, "oz": 29.57}, # ~1.03 g/ml USDA
    # Conversion factors for lime juice: teaspoon, tablespoon, ounce to grams.
    "lime juice": {"tsp": 5.0, "tbsp": 15.0, "oz": 29.57}, # ~1.02 g/ml USDA

    # Section for grain, pasta, rice, and cereal conversions (mostly cooked weights).
    # == Grains, Pasta, Rice, Cereals (Cooked weights unless noted) ==
    # Conversion factors for generic pasta: ounce, cup to grams.
    "pasta":      {"oz": 28.35, "cup": 140.0}, # Cooked generic reference
    # Conversion factors for plain cooked pasta: ounce, cup to grams.
    "pasta plain cooked": {"oz": 28.35, "cup": 140.0}, # Cooked spaghetti example USDA
    # Conversion factors for generic rice: ounce, cup to grams.
    "rice":       {"oz": 28.35, "cup": 158.0}, # Cooked generic white reference
    # Conversion factors for cooked white rice: ounce, cup to grams.
    "rice white cooked": {"oz": 28.35, "cup": 158.0}, # Long grain USDA
    # Conversion factors for cooked brown rice: ounce, cup to grams.
    "rice brown cooked": {"oz": 28.35, "cup": 195.0}, # Long grain USDA
    # Conversion factors for white rice side portion: ounce, cup to grams.
    "rice white side": {"oz": 28.35, "cup": 158.0}, # Use S/M/L from CSV for typical side portion
    # Conversion factors for brown rice side portion: ounce, cup to grams.
    "rice brown side": {"oz": 28.35, "cup": 195.0}, # Use S/M/L from CSV
    # Conversion factors for rice pilaf: ounce, cup to grams.
    "rice pilaf": {"oz": 28.35, "cup": 170.0}, # Cooked, varies
    # Conversion factors for fried rice: ounce, cup to grams.
    "fried rice": {"oz": 28.35, "cup": 170.0}, # Cooked, varies
    # Conversion factors for risotto: ounce, cup to grams.
    "risotto":    {"oz": 28.35, "cup": 210.0}, # Cooked, dense
    # Conversion factors for paella: ounce, cup to grams.
    "paella":     {"oz": 28.35, "cup": 200.0}, # Cooked, varies
    # Conversion factors for biryani: ounce, cup to grams.
    "biryani":    {"oz": 28.35, "cup": 200.0}, # Cooked, varies
    # Conversion factors for generic quinoa: ounce, cup to grams.
    "quinoa":     {"oz": 28.35, "cup": 185.0}, # Cooked USDA
    # Conversion factors for cooked quinoa: ounce, cup to grams.
    "quinoa cooked": {"oz": 28.35, "cup": 185.0},
    # Conversion factors for generic couscous: ounce, cup to grams.
    "couscous":   {"oz": 28.35, "cup": 157.0}, # Cooked USDA
    # Conversion factors for cooked couscous: ounce, cup to grams.
    "couscous cooked": {"oz": 28.35, "cup": 157.0},
    # Conversion factors for generic oatmeal: ounce, packet, cup to grams.
    "oatmeal":    {"oz": 28.35, "packet": 40.0, "cup": 234.0}, # Cooked with water USDA, packet=dry weight ref
    # Conversion factors for plain oatmeal: ounce, packet, cup to grams.
    "oatmeal plain": {"oz": 28.35, "packet": 40.0, "cup": 234.0},
    # Conversion factors for generic cereal: ounce, cup to grams (dry weight).
    "cereal":     {"oz": 28.35, "cup": 30.0}, # DRY weight, varies hugely, generic flakes ref
    # Conversion factors for generic flake cereal: ounce, cup to grams (dry weight).
    "cereal generic flakes": {"oz": 28.35, "cup": 30.0}, # E.g., corn flakes
    # Conversion factors for granola cereal: ounce, teaspoon, tablespoon, cup to grams (dry weight).
    "cereal granola":    {"oz": 28.35, "tsp": 4.0, "tbsp": 12.0, "cup": 100.0}, # DRY, dense, homemade ref
    # Conversion factors for shredded wheat cereal: ounce, biscuit, cup to grams (dry weight).
    "cereal shredded wheat": {"oz": 28.35, "biscuit": 23.0, "cup": 45.0}, # Large biscuit USDA
    # Conversion factors for generic bread crumbs: ounce, teaspoon, tablespoon, cup to grams.
    "bread crumbs": {"oz": 28.35, "tsp": 1.8, "tbsp": 5.5, "cup": 108.0}, # Dry, plain USDA
    # Conversion factors for plain bread crumbs: ounce, teaspoon, tablespoon, cup to grams.
    "bread crumbs plain": {"oz": 28.35, "tsp": 1.8, "tbsp": 5.5, "cup": 108.0},
    # Conversion factors for italian bread crumbs: ounce, teaspoon, tablespoon, cup to grams.
    "bread crumbs italian": {"oz": 28.35, "tsp": 1.9, "tbsp": 5.7, "cup": 110.0}, # Slightly denser due to seasoning
    # Conversion factors for panko bread crumbs: ounce, teaspoon, tablespoon, cup to grams.
    "panko bread crumbs": {"oz": 28.35, "tsp": 0.8, "tbsp": 2.5, "cup": 50.0}, # Dry, very light
    # Conversion factors for generic croutons: ounce, teaspoon, tablespoon, piece, cup to grams.
    "croutons":   {"oz": 28.35, "tsp": 0.5, "tbsp": 1.5, "piece": 1.5, "cup": 30.0}, # Plain/garlic USDA
    # Conversion factors for garlic herb croutons: ounce, teaspoon, tablespoon, piece, cup to grams.
    "croutons garlic herb": {"oz": 28.35, "tsp": 0.5, "tbsp": 1.5, "piece": 1.5, "cup": 30.0},

    # Section for meat, poultry, fish, egg, and tofu conversions (mostly cooked weights).
    # == Meats, Poultry, Fish, Eggs, Tofu (Cooked weights unless noted) ==
    # Conversion factors for generic chicken: ounce, tablespoon chopped to grams.
    "chicken":    {"oz": 28.35, "tbsp chopped": 9.0}, # Generic cooked reference, chopped tbsp
    # Conversion factors for grilled chicken breast: ounce, each to grams.
    "grilled chicken breast": {"oz": 28.35, "each": 170.0}, # Average ~6oz raw -> cooked breast weight
    # Conversion factors for roasted chicken: ounce, quarter, piece to grams.
    "roasted chicken": {"oz": 28.35, "quarter": 250.0, "piece": 150.0}, # Mixed pieces ref, use S/M/L
    # Conversion factors for fried chicken pieces: ounce, wing, thigh, leg, breast to grams.
    "fried chicken": {"oz": 28.35, "wing": 45.0, "thigh": 130.0, "leg": 150.0, "breast": 220.0}, # Weights include bone/skin/breading
    # Conversion factors for chicken wings: ounce, wing, each to grams.
    "chicken wings": {"oz": 28.35, "wing": 35.0, "each": 35.0}, # Cooked wing flat/drumette avg weight USDA
    # Conversion factors for chicken stir-fry: ounce, cup to grams.
    "chicken stir-fry": {"oz": 28.35, "cup": 180.0}, # Mixed dish reference, use S/M/L
    # Conversion factors for chicken thigh: ounce, each to grams.
    "chicken thigh": {"oz": 28.35, "each": 100.0}, # Boneless, skinless cooked USDA avg
    # Conversion factors for chicken leg: ounce, each to grams.
    "chicken leg": {"oz": 28.35, "each": 120.0}, # Drumstick + thigh portion, bone-in cooked avg
    # Conversion factors for chicken strip: ounce, each to grams.
    "chicken strip": {"oz": 28.35, "each": 30.0}, # Cooked tender/strip avg
    # Conversion factors for generic turkey: ounce, slice to grams.
    "turkey":     {"oz": 28.35, "slice": 28.0}, # Deli slice reference
    # Conversion factors for roasted turkey breast: ounce, slice to grams.
    "turkey breast roasted": {"oz": 28.35, "slice": 28.0}, # Deli slice ref, use S/M/L for roast portion
    # Conversion factors for cooked ground turkey: ounce, tablespoon, cup to grams.
    "ground turkey cooked": {"oz": 28.35, "tbsp": 9.0, "cup": 135.0}, # 93% lean, crumbled USDA
    # Conversion factors for generic beef: ounce, strip, cube, tablespoon minced to grams.
    "beef":       {"oz": 28.35, "strip": 30.0, "cube": 15.0, "tbsp minced": 10.0}, # Cooked references
    # Conversion factors for generic steak: ounce to grams.
    "steak":      {"oz": 28.35}, # Use S/M/L for whole steak via CSV
    # Conversion factors for steak (with trailing space): ounce to grams.
    "steak ": {"oz": 28.35},
    # Conversion factors for roast beef: ounce, slice to grams.
    "roast beef": {"oz": 28.35, "slice": 28.0}, # Deli slice reference
    # Conversion factors for beef stir-fry: ounce, cup to grams.
    "beef stir-fry": {"oz": 28.35, "cup": 190.0}, # Mixed dish reference, use S/M/L
    # Conversion factors for cooked ground beef: ounce, patty, tablespoon, cup to grams.
    "ground beef cooked": {"oz": 28.35, "patty": 113.0, "tbsp": 9.0, "cup": 135.0}, # 85% lean, crumbled USDA. Patty=4oz raw->cooked
    # Conversion factors for cooked hamburger patty: ounce, each to grams.
    "hamburger patty cooked": {"oz": 28.35, "each": 113.0}, # Assumes 4oz raw patty cooked
    # Conversion factors for generic pork: ounce, strip, cube, tablespoon minced to grams.
    "pork":       {"oz": 28.35, "strip": 30.0, "cube": 15.0, "tbsp minced": 10.0}, # Cooked references
    # Conversion factors for generic pork chop: ounce, each to grams.
    "pork chop":  {"oz": 28.35, "each": 170.0}, # Average bone-in cooked chop (~6oz raw)
    # Conversion factors for cooked pork chop: ounce, each to grams.
    "pork chop cooked": {"oz": 28.35, "each": 170.0},
    # Conversion factors for pork tenderloin: ounce, slice, medallion to grams.
    "pork tenderloin": {"oz": 28.35, "slice": 40.0, "medallion": 40.0}, # Cooked ~1 inch slice
    # Conversion factors for pulled pork: ounce, cup to grams.
    "pulled pork": {"oz": 28.35, "cup": 140.0}, # Cooked, packed lightly
    # Conversion factors for generic ham: ounce, slice to grams.
    "ham":        {"oz": 28.35, "slice": 28.0}, # Deli slice reference
    # Conversion factors for generic bacon: strip, slice, ounce, bit to grams.
    "bacon":      {"strip": 8.0, "slice": 8.0, "oz": 28.35, "bit": 1.0}, # Cooked, average thickness USDA
    # Conversion factors for bacon strip: each, ounce to grams.
    "bacon strip": {"each": 8.0, "oz": 28.35},
    # Conversion factors for bacon bits: teaspoon, tablespoon, ounce to grams.
    "bacon bits": {"tsp": 1.5, "tbsp": 4.5, "oz": 28.35}, # Real bacon bits
    # Conversion factors for generic sausage: link, patty, ounce to grams.
    "sausage":    {"link": 55.0, "patty": 50.0, "oz": 28.35}, # Cooked breakfast refs
    # Conversion factors for cooked sausage: link, patty, ounce to grams.
    "sausage cooked": {"link": 55.0, "patty": 50.0, "oz": 28.35},
    # Conversion factors for breakfast sausage link: link, ounce to grams.
    "breakfast sausage link": {"link": 25.0, "oz": 28.35}, # Smaller link USDA
    # Conversion factors for cooked italian sausage: link, ounce to grams.
    "sausage italian cooked": {"link": 80.0, "oz": 28.35}, # Cooked avg link
    # Conversion factors for bratwurst: link, ounce to grams.
    "bratwurst":  {"link": 85.0, "oz": 28.35}, # Cooked avg link
    # Conversion factors for generic lamb: ounce, chop, cube to grams.
    "lamb":       {"oz": 28.35, "chop": 100.0, "cube": 15.0}, # Cooked references
    # Conversion factors for lamb chop: ounce, each to grams.
    "lamb chop":  {"oz": 28.35, "each": 100.0}, # Cooked loin chop avg
    # Conversion factors for kebab meat: skewer, ounce to grams.
    "kebab meat": {"skewer": 100.0, "oz": 28.35}, # Meat only weight est.
    # Conversion factors for meatloaf: slice, ounce to grams.
    "meatloaf":   {"slice": 120.0, "oz": 28.35}, # Avg slice ~1 inch thick
    # Conversion factors for generic fish: ounce, fillet to grams.
    "fish":       {"oz": 28.35, "fillet": 140.0}, # Generic cooked fillet ref ~5oz
    # Conversion factors for cooked fish: ounce, fillet to grams.
    "fish cooked": {"oz": 28.35, "fillet": 140.0},
    # Conversion factors for salmon: ounce, fillet, steak to grams.
    "salmon":     {"oz": 28.35, "fillet": 170.0, "steak": 170.0}, # Standard 6oz raw -> cooked fillet/steak
    # Conversion factors for cooked salmon: ounce, fillet, steak to grams.
    "salmon cooked": {"oz": 28.35, "fillet": 170.0, "steak": 170.0},
    # Conversion factors for generic tuna: ounce, steak, can to grams.
    "tuna":       {"oz": 28.35, "steak": 150.0, "can": 120.0}, # Steak=6oz raw->cooked, Can=5oz canned drained solids USDA
    # Conversion factors for cooked tuna: ounce, steak to grams.
    "tuna cooked": {"oz": 28.35, "steak": 150.0},
    # Conversion factors for cod: ounce, fillet to grams.
    "cod":        {"oz": 28.35, "fillet": 150.0}, # Cooked fillet ref ~5-6oz
    # Conversion factors for tilapia: ounce, fillet to grams.
    "tilapia":    {"oz": 28.35, "fillet": 120.0}, # Cooked fillet ref ~4-5oz
    # Conversion factors for fried fish fillet: ounce, each to grams.
    "fried fish fillet": {"oz": 28.35, "each": 100.0}, # Breaded, fried avg
    # Conversion factors for fish taco: each, ounce to grams.
    "fish taco":  {"each": 130.0, "oz": 28.35}, # Incl tortilla, toppings avg
    # Conversion factors for generic shrimp: ounce, each to grams.
    "shrimp":     {"oz": 28.35, "each": 8.0}, # Large shrimp, cooked, peeled (~16-20 count/lb raw) USDA
    # Conversion factors for cooked shrimp: ounce, each to grams.
    "shrimp cooked": {"oz": 28.35, "each": 8.0},
    # Conversion factors for generic scallop: ounce, each to grams.
    "scallop":    {"oz": 28.35, "each": 20.0}, # Large sea scallop, cooked USDA
    # Conversion factors for cooked scallops: ounce, each to grams.
    "scallops cooked": {"oz": 28.35, "each": 20.0},
    # Conversion factors for generic crab: ounce, leg to grams.
    "crab":       {"oz": 28.35, "leg": 100.0}, # Cooked leg meat estimate
    # Conversion factors for crab cake: each, ounce to grams.
    "crab cake":  {"each": 80.0, "oz": 28.35}, # Avg size cooked
    # Conversion factors for generic lobster: ounce, tail to grams.
    "lobster":    {"oz": 28.35, "tail": 120.0}, # Cooked tail meat ~4-5oz avg
    # Conversion factors for steamed lobster tail: each, ounce to grams.
    "lobster tail steamed": {"each": 120.0, "oz": 28.35},
    # Conversion factors for generic egg: each, ounce to grams.
    "egg":        {"each": 50.0, "oz": 28.35}, # Large egg, raw weight USDA (cooked weight similar)
    # Conversion factors for fried egg: each, ounce to grams.
    "fried egg":  {"each": 46.0, "oz": 28.35}, # Cooked weight USDA (slight loss)
    # Conversion factors for boiled egg: each, ounce to grams.
    "boiled egg": {"each": 50.0, "oz": 28.35}, # Cooked weight USDA
    # Conversion factors for poached egg: each, ounce to grams.
    "poached egg":{"each": 50.0, "oz": 28.35}, # Cooked weight USDA
    # Conversion factors for scrambled eggs: ounce, cup to grams.
    "scrambled eggs": {"oz": 28.35, "cup": 160.0}, # Cooked, ~3 large eggs per cup
    # Conversion factors for generic omelette: ounce to grams.
    "omelette":   {"oz": 28.35}, # Use S/M/L via CSV for size (e.g., 2-egg, 3-egg)
    # Conversion factors for generic tofu: ounce, slice, cube to grams.
    "tofu":       {"oz": 28.35, "slice": 40.0, "cube": 15.0}, # Firm tofu, slice ~1cm thick from standard block
    # Conversion factors for baked tofu: ounce, slice, cube to grams.
    "tofu baked": {"oz": 28.35, "slice": 35.0, "cube": 13.0}, # Loses some moisture
    # Conversion factors for tempeh: ounce, slice to grams.
    "tempeh":     {"oz": 28.35, "slice": 40.0}, # ~1cm thick slice

    # Section for cheese and dairy alternative conversions.
    # == Cheese & Dairy Alternatives ==
    # Conversion factors for generic cheese: ounce to grams.
    "cheese":     {"oz": 28.35}, # Generic, rely on specific types or S/M/L via CSV for general use
    # Conversion factors for generic cheddar: slice, tablespoon shredded, ounce, cube to grams.
    "cheddar":    {"slice": 21.0, "tbsp shredded": 7.0, "oz": 28.35, "cube": 7.0}, # Standard slice ~0.75oz USDA
    # Conversion factors for cheese cheddar: slice, tablespoon shredded, ounce, cube to grams.
    "cheese cheddar": {"slice": 21.0, "tbsp shredded": 7.0, "oz": 28.35, "cube": 7.0},
    # Conversion factors for generic mozzarella: slice, tablespoon shredded, ounce, ball to grams.
    "mozzarella": {"slice": 28.0, "tbsp shredded": 7.0, "oz": 28.35, "ball": 113.0}, # Slice ~1oz USDA (low moisture part skim), Ball = Fresh 4oz
    # Conversion factors for cheese mozzarella: slice, tablespoon shredded, ounce, ball to grams.
    "cheese mozzarella": {"slice": 28.0, "tbsp shredded": 7.0, "oz": 28.35, "ball": 113.0},
    # Conversion factors for generic swiss: slice, tablespoon shredded, ounce to grams.
    "swiss":      {"slice": 28.0, "tbsp shredded": 8.0, "oz": 28.35}, # Slice ~1oz USDA
    # Conversion factors for cheese swiss: slice, tablespoon shredded, ounce to grams.
    "cheese swiss": {"slice": 28.0, "tbsp shredded": 8.0, "oz": 28.35},
    # Conversion factors for generic provolone: slice, tablespoon shredded, ounce to grams.
    "provolone":  {"slice": 28.0, "tbsp shredded": 8.0, "oz": 28.35}, # Slice ~1oz USDA
    # Conversion factors for cheese provolone: slice, tablespoon shredded, ounce to grams.
    "cheese provolone": {"slice": 28.0, "tbsp shredded": 8.0, "oz": 28.35},
    # Conversion factors for american cheese: slice, ounce to grams.
    "american cheese": {"slice": 21.0, "oz": 28.35}, # Processed slice ~0.75oz
    # Conversion factors for cheese american: slice, ounce to grams.
    "cheese american": {"slice": 21.0, "oz": 28.35},
    # Conversion factors for generic parmesan: tablespoon grated, ounce, wedge to grams.
    "parmesan":   {"tbsp grated": 5.0, "oz": 28.35, "wedge": 28.35}, # Grated USDA, Wedge=1oz reference
    # Conversion factors for cheese parmesan: tablespoon grated, ounce, wedge to grams.
    "cheese parmesan": {"tbsp grated": 5.0, "oz": 28.35, "wedge": 28.35},
    # Conversion factors for generic feta: tablespoon crumbled, ounce, cube to grams.
    "feta":       {"tbsp crumbled": 7.0, "oz": 28.35, "cube": 7.0}, # USDA
    # Conversion factors for cheese feta: tablespoon crumbled, ounce, cube to grams.
    "cheese feta": {"tbsp crumbled": 7.0, "oz": 28.35, "cube": 7.0},
    # Conversion factors for generic goat cheese: tablespoon crumbled, ounce, log to grams.
    "goat cheese": {"tbsp crumbled": 7.5, "oz": 28.35, "log": 113.0}, # Soft goat cheese USDA, Log=4oz ref
    # Conversion factors for cheese goat: tablespoon crumbled, ounce, log to grams.
    "cheese goat": {"tbsp crumbled": 7.5, "oz": 28.35, "log": 113.0},
    # Conversion factors for generic blue cheese: tablespoon crumbled, ounce, wedge to grams.
    "blue cheese": {"tbsp crumbled": 8.8, "oz": 28.35, "wedge": 28.35}, # Crumbled USDA, Wedge=1oz ref
    # Conversion factors for cheese blue: tablespoon crumbled, ounce, wedge to grams.
    "cheese blue": {"tbsp crumbled": 8.8, "oz": 28.35, "wedge": 28.35},
    # Conversion factors for generic ricotta: teaspoon, tablespoon, ounce, cup to grams.
    "ricotta":    {"tsp": 6.0, "tbsp": 18.0, "oz": 28.35, "cup": 246.0}, # Whole milk USDA
    # Conversion factors for cheese ricotta: teaspoon, tablespoon, ounce, cup to grams.
    "cheese ricotta": {"tsp": 6.0, "tbsp": 18.0, "oz": 28.35, "cup": 246.0},
    # Conversion factors for generic cottage cheese: teaspoon, tablespoon, ounce, cup to grams.
    "cottage cheese": {"tsp": 6.0, "tbsp": 18.0, "oz": 28.35, "cup": 210.0}, # Lowfat 2% USDA
    # Conversion factors for cheese cottage: teaspoon, tablespoon, ounce, cup to grams.
    "cheese cottage": {"tsp": 6.0, "tbsp": 18.0, "oz": 28.35, "cup": 210.0},
    # Conversion factors for generic yogurt: teaspoon, tablespoon, ounce, cup to grams.
    "yogurt":     {"tsp": 6.0, "tbsp": 18.0, "oz": 28.35, "cup": 224.0}, # Plain standard yogurt USDA
    # Conversion factors for plain yogurt: teaspoon, tablespoon, ounce, cup to grams.
    "yogurt plain": {"tsp": 6.0, "tbsp": 18.0, "oz": 28.35, "cup": 224.0},
    # Conversion factors for greek yogurt: teaspoon, tablespoon, ounce, cup to grams.
    "greek yogurt": {"tsp": 6.0, "tbsp": 18.0, "oz": 28.35, "cup": 224.0}, # Plain, nonfat USDA
    # Conversion factors for plain greek yogurt: teaspoon, tablespoon, ounce, cup to grams.
    "greek yogurt plain": {"tsp": 6.0, "tbsp": 18.0, "oz": 28.35, "cup": 224.0},
    # Conversion factors for frozen yogurt: scoop, ounce, cup to grams.
    "frozen yoghurt": {"scoop": 70.0, "oz": 28.35, "cup": 174.0}, # Vanilla soft serve USDA

    # Section for fruit and vegetable conversions (mostly raw weights).
    # == Fruits & Vegetables (Raw weights unless noted) ==
    # Conversion factors for generic fruit: ounce, piece, cup to grams.
    "fruit":      {"oz": 28.35, "piece": 150.0, "cup": 150.0}, # Generic references
    # Conversion factors for apple: fruit, each, ounce, slice to grams.
    "apple":      {"fruit": 182.0, "each": 182.0, "oz": 28.35, "slice": 15.0}, # Medium raw with skin USDA
    # Conversion factors for banana: fruit, each, ounce, slice to grams.
    "banana":     {"fruit": 118.0, "each": 118.0, "oz": 28.35, "slice": 10.0}, # Medium raw peeled USDA
    # Conversion factors for orange: fruit, each, ounce, slice, wedge to grams.
    "orange":     {"fruit": 154.0, "each": 154.0, "oz": 28.35, "slice": 20.0, "wedge": 38.0}, # Medium raw peeled navel USDA
    # Conversion factors for grapes: ounce, cup to grams.
    "grapes":     {"oz": 28.35, "cup": 151.0}, # Seedless raw USDA
    # Conversion factors for strawberries: ounce, each, cup to grams.
    "strawberries": {"oz": 28.35, "each": 12.0, "cup": 152.0}, # Medium raw berry, whole USDA
    # Conversion factors for blueberries: ounce, tablespoon, cup to grams.
    "blueberries": {"oz": 28.35, "tbsp": 9.3, "cup": 148.0}, # Raw USDA
    # Conversion factors for raspberries: ounce, tablespoon, cup to grams.
    "raspberries": {"oz": 28.35, "tbsp": 7.7, "cup": 123.0}, # Raw USDA
    # Conversion factors for watermelon: wedge, ounce, cube, cup to grams.
    "watermelon": {"wedge": 286.0, "oz": 28.35, "cube": 10.0, "cup": 152.0}, # Wedge=1/16th of avg melon, cup diced USDA
    # Conversion factors for cantaloupe: wedge, ounce, cube, cup to grams.
    "cantaloupe": {"wedge": 177.0, "oz": 28.35, "cube": 10.0, "cup": 160.0}, # Wedge=1/8th of medium, cup cubed USDA
    # Conversion factors for pineapple: slice, ring, ounce, chunk, cup to grams.
    "pineapple":  {"slice": 84.0, "ring": 84.0, "oz": 28.35, "chunk": 15.0, "cup": 165.0}, # Slice=3/4" thick, cup chunks USDA
    # Conversion factors for mango: fruit, each, ounce, slice, cube to grams.
    "mango":      {"fruit": 207.0, "each": 207.0, "oz": 28.35, "slice": 25.0, "cube": 10.0}, # Average raw peeled USDA
    # Conversion factors for pear: fruit, each, ounce, slice to grams.
    "pear":       {"fruit": 178.0, "each": 178.0, "oz": 28.35, "slice": 20.0}, # Medium raw Bartlett USDA
    # Conversion factors for peach: fruit, each, ounce, slice to grams.
    "peach":      {"fruit": 150.0, "each": 150.0, "oz": 28.35, "slice": 20.0}, # Medium raw USDA
    # Conversion factors for plum: fruit, each, ounce to grams.
    "plum":       {"fruit": 66.0, "each": 66.0, "oz": 28.35}, # Medium raw USDA
    # Conversion factors for kiwi: fruit, each, ounce, slice to grams.
    "kiwi":       {"fruit": 75.0, "each": 75.0, "oz": 28.35, "slice": 8.0}, # Medium raw green USDA
    # Conversion factors for avocado: fruit, each, ounce, slice, tablespoon mashed to grams.
    "avocado":    {"fruit": 201.0, "each": 100.0, "oz": 28.35, "slice": 15.0, "tbsp mashed": 15.0}, # Fruit=whole avg CA Hass USDA, Each=half avg
    # Conversion factors for generic vegetables: ounce, cup to grams.
    "vegetables": {"oz": 28.35, "cup": 100.0}, # Generic mixed cooked reference
    # Conversion factors for steamed vegetables: ounce, cup to grams.
    "steamed vegetables": {"oz": 28.35, "cup": 100.0},
    # Conversion factors for roasted vegetables: ounce, cup to grams.
    "roasted vegetables": {"oz": 28.35, "cup": 120.0}, # Less water weight
    # Conversion factors for broccoli: ounce, floret, spear, cup to grams.
    "broccoli":   {"oz": 28.35, "floret": 20.0, "spear": 50.0, "cup": 91.0}, # Raw chopped USDA
    # Conversion factors for cooked broccoli: ounce, floret, spear, cup to grams.
    "broccoli cooked": {"oz": 28.35, "floret": 18.0, "spear": 45.0, "cup": 156.0}, # Boiled, drained USDA
    # Conversion factors for carrots: ounce, each, stick, slice, tablespoon shredded, cup to grams.
    "carrots":    {"oz": 28.35, "each": 61.0, "stick": 10.0, "slice": 3.0, "tbsp shredded": 7.0, "cup": 122.0}, # Medium raw, cup chopped USDA
    # Conversion factors for celery: ounce, stick, slice, cup to grams.
    "celery":     {"oz": 28.35, "stick": 40.0, "slice": 3.0, "cup": 101.0}, # Large raw stalk (~11"), cup chopped USDA
    # Conversion factors for cucumber: ounce, each, slice, cup to grams.
    "cucumber":   {"oz": 28.35, "each": 200.0, "slice": 8.0, "cup": 104.0}, # Medium raw (~8 inch) peeled, cup sliced USDA
    # Conversion factors for tomato: ounce, each, slice, wedge, cup to grams.
    "tomato":     {"oz": 28.35, "each": 123.0, "slice": 20.0, "wedge": 30.0, "cup": 180.0}, # Medium raw, cup chopped USDA
    # Conversion factors for cherry tomatoes: ounce, each, cup to grams.
    "cherry tomatoes": {"oz": 28.35, "each": 17.0, "cup": 149.0}, # Raw USDA
    # Conversion factors for bell pepper: ounce, each, slice, ring, cup to grams.
    "bell pepper": {"oz": 28.35, "each": 164.0, "slice": 10.0, "ring": 15.0, "cup": 149.0}, # Large raw (any color), cup chopped USDA
    # Conversion factors for generic spinach: ounce, leaf, cup to grams.
    "spinach":    {"oz": 28.35, "leaf": 3.0, "cup": 30.0}, # Raw USDA
    # Conversion factors for raw spinach: ounce, leaf, cup to grams.
    "spinach raw": {"oz": 28.35, "leaf": 3.0, "cup": 30.0},
    # Conversion factors for cooked spinach: ounce, cup to grams.
    "spinach cooked": {"oz": 28.35, "cup": 180.0}, # Boiled, drained USDA
    # Conversion factors for creamed spinach: ounce, cup to grams.
    "creamed spinach": {"oz": 28.35, "cup": 200.0}, # Varies
    # Conversion factors for generic lettuce: ounce, leaf, cup to grams.
    "lettuce":    {"oz": 28.35, "leaf": 5.0, "cup": 55.0}, # Generic leaf, cup shredded iceberg USDA
    # Conversion factors for kale: ounce, leaf, cup to grams.
    "kale":       {"oz": 28.35, "leaf": 15.0, "cup": 67.0}, # Raw chopped USDA
    # Conversion factors for green beans: ounce, each, cup to grams.
    "green beans": {"oz": 28.35, "each": 5.0, "cup": 110.0}, # Raw cut USDA
    # Conversion factors for cooked green beans: ounce, each, cup to grams.
    "green beans cooked": {"oz": 28.35, "each": 4.5, "cup": 125.0}, # Boiled, drained USDA
    # Conversion factors for generic peas: ounce, tablespoon, cup to grams.
    "peas":       {"oz": 28.35, "tbsp": 10.0, "cup": 145.0}, # Raw green peas USDA
    # Conversion factors for cooked peas: ounce, tablespoon, cup to grams.
    "peas cooked": {"oz": 28.35, "tbsp": 10.0, "cup": 160.0}, # Boiled, drained USDA
    # Conversion factors for generic corn: ounce, cob, cup to grams.
    "corn":       {"oz": 28.35, "cob": 103.0, "cup": 164.0}, # Kernels from medium ear, cup kernels USDA (sweet yellow raw)
    # Conversion factors for corn on the cob: each, ounce to grams.
    "corn on the cob": {"each": 103.0, "oz": 28.35}, # Medium ear, raw kernels weight
    # Conversion factors for corn kernels: ounce, tablespoon, cup to grams.
    "corn kernels": {"oz": 28.35, "tbsp": 10.3, "cup": 164.0}, # Raw sweet yellow
    # Conversion factors for creamed corn: ounce, tablespoon, cup to grams.
    "creamed corn": {"oz": 28.35, "tbsp": 18.0, "cup": 245.0}, # Canned USDA
    # Conversion factors for generic onion: ounce, each, slice, ring, tablespoon chopped, cup to grams.
    "onion":      {"oz": 28.35, "each": 110.0, "slice": 8.0, "ring": 6.0, "tbsp chopped": 10.0, "cup": 160.0}, # Medium raw (2.5" dia), cup chopped USDA
    # Conversion factors for raw onion: ounce, each, slice, ring, tablespoon chopped to grams.
    "onion raw":  {"oz": 28.35, "each": 110.0, "slice": 8.0, "ring": 6.0, "tbsp chopped": 10.0},
    # Conversion factors for generic mushroom: ounce, each, slice, cup to grams.
    "mushroom":   {"oz": 28.35, "each": 18.0, "slice": 4.0, "cup": 70.0}, # Medium white raw USDA, cup sliced
    # Conversion factors for raw mushrooms: ounce, each, slice, cup to grams.
    "mushrooms raw": {"oz": 28.35, "each": 18.0, "slice": 4.0, "cup": 70.0},
    # Conversion factors for sauteed mushrooms: ounce, cup to grams.
    "sauteed mushrooms": {"oz": 28.35, "cup": 100.0}, # Cooked down
    # Conversion factors for generic zucchini: ounce, each, slice, cup to grams.
    "zucchini":   {"oz": 28.35, "each": 196.0, "slice": 8.0, "cup": 124.0}, # Medium raw USDA, cup sliced
    # Conversion factors for raw zucchini: ounce, each, slice, cup to grams.
    "zucchini raw": {"oz": 28.35, "each": 196.0, "slice": 8.0, "cup": 124.0},
    # Conversion factors for generic asparagus: ounce, spear, cup to grams.
    "asparagus":  {"oz": 28.35, "spear": 20.0, "cup": 134.0}, # Medium spear raw USDA, cup chopped
    # Conversion factors for cooked asparagus: ounce, spear, cup to grams.
    "asparagus cooked": {"oz": 28.35, "spear": 18.0, "cup": 180.0}, # Boiled, drained USDA
    # Conversion factors for grilled asparagus: ounce, spear, cup to grams.
    "grilled asparagus": {"oz": 28.35, "spear": 18.0, "cup": 170.0}, # Loses more water
    # Conversion factors for generic eggplant: ounce, each, slice, cube, cup to grams.
    "eggplant":   {"oz": 28.35, "each": 458.0, "slice": 30.0, "cube": 10.0, "cup": 82.0}, # Average raw USDA, cup cubed
    # Conversion factors for eggplant parmesan: ounce to grams.
    "eggplant parmesan": {"oz": 28.35}, # Use S/M/L via CSV for serving
    # Conversion factors for generic potatoes: ounce, each, wedge, cube, cup to grams.
    "potatoes":   {"oz": 28.35, "each": 173.0, "wedge": 30.0, "cube": 10.0, "cup": 150.0}, # Medium raw russet USDA (flesh+skin), cup cubed
    # Conversion factors for baked potato: ounce, each to grams.
    "baked potato": {"oz": 28.35, "each": 173.0}, # Cooked weight similar to raw avg USDA
    # Conversion factors for plain baked potato: ounce, each to grams.
    "baked potato plain": {"oz": 28.35, "each": 173.0},
    # Conversion factors for mashed potatoes: ounce, scoop, cup to grams.
    "mashed potatoes": {"oz": 28.35, "scoop": 80.0, "cup": 210.0}, # Plain, with milk/butter USDA
    # Conversion factors for plain mashed potatoes: ounce, scoop, cup to grams.
    "mashed potatoes plain": {"oz": 28.35, "scoop": 80.0, "cup": 210.0},
    # Conversion factors for roasted potatoes: ounce, piece, cup to grams.
    "roasted potatoes": {"oz": 28.35, "piece": 25.0, "cup": 150.0}, # Cooked weight, depends on cut size
    # Conversion factors for potato wedges: ounce, wedge, cup to grams.
    "potato wedges": {"oz": 28.35, "wedge": 30.0, "cup": 140.0}, # Cooked weight
    # Conversion factors for french fries: ounce, cup to grams.
    "french fries": {"oz": 28.35, "cup": 71.0}, # Fast food style, cooked USDA
    # Conversion factors for sweet potato fries: ounce, cup to grams.
    "sweet potato fries": {"oz": 28.35, "cup": 90.0}, # Cooked, denser
    # Conversion factors for onion rings: ounce, each to grams.
    "onion rings": {"oz": 28.35, "each": 15.0}, # Breaded, fried avg
    # Conversion factors for generic pickles: ounce, slice, spear, each to grams.
    "pickles":    {"oz": 28.35, "slice": 5.0, "spear": 35.0, "each": 65.0}, # Medium dill pickle USDA
    # Conversion factors for dill pickles: ounce, slice, spear, each to grams.
    "pickles dill": {"oz": 28.35, "slice": 5.0, "spear": 35.0, "each": 65.0},
    # Conversion factors for sweet gherkin pickles: ounce, each to grams.
    "pickles sweet gherkin": {"oz": 28.35, "each": 15.0}, # Small sweet pickle USDA
    # Conversion factors for pickled onions: ounce, each, tablespoon to grams.
    "pickled onions": {"oz": 28.35, "each": 10.0, "tbsp": 15.0}, # Pearl onion size
    # Conversion factors for pickled jalapenos: ounce, slice, tablespoon to grams.
    "pickled jalapenos": {"oz": 28.35, "slice": 2.0, "tbsp": 15.0}, # Sliced
    # Conversion factors for generic olives: ounce, each, tablespoon to grams.
    "olives":     {"oz": 28.35, "each": 4.0, "tbsp": 8.0}, # Medium size, pitted green USDA
    # Conversion factors for green olives: ounce, each, tablespoon to grams.
    "olives green": {"oz": 28.35, "each": 4.0, "tbsp": 8.0},
    # Conversion factors for kalamata olives: ounce, each, tablespoon to grams.
    "olives kalamata": {"oz": 28.35, "each": 4.0, "tbsp": 8.0}, # USDA
    # Conversion factors for capers: teaspoon, tablespoon, ounce to grams.
    "capers":     {"tsp": 2.0, "tbsp": 6.0, "oz": 28.35}, # Canned, drained USDA
    # Conversion factors for drained capers: teaspoon, tablespoon, ounce to grams.
    "capers drained": {"tsp": 2.0, "tbsp": 6.0, "oz": 28.35},
    # Conversion factors for artichoke hearts: ounce, each, cup to grams.
    "artichoke hearts": {"oz": 28.35, "each": 30.0, "cup": 160.0}, # Canned, drained quartered USDA
    # Conversion factors for canned artichoke hearts: ounce, each, cup to grams.
    "artichoke hearts canned": {"oz": 28.35, "each": 30.0, "cup": 160.0},
    # Conversion factors for marinated artichoke hearts: ounce, each, cup to grams.
    "artichoke hearts marinated": {"oz": 28.35, "each": 30.0, "cup": 160.0}, # Weight includes some oil
    # Conversion factors for sun dried tomatoes: ounce, piece, tablespoon to grams.
    "sun dried tomatoes": {"oz": 28.35, "piece": 3.0, "tbsp": 5.0}, # Not packed in oil
    # Conversion factors for roasted red peppers: ounce, strip, tablespoon to grams.
    "roasted red peppers": {"oz": 28.35, "strip": 10.0, "tbsp": 10.0}, # Jarred, drained
    # Conversion factors for jarred roasted red peppers: ounce, strip, tablespoon to grams.
    "roasted red peppers jarred": {"oz": 28.35, "strip": 10.0, "tbsp": 10.0},

    # Section for legume conversions (cooked weights).
    # == Legumes (Cooked weights) ==
    # Conversion factors for generic beans: ounce, tablespoon, cup to grams.
    "beans":      {"oz": 28.35, "tbsp": 16.0, "cup": 250.0}, # Generic cooked avg
    # Conversion factors for baked beans: ounce, tablespoon, cup to grams.
    "baked beans": {"oz": 28.35, "tbsp": 18.0, "cup": 253.0}, # Canned, plain/vegetarian USDA
    # Conversion factors for refried beans: ounce, tablespoon, cup to grams.
    "refried beans": {"oz": 28.35, "tbsp": 17.0, "cup": 239.0}, # Canned, traditional USDA
    # Conversion factors for generic lentils: ounce, tablespoon, cup to grams.
    "lentils":    {"oz": 28.35, "tbsp": 12.4, "cup": 198.0}, # Cooked USDA
    # Conversion factors for cooked lentils: ounce, tablespoon, cup to grams.
    "lentils cooked": {"oz": 28.35, "tbsp": 12.4, "cup": 198.0},
    # Conversion factors for generic chickpeas: ounce, tablespoon, cup to grams.
    "chickpeas":  {"oz": 28.35, "tbsp": 10.3, "cup": 164.0}, # Cooked (Garbanzos) USDA
    # Conversion factors for cooked chickpeas: ounce, tablespoon, cup to grams.
    "chickpeas cooked": {"oz": 28.35, "tbsp": 10.3, "cup": 164.0},
    # Conversion factors for black beans: ounce, tablespoon, cup to grams.
    "black beans": {"oz": 28.35, "tbsp": 10.8, "cup": 172.0}, # Cooked USDA
    # Conversion factors for edamame: ounce, pod, cup to grams.
    "edamame":    {"oz": 28.35, "pod": 5.0, "cup": 155.0}, # Shelled, cooked USDA

    # Section for bread and baked good conversions.
    # == Breads & Baked Goods ==
    # Conversion factors for generic bread: slice, ounce, roll to grams.
    "bread":      {"slice": 28.0, "oz": 28.35, "roll": 50.0}, # Avg sandwich slice white/wheat
    # Conversion factors for generic toast: slice, ounce to grams.
    "toast":      {"slice": 25.0, "oz": 28.35}, # Slightly lighter due to moisture loss
    # Conversion factors for white toast slice: each, ounce to grams.
    "toast white slice": {"each": 25.0, "oz": 28.35},
    # Conversion factors for whole wheat toast slice: each, ounce to grams.
    "toast whole wheat slice": {"each": 25.0, "oz": 28.35},
    # Conversion factors for generic bagel: each, ounce to grams.
    "bagel":      {"each": 90.0, "oz": 28.35}, # Average 3.5-4" plain bagel USDA
    # Conversion factors for plain bagel: each, ounce to grams.
    "bagel plain": {"each": 90.0, "oz": 28.35},
    # Conversion factors for generic english muffin: each, ounce to grams.
    "english muffin": {"each": 57.0, "oz": 28.35}, # Average plain USDA
    # Conversion factors for plain english muffin: each, ounce to grams.
    "english muffin plain": {"each": 57.0, "oz": 28.35},
    # Conversion factors for generic croissant: each, ounce to grams.
    "croissant":  {"each": 57.0, "oz": 28.35}, # Average butter croissant USDA
    # Conversion factors for plain croissant: each, ounce to grams.
    "croissant plain": {"each": 57.0, "oz": 28.35},
    # Conversion factors for generic muffin: each, ounce to grams.
    "muffin":     {"each": 85.0, "oz": 28.35}, # Generic medium ~3oz muffin
    # Conversion factors for blueberry muffin: each, ounce to grams.
    "muffin blueberry": {"each": 95.0, "oz": 28.35}, # Slightly heavier
    # Conversion factors for bran muffin: each, ounce to grams.
    "muffin bran": {"each": 90.0, "oz": 28.35},
    # Conversion factors for generic dinner roll: each, ounce to grams.
    "dinner roll": {"each": 35.0, "oz": 28.35}, # Small plain roll ~1.25oz USDA
    # Conversion factors for plain dinner roll: each, ounce to grams.
    "dinner roll plain": {"each": 35.0, "oz": 28.35},
    # Conversion factors for pita bread: each, ounce to grams.
    "pita bread": {"each": 60.0, "oz": 28.35}, # 6" diameter white avg USDA
    # Conversion factors for naan bread: each, ounce to grams.
    "naan bread": {"each": 90.0, "oz": 28.35}, # Average piece plain
    # Conversion factors for generic cornbread: piece, ounce to grams.
    "cornbread":  {"piece": 70.0, "oz": 28.35}, # ~2.5 inch square from mix USDA
    # Conversion factors for cornbread piece: each, ounce to grams.
    "cornbread piece": {"each": 70.0, "oz": 28.35},
    # Conversion factors for generic garlic bread: slice, ounce to grams.
    "garlic bread": {"slice": 40.0, "oz": 28.35}, # Frozen type slice avg
    # Conversion factors for garlic bread slice: each, ounce to grams.
    "garlic bread slice": {"each": 40.0, "oz": 28.35},
    # Conversion factors for generic waffles: each, ounce to grams.
    "waffles":    {"each": 75.0, "oz": 28.35}, # 7" round frozen plain type avg USDA
    # Conversion factors for plain waffles: each, ounce to grams.
    "waffles plain": {"each": 75.0, "oz": 28.35},
    # Conversion factors for generic pancakes: each, ounce to grams.
    "pancakes":   {"each": 60.0, "oz": 28.35}, # 5" diameter homemade plain avg
    # Conversion factors for plain pancakes: each, ounce to grams.
    "pancakes plain": {"each": 60.0, "oz": 28.35},
    # Conversion factors for generic french toast: slice, ounce to grams.
    "french toast": {"slice": 80.0, "oz": 28.35}, # Homemade, from avg bread slice + egg
    # Conversion factors for plain french toast slice: slice, ounce to grams.
    "french toast slice plain": {"slice": 80.0, "oz": 28.35},
    # Conversion factors for generic cookie: each, ounce to grams.
    "cookie":     {"each": 25.0, "oz": 28.35}, # Medium ~3" chocolate chip type avg
    # Conversion factors for chocolate chip cookie: each, ounce to grams.
    "chocolate chip cookie": {"each": 25.0, "oz": 28.35}, # USDA prepared from recipe
    # Conversion factors for oatmeal raisin cookie: each, ounce to grams.
    "oatmeal raisin cookie": {"each": 25.0, "oz": 28.35}, # Similar size avg
    # Conversion factors for sugar cookie: each, ounce to grams.
    "sugar cookie": {"each": 20.0, "oz": 28.35}, # Often smaller/lighter
    # Conversion factors for generic brownie: each, ounce to grams.
    "brownie":    {"each": 60.0, "oz": 28.35}, # ~2.5 inch square avg USDA
    # Conversion factors for fudge brownie: each, ounce to grams.
    "brownie fudge": {"each": 65.0, "oz": 28.35}, # Denser
    # Conversion factors for blondie: each, ounce to grams.
    "blondie":    {"each": 60.0, "oz": 28.35}, # Similar size to brownie
    # Conversion factors for generic cake: slice, ounce to grams.
    "cake":       {"slice": 100.0, "oz": 28.35}, # Generic slice (1/12 of 9" yellow cake) avg
    # Conversion factors for chocolate cake: slice, ounce to grams.
    "chocolate cake": {"slice": 110.0, "oz": 28.35}, # Usually denser/richer
    # Conversion factors for vanilla cake: slice, ounce to grams.
    "vanilla cake": {"slice": 100.0, "oz": 28.35},
    # Conversion factors for carrot cake: slice, ounce to grams.
    "carrot cake": {"slice": 120.0, "oz": 28.35}, # Often denser, with cream cheese frosting
    # Conversion factors for generic cupcake: each, ounce to grams.
    "cupcake":    {"each": 70.0, "oz": 28.35}, # Standard size, unfrosted avg
    # Conversion factors for frosted cupcake: each, ounce to grams.
    "cupcake frosted": {"each": 85.0, "oz": 28.35}, # Adding frosting weight
    # Conversion factors for generic pie: slice, ounce to grams.
    "pie":        {"slice": 120.0, "oz": 28.35}, # Generic slice (1/8 of 9" double crust fruit pie) avg
    # Conversion factors for apple pie: slice, ounce to grams.
    "apple pie":  {"slice": 140.0, "oz": 28.35}, # USDA
    # Conversion factors for pumpkin pie: slice, ounce to grams.
    "pumpkin pie": {"slice": 130.0, "oz": 28.35}, # USDA
    # Conversion factors for pecan pie: slice, ounce to grams.
    "pecan pie":  {"slice": 125.0, "oz": 28.35}, # Dense filling USDA
    # Conversion factors for generic cheesecake: slice, ounce to grams.
    "cheesecake": {"slice": 120.0, "oz": 28.35}, # Avg slice USDA
    # Conversion factors for plain cheesecake slice: slice, ounce to grams.
    "cheesecake slice plain": {"slice": 120.0, "oz": 28.35},
    # Conversion factors for generic donut: each, ounce to grams.
    "donut":      {"each": 70.0, "oz": 28.35}, # Average glazed yeast donut USDA
    # Conversion factors for glazed donut: each, ounce to grams.
    "donut glazed": {"each": 70.0, "oz": 28.35},
    # Conversion factors for cake donut: each, ounce to grams.
    "donut cake": {"each": 80.0, "oz": 28.35}, # Denser
    # Conversion factors for jelly filled donut: each, ounce to grams.
    "donut jelly filled": {"each": 85.0, "oz": 28.35}, # Added filling weight
    # Conversion factors for macaron: each, ounce to grams.
    "macaron":    {"each": 15.0, "oz": 28.35}, # Small almond meringue cookie
    # Conversion factors for tiramisu: slice, piece, ounce to grams.
    "tiramisu":   {"slice": 150.0, "piece": 150.0, "oz": 28.35}, # Rich dessert, avg portion
    # Conversion factors for creme brulee: ramekin, ounce to grams.
    "creme brulee": {"ramekin": 120.0, "oz": 28.35}, # Custard in standard ramekin

    # Section for snack conversions.
    # == Snacks ==
    # Conversion factors for generic nuts: ounce, tablespoon to grams.
    "nuts":       {"oz": 28.35, "tbsp": 8.0}, # Generic mixed nuts, tbsp chopped avg
    # Conversion factors for mixed nuts: ounce, tablespoon to grams.
    "mixed nuts": {"oz": 28.35, "tbsp": 8.0},
    # Conversion factors for almonds: ounce, each, tablespoon to grams.
    "almonds":    {"oz": 28.35, "each": 1.2, "tbsp": 8.5}, # Whole raw almonds USDA
    # Conversion factors for walnuts: ounce, each, half, tablespoon to grams.
    "walnuts":    {"oz": 28.35, "each": 4.0, "half": 2.0, "tbsp": 7.5}, # Halves/pieces raw USDA
    # Conversion factors for peanuts: ounce, each, tablespoon to grams.
    "peanuts":    {"oz": 28.35, "each": 0.6, "tbsp": 9.0}, # Raw shelled USDA
    # Conversion factors for cashews: ounce, each, tablespoon to grams.
    "cashews":    {"oz": 28.35, "each": 1.5, "tbsp": 8.0}, # Raw whole USDA
    # Conversion factors for pecans: ounce, each, half, tablespoon to grams.
    "pecans":     {"oz": 28.35, "each": 2.0, "half": 2.0, "tbsp": 7.0}, # Halves raw USDA
    # Conversion factors for pistachios: ounce, each to grams.
    "pistachios": {"oz": 28.35, "each": 0.7}, # Raw in shell weight avg
    # Conversion factors for macadamia nuts: ounce, each to grams.
    "macadamia nuts": {"oz": 28.35, "each": 2.5}, # Raw USDA
    # Conversion factors for brazil nuts: ounce, each to grams.
    "brazil nuts": {"oz": 28.35, "each": 4.0}, # Raw USDA
    # Conversion factors for hazelnuts: ounce, each to grams.
    "hazelnuts":  {"oz": 28.35, "each": 1.0}, # Raw USDA
    # Conversion factors for generic seeds: ounce, teaspoon, tablespoon to grams.
    "seeds":      {"oz": 28.35, "tsp": 3.0, "tbsp": 9.0}, # Generic seed avg
    # Conversion factors for chia seeds: ounce, teaspoon, tablespoon to grams.
    "chia seeds": {"oz": 28.35, "tsp": 4.0, "tbsp": 12.0}, # Dried USDA
    # Conversion factors for flax seeds: ounce, teaspoon, tablespoon to grams.
    "flax seeds": {"oz": 28.35, "tsp": 3.5, "tbsp": 10.0}, # Whole USDA
    # Conversion factors for pumpkin seeds: ounce, teaspoon, tablespoon to grams.
    "pumpkin seeds": {"oz": 28.35, "tsp": 2.5, "tbsp": 7.5}, # Hulled, roasted USDA
    # Conversion factors for sunflower seeds: ounce, teaspoon, tablespoon to grams.
    "sunflower seeds": {"oz": 28.35, "tsp": 2.7, "tbsp": 8.0}, # Hulled, roasted USDA
    # Conversion factors for sesame seeds: ounce, teaspoon, tablespoon to grams.
    "sesame seeds": {"oz": 28.35, "tsp": 2.8, "tbsp": 8.5}, # Whole, roasted USDA
    # Conversion factors for hemp seeds: ounce, teaspoon, tablespoon to grams.
    "hemp seeds": {"oz": 28.35, "tsp": 3.3, "tbsp": 10.0}, # Hulled (hearts)
    # Conversion factors for popcorn: ounce, cup to grams.
    "popcorn":    {"oz": 28.35, "cup": 8.0}, # Air-popped USDA
    # Conversion factors for pretzels: ounce, each to grams.
    "pretzels":   {"oz": 28.35, "each": 5.0}, # Small hard twist USDA
    # Conversion factors for generic chips: ounce, each to grams.
    "chips":      {"oz": 28.35, "each": 2.0}, # Generic potato/tortilla chip avg
    # Conversion factors for potato chips: ounce, each to grams.
    "potato chips": {"oz": 28.35, "each": 2.0}, # Regular cut chip avg USDA
    # Conversion factors for tortilla chips: ounce, each to grams.
    "tortilla chips": {"oz": 28.35, "each": 3.0}, # Standard triangle avg USDA
    # Conversion factors for generic chocolate: ounce, piece, square, bar to grams.
    "chocolate":  {"oz": 28.35, "piece": 7.0, "square": 7.0, "bar": 43.0}, # Piece/square common ~7g, bar=standard ~1.5oz USDA dark
    # Conversion factors for chocolate bar: ounce, piece, square, each to grams.
    "chocolate bar": {"oz": 28.35, "piece": 7.0, "square": 7.0, "each": 43.0},
    # Conversion factors for chocolate chips: ounce, teaspoon, tablespoon to grams.
    "chocolate chips": {"oz": 28.35, "tsp": 5.0, "tbsp": 15.0}, # Semisweet USDA
    # Conversion factors for raisins: ounce, tablespoon, box to grams.
    "raisins":    {"oz": 28.35, "tbsp": 10.0, "box": 14.0}, # Seedless USDA, Standard small box ~0.5oz
    # Conversion factors for craisins: ounce, tablespoon to grams.
    "craisins":   {"oz": 28.35, "tbsp": 10.0}, # Dried cranberries, sweetened
    # Conversion factors for generic dried fruit: ounce, piece, tablespoon to grams.
    "dried fruit": {"oz": 28.35, "piece": 8.0, "tbsp": 10.0}, # Generic piece avg
    # Conversion factors for dried apricots: ounce, each, tablespoon to grams.
    "dried apricots": {"oz": 28.35, "each": 6.0, "tbsp": 10.0}, # Halves USDA
    # Conversion factors for generic dates: ounce, each to grams.
    "dates":      {"oz": 28.35, "each": 24.0}, # Pitted Medjool date avg USDA
    # Conversion factors for pitted dates: ounce, each to grams.
    "dates pitted": {"oz": 28.35, "each": 24.0},

    # Section for combined dish conversions (rely heavily on S/M/L from CSV).
    # == Combined Dishes (Rely on S/M/L via CSV for serving size) ==
    # Conversion factors for generic pizza: slice, ounce to grams.
    "pizza":      {"slice": 110.0, "oz": 28.35}, # Average slice (1/8 of 14" cheese) ref
    # Conversion factors for pizza slice: each, ounce to grams.
    "pizza slice": {"each": 110.0, "oz": 28.35}, # 'each' here means one slice
    # Conversion factors for personal pizza: ounce to grams.
    "personal pizza": {"oz": 28.35}, # Use S/M/L via CSV
    # Conversion factors for generic burger: ounce to grams.
    "burger":     {"oz": 28.35}, # Use S/M/L via CSV for whole burger
    # Conversion factors for cheeseburger: ounce to grams.
    "cheeseburger": {"oz": 28.35}, # Use S/M/L via CSV
    # Conversion factors for bacon cheeseburger: ounce to grams.
    "bacon cheeseburger": {"oz": 28.35}, # Use S/M/L via CSV
    # Conversion factors for veggie burger: ounce to grams.
    "veggie burger": {"oz": 28.35}, # Use S/M/L via CSV
    # Conversion factors for generic sandwich: ounce to grams.
    "sandwich":   {"oz": 28.35}, # Use S/M/L via CSV for whole sandwich
    # Conversion factors for chicken sandwich: ounce to grams.
    "chicken sandwich": {"oz": 28.35}, # Use S/M/L via CSV
    # Conversion factors for pulled pork sandwich: ounce to grams.
    "pulled pork sandwich": {"oz": 28.35}, # Use S/M/L via CSV
    # Conversion factors for club sandwich: ounce to grams.
    "club sandwich": {"oz": 28.35}, # Use S/M/L via CSV
    # Conversion factors for grilled cheese sandwich: ounce to grams.
    "grilled cheese sandwich": {"oz": 28.35}, # Use S/M/L via CSV
    # Conversion factors for peanut butter jelly sandwich: ounce to grams.
    "peanut butter jelly sandwich": {"oz": 28.35}, # Use S/M/L via CSV
    # Conversion factors for generic wrap: ounce to grams.
    "wrap":       {"oz": 28.35}, # Use S/M/L via CSV
    # Conversion factors for generic burrito: ounce to grams.
    "burrito":    {"oz": 28.35}, # Use S/M/L via CSV
    # Conversion factors for generic taco: each, ounce to grams.
    "taco":       {"each": 120.0, "oz": 28.35}, # Average hard or soft shell taco weight ref
    # Conversion factors for hard shell taco: each, ounce to grams.
    "taco hard shell": {"each": 110.0, "oz": 28.35}, # Lighter filling maybe
    # Conversion factors for soft shell taco: each, ounce to grams.
    "taco soft shell": {"each": 130.0, "oz": 28.35}, # Heavier tortilla/filling
    # Conversion factors for generic quesadilla: wedge, ounce to grams.
    "quesadilla": {"wedge": 50.0, "oz": 28.35}, # Wedge (1/4 of 10" cheese quesadilla) ref
    # Conversion factors for generic stir-fry: ounce, cup to grams.
    "stir-fry":   {"oz": 28.35, "cup": 180.0}, # Generic mixed dish ref, use S/M/L via CSV
    # Conversion factors for chicken stir-fry: ounce, cup to grams.
    "chicken stir-fry": {"oz": 28.35, "cup": 180.0}, # Use S/M/L via CSV
    # Conversion factors for generic curry: ounce, cup to grams.
    "curry":      {"oz": 28.35, "cup": 220.0}, # Generic mixed dish ref, use S/M/L via CSV
    # Conversion factors for chicken curry: ounce, cup to grams.
    "chicken curry": {"oz": 28.35, "cup": 220.0}, # Use S/M/L via CSV
    # Conversion factors for generic salad: ounce to grams.
    "salad":      {"oz": 28.35}, # Use S/M/L via CSV for main salad serving
    # Conversion factors for green salad: ounce to grams.
    "green salad": {"oz": 28.35}, # Use S/M/L via CSV
    # Conversion factors for caesar salad: ounce to grams.
    "caesar salad": {"oz": 28.35}, # Use S/M/L via CSV
    # Conversion factors for tuna salad: ounce, scoop, cup to grams.
    "tuna salad": {"oz": 28.35, "scoop": 80.0, "cup": 160.0}, # Salad mix ref, use S/M/L via CSV for portion
    # Conversion factors for chicken salad: ounce, scoop, cup to grams.
    "chicken salad": {"oz": 28.35, "scoop": 80.0, "cup": 160.0}, # Salad mix ref, use S/M/L via CSV
    # Conversion factors for potato salad: ounce, scoop, cup to grams.
    "potato salad": {"oz": 28.35, "scoop": 100.0, "cup": 200.0}, # Side dish ref, use S/M/L via CSV
    # Conversion factors for coleslaw: ounce, scoop, cup to grams.
    "coleslaw":   {"oz": 28.35, "scoop": 80.0, "cup": 100.0}, # Side dish ref, use S/M/L via CSV
    # Conversion factors for omelette: ounce to grams (relying on S/M/L from CSV).
    "omelette":   {"oz": 28.35}, # Use S/M/L via CSV for size (e.g., 2-egg, 3-egg)
    # Conversion factors for scrambled eggs: ounce, cup to grams (relying on S/M/L from CSV).
    "scrambled eggs": {"oz": 28.35, "cup": 160.0}, # Cooked, ~3 large eggs per cup ref, use S/M/L via CSV
    # Conversion factors for lasagna: slice, piece, ounce to grams.
    "lasagna":    {"slice": 250.0, "piece": 250.0, "oz": 28.35}, # Average slice ref, use S/M/L via CSV
    # Conversion factors for mac and cheese: ounce, cup to grams.
    "mac and cheese": {"oz": 28.35, "cup": 220.0}, # Cooked ref, use S/M/L via CSV
    # Conversion factors for sushi roll: piece, roll, ounce to grams.
    "sushi roll": {"piece": 25.0, "roll": 150.0, "oz": 28.35}, # Piece=single cut slice, Roll=6-8 pieces avg
    # Conversion factors for nigiri: piece, ounce to grams.
    "nigiri":     {"piece": 35.0, "oz": 28.35}, # Single piece avg
    # Conversion factors for onigiri: each, ounce to grams.
    "onigiri":    {"each": 100.0, "oz": 28.35}, # Japanese rice ball avg
    # Conversion factors for pad thai: ounce, cup to grams.
    "pad thai":   {"oz": 28.35, "cup": 200.0}, # Cooked ref, use S/M/L via CSV
    # Conversion factors for falafel: ball, each, ounce to grams.
    "falafel":    {"ball": 20.0, "each": 20.0, "oz": 28.35}, # ~1 inch diameter ball fried
    # Conversion factors for stuffed bell pepper: each, ounce to grams.
    "stuffed bell pepper": {"each": 250.0, "oz": 28.35}, # Average size cooked

    # Section for dessert conversions (specific items).
    # == Desserts (Specific items) ==
    # Conversion factors for generic ice cream: scoop, ounce, cup to grams.
    "ice cream":  {"scoop": 66.0, "oz": 28.35, "cup": 132.0}, # Standard #12 scoop (~4 fl oz) vanilla USDA
    # Conversion factors for vanilla ice cream: scoop, ounce, cup to grams.
    "ice cream vanilla": {"scoop": 66.0, "oz": 28.35, "cup": 132.0},
    # Conversion factors for chocolate ice cream: scoop, ounce, cup to grams.
    "ice cream chocolate": {"scoop": 70.0, "oz": 28.35, "cup": 140.0}, # Slightly denser USDA
    # Conversion factors for sorbet: scoop, ounce, cup to grams.
    "sorbet":     {"scoop": 80.0, "oz": 28.35, "cup": 180.0}, # Water based, denser than ice cream
    # Conversion factors for generic pudding: teaspoon, tablespoon, ounce, cup to grams.
    "pudding":    {"tsp": 6.0, "tbsp": 18.0, "oz": 28.35, "cup": 150.0}, # Cooked from mix avg
    # Conversion factors for pudding cup: each, ounce to grams.
    "pudding cup": {"each": 110.0, "oz": 28.35}, # Standard prepackaged ~4oz cup size
    # Conversion factors for generic jello: teaspoon, tablespoon, ounce, cup to grams.
    "jello":      {"tsp": 6.0, "tbsp": 18.0, "oz": 28.35, "cup": 120.0}, # Prepared avg
    # Conversion factors for jello cup: each, ounce to grams.
    "jello cup":  {"each": 100.0, "oz": 28.35}, # Standard prepackaged ~3.5oz cup size
# End of the CONVERSIONS dictionary definition.
}


# --- Core Units ---
# Define a list of fundamental units always available in the UI.
CORE_UNITS = ["grams", "small", "medium", "large"]

# --- Qualitative / Implicit Quantity Units ---
# Initialize a set with the size units (small, medium, large) which imply a quantity.
_units_implying_quantity = set(CORE_UNITS[1:])
# Define a list of specific keywords that represent a somewhat standard quantity (e.g., 'slice', 'scoop').
_specific_qualitative_keywords = [
    'drizzle', 'pat', 'packet', 'slice', 'splash', 'fruit', 'pancake',
    'roll', 'taco', 'wing', 'fillet', 'patty', 'egg', 'each', 'scoop',
    'bowl', 'glass', 'bottle', 'can', 'mug', 'pint', 'piece', 'chop',
    'bar', 'serving', 'shot', 'skewer', 'ramekin', 'box', 'square',
    'leaf', 'floret', 'spear', 'stick', 'cob', 'wedge', 'ring', 'cube',
    'chunk', 'log', 'ball', 'tail', 'leg', 'thigh', 'breast', 'strip',
    'dash', 'biscuit', 'medallion', 'pod', 'half', 'quarter', 'dollop', 'bit',
    'link',
]
# Iterate through all the unit conversion dictionaries defined in CONVERSIONS.
for conversion_dict in CONVERSIONS.values():
    # Iterate through each unit key (like 'tsp', 'slice', 'cup') within a specific food's conversion dictionary.
    for unit_key in conversion_dict.keys():
        # Check if this unit key is one of our predefined qualitative keywords.
        if unit_key in _specific_qualitative_keywords:
             # If it is, add it to the set of units that imply a quantity.
             _units_implying_quantity.add(unit_key)
# Create a sorted list from the set of all qualitative units for consistent UI display.
QUALITATIVE_UNIT_TERMS = sorted(list(_units_implying_quantity))


# --- Load Calorie Table Function ---
# Define the function to load calorie data from the processed CSV file.
def load_calorie_table(path="calorie_table_processed.csv") -> dict | None:
    # Docstring explaining the function's purpose, arguments, and return value.
    """
    Loads calorie and S/M/L size data from a specified CSV file.

    Args:
        path (str): The file path to the calorie data CSV.

    Returns:
        dict | None: Dictionary mapping lowercase labels to tuples:
                     (Original_Label, Calories_per_Gram, Small_g, Medium_g, Large_g).
                     Returns None on failure. Needs realistic S/M/L values in CSV.
    """
    # Check if the specified path exists.
    if not os.path.exists(path):
        # If not, print an error message to standard error.
        print(f"ERROR: Calorie data file '{path}' not found.", file=sys.stderr)
        # Get the directory where the current script (ut.py) is located.
        script_dir = os.path.dirname(__file__)
        # Construct an alternative path relative to the script directory.
        alt_path = os.path.join(script_dir, path)
        # Check if the alternative path exists.
        if not os.path.exists(alt_path):
            # If the alternative path also doesn't exist, print another error.
            print(f"ERROR: Also not found at alternative path '{alt_path}'.", file=sys.stderr)
            # Return None to indicate failure.
            return None
        # If the alternative path exists.
        else:
            # Update the path variable to use the alternative path.
            path = alt_path
            # Print an informational message that the alternative path is being used.
            print(f"Info: Using calorie data file found at '{path}'.")

    # Initialize an empty dictionary to store the loaded data.
    table = {}
    # Define the list of column names expected in the CSV header.
    required_cols = ["Label", "Calories_per_Gram", "Small_g", "Medium_g", "Large_g"]

    # Start a try block to handle potential file I/O or parsing errors.
    try:
        # Open the CSV file for reading ('r'), disable universal newlines (''), and specify UTF-8 encoding.
        with open(path, mode="r", newline="", encoding="utf-8") as f:
            # Create a CSV DictReader object to read rows as dictionaries.
            reader = csv.DictReader(f)

            # Validate that all required columns are present in the CSV header.
            if not all(col in reader.fieldnames for col in required_cols):
                # Find the missing columns.
                missing = [col for col in required_cols if col not in reader.fieldnames]
                # Print an error message listing the missing columns.
                print(f"ERROR: CSV '{path}' missing required columns: {missing}", file=sys.stderr)
                # Return None to indicate failure due to incorrect format.
                return None

            # Iterate through each row in the CSV file, getting both index (i) and row data.
            for i, row in enumerate(reader):
                # Get the 'Label' value, remove leading/trailing whitespace.
                label_original = row.get("Label", "").strip()
                # Convert the original label to lowercase for consistent key usage.
                label_lower = label_original.lower()
                # Get the 'Calories_per_Gram' value as a string, remove whitespace.
                cal_g_str = row.get("Calories_per_Gram", "").strip()
                # Get the 'Small_g' value as a string, remove whitespace.
                small_g_str = row.get("Small_g", "").strip()
                # Get the 'Medium_g' value as a string, remove whitespace.
                medium_g_str = row.get("Medium_g", "").strip()
                # Get the 'Large_g' value as a string, remove whitespace.
                large_g_str = row.get("Large_g", "").strip()

                # Check if any of the essential string values are empty; if so, skip this row.
                if not label_original or not cal_g_str or not small_g_str or not medium_g_str or not large_g_str:
                    # Continue to the next row.
                    continue

                # Start a nested try block to handle potential errors when converting strings to numbers.
                try:
                    # Convert the calorie string to a float.
                    calories_per_gram = float(cal_g_str)
                    # Convert the small size string to a float.
                    small_g = float(small_g_str)
                    # Convert the medium size string to a float.
                    medium_g = float(medium_g_str)
                    # Convert the large size string to a float.
                    large_g = float(large_g_str)

                    # Perform sanity checks on the converted numeric values.
                    # Check if calories are negative, any size is non-positive, or sizes are not ordered correctly (S <= M <= L).
                    if calories_per_gram < 0 or small_g <= 0 or medium_g <= 0 or large_g <= 0 or medium_g < small_g or large_g < medium_g :
                        # Allow the special case where all sizes are equal and positive.
                        if small_g > 0 and small_g == medium_g == large_g:
                             # If sizes are equal and positive, do nothing (it's allowed).
                             pass # Allow sizes to be equal if needed
                        # Otherwise, if the values are invalid.
                        else:
                            # Print a warning message indicating the row is being skipped due to invalid numbers.
                            print(f"Warning: Skipping row {i+1} ('{label_original}') due to invalid numeric values (neg/zero/unordered). Values: S={small_g}, M={medium_g}, L={large_g}", file=sys.stderr)
                            # Continue to the next row.
                            continue

                    # Check if this lowercase label already exists in the table (to avoid duplicates).
                    if label_lower in table:
                        # If it's a duplicate, skip this row (keep the first one encountered).
                        continue

                    # If the data is valid and not a duplicate, add it to the table dictionary.
                    # The key is the lowercase label, the value is a tuple of the original label and the numeric data.
                    table[label_lower] = (label_original, calories_per_gram, small_g, medium_g, large_g)

                # If a ValueError occurs during float conversion (e.g., non-numeric text in a number column).
                except ValueError:
                    # Print a warning message indicating the row is skipped due to non-numeric data.
                    print(f"Warning: Skipping row {i+1} ('{label_original}') due to non-numeric value in cal/size.", file=sys.stderr)
                    # Continue to the next row.
                    continue

    # If any other exception occurs during file reading or processing.
    except Exception as e:
        # Print a general error message including the exception details.
        print(f"ERROR: Failed to read or parse '{path}': {e}", file=sys.stderr)
        # Return None to indicate failure.
        return None

    # After processing all rows, check if the table is empty.
    if not table:
        # If no valid data was loaded, print an error message.
        print(f"ERROR: No valid data loaded from '{path}'. Check file content and format.", file=sys.stderr)
        # Return None.
        return None

    # If data was loaded successfully, print a success message with the number of items loaded.
    print(f"Successfully loaded {len(table)} items from '{path}'.")
    # Return the populated table dictionary.
    return table


# --- Get Base Label Function ---
# Define a helper function to try and simplify a specific food label into a more generic one.
def _get_base_label(specific_label_lower: str) -> str:
    # Docstring explaining the function's purpose, arguments, and return value.
    """
    Derives a more generic base label by removing common modifiers from the end.

    Args:
        specific_label_lower (str): The lowercase specific food label.

    Returns:
        str: The potentially simplified base label (lowercase).
    """
    # Define a list of common words that modify food labels (adjectives, preparations, units, etc.).
    common_modifiers = [
        "medium", "large", "small", "plain", "cooked", "grilled", "baked",
        "fried", "roasted", "steamed", "raw", "mashed", "chopped", "diced",
        "grated", "shredded", "whole", "shelled", "pitted", "canned", "jarred",
        "sweetened", "unsweetened", "light", "regular", "full fat", "low sodium",
        "salted", "unsalted", "active dry", "unflavored", "black", "white",
        "red", "green", "yellow", "generic", "fresh", "frozen", "dried", "instant",
        "boneless", "skinless", "lean", "extra lean", "organic", "paste", "powder",
        "juice", "cocktail", "sauce", "dressing", "spread", "butter", "oil", "milk",
        "cream", "cheese", "syrup", "nectar", "soup", "stew", "chili", "curry",
        # Units sometimes appended erroneously - less likely now but keep for robustness
        "slice", "piece", "dish", "cup", "bowl", "plate", "glass", "can",
        "bottle", "scoop", "wedge", "stick", "bar", "patty", "fillet", "link",
        "strip", "quarter", "half", "spear", "floret", "leaf", "ring", "cube",
        "chunk", "ball", "log", "stalk", "sprig", "head", "bunch", "cob", "pod",
        "kernel", "bean", "nut", "seed", "berry", "loin", "chop", "roast", "breast",
        "thigh", "leg", "wing", "drumstick", "tender", "medallion", "steak"
    ]

    # Create a working copy of the input label after removing leading/trailing whitespace.
    current_label = specific_label_lower.strip()
    # Split the label into a list of words.
    parts = current_label.split()

    # Initialize a flag to control the loop.
    removed_modifier = True # Flag to control loop
    # Loop as long as a modifier was removed in the previous iteration and there's more than one word left.
    while removed_modifier and len(parts) > 1:
        # Reset the flag for the current iteration.
        removed_modifier = False
        # Get the last word of the current label parts.
        last_word = parts[-1]

        # Check if the label has at least two words to potentially form a compound name.
        if len(parts) > 1:
            # Get the second-to-last word.
            prev_word = parts[-2]
            # Define a list of compound food names that should not be broken up (e.g., "cream cheese").
            protected_compounds = [
                 "cream cheese", "cottage cheese", "blue cheese", "goat cheese",
                 "ice cream", "olive oil", "coconut oil", "peanut butter", "almond butter",
                 "soy milk", "almond milk", "oat milk", "green beans", "black beans",
                 "bell pepper", "sweet potato", "corn starch", "baking soda", "baking powder",
                 "hot sauce", "soy sauce", "fish sauce", "bbq sauce", "apple juice",
                 "orange juice", "maple syrup", "corn syrup", "brown sugar",
                 "whole wheat", "all purpose", "french fries", "onion rings",
                 "chicken breast", "pork chop", "ground beef", "ground turkey",
                 "new england", "manhattan", # For clam chowder
            ]
            # Check if the last two words form one of the protected compound names.
            if f"{prev_word} {last_word}" in protected_compounds:
                # If it's a protected compound name, stop trying to remove modifiers from this label.
                break # Stop removing if it's part of a protected compound name

        # Check if the last word itself is in the list of common modifiers.
        if last_word in common_modifiers:
            # Add specific exceptions where a modifier shouldn't be removed (e.g., 'pie' from 'apple pie').
            if current_label == "apple pie" and last_word == "pie": break
            if current_label == "beef stew" and last_word == "stew": break
            # If it's a removable modifier, remove the last word from the list of parts.
            parts = parts[:-1]
            # Set the flag to indicate a modifier was removed, allowing the loop to continue.
            removed_modifier = True
            # Reconstruct the current label string from the modified parts list for the next iteration check.
            current_label = " ".join(parts) # Update label for next iteration

    # After the loop finishes, return the potentially simplified label.
    return current_label # Return the most simplified label found

# --- get_unit_options Function ---
# Define the function to get a list of appropriate units for a given ingredient.
def get_unit_options(ingredient_label_lower: str) -> list[str]:
    # Docstring explaining the function's purpose, arguments, and return value.
    """
    Generates a sorted list of relevant unit options for the UI.

    Combines CORE_UNITS with units from CONVERSIONS for the ingredient (or base),
    filters out 'cup', and sorts logically based on unit type/commonality.

    Args:
        ingredient_label_lower (str): The lowercase label of the food ingredient.

    Returns:
        list[str]: A sorted list of applicable unit strings for the UI dropdown.
    """
    # Initialize a set with the core units (grams, small, medium, large).
    options = set(CORE_UNITS) # Start with grams, small, medium, large
    # If the input label is empty or None, return the sorted core units immediately.
    if not ingredient_label_lower: # Handle empty/None input gracefully
        return sorted(list(options))

    # Get the base label for the ingredient using the helper function.
    base_label = _get_base_label(ingredient_label_lower)
    # Create a set containing both the specific label and the base label to check for conversions.
    labels_to_check = {ingredient_label_lower, base_label}

    # Iterate through the labels to check (specific and base).
    for label in labels_to_check:
        # Check if this label exists as a key in the CONVERSIONS dictionary.
        if label in CONVERSIONS:
            # If it exists, iterate through the unit keys defined for this label.
            for unit in CONVERSIONS[label].keys():
                # Add each found unit to the set of options.
                options.add(unit)

    # Define a dictionary to assign sorting priorities to different units (lower number means higher priority/appears first).
    priority = {
        # Core / Size units have the highest priority.
        "grams": 0, "small": 1, "medium": 2, "large": 3,
        # Common measurement units.
        "oz": 10, "tsp": 11, "tbsp": 12,
        # Common countable units / pieces, grouped roughly.
        'each': 15, 'slice': 16, 'piece': 17, 'fruit': 18, 'egg': 19,
        'stick': 20, 'strip': 21, 'wing': 22, 'thigh': 23, 'leg': 24, 'breast': 25,
        'fillet': 26, 'chop': 27, 'link': 28, 'patty': 29, 'steak': 30,
        'ball': 31, 'cube': 32, 'wedge': 33, 'ring': 34, 'spear': 35, 'floret': 36,
        'leaf': 37, 'cob': 38, 'pod': 39, 'kernel': 40, 'bean': 41, 'nut': 42, 'seed': 43, 'berry': 44,
        # Containers / Serving-related units.
        'can': 50, 'bottle': 51, 'glass': 52, 'mug': 53, 'bowl': 54, 'packet': 55,
        'scoop': 56, 'pint': 57, 'shot': 58, 'bar': 59, 'square': 60, 'box': 61,
        'serving': 62, 'skewer': 63, 'ramekin': 64, 'log': 65,
        # Smaller / Approximate units.
        'splash': 70, 'drizzle': 71, 'dollop': 72, 'pat': 73, 'pinch': 74, 'dash': 75, 'bit': 76,
        # Fractional units.
        'half': 80, 'quarter': 81,
        # Give 'cup' low priority as it will be filtered out later for the UI.
        "cup": 98, # Give 'cup' low priority, it will be filtered anyway
    }
    # Assign a default low priority for any units not explicitly listed.
    other_priority = 99 # For any unlisted units

    # Sort the collected options first by their priority number, then alphabetically for units with the same priority.
    sorted_options = sorted(
        list(options),
        key=lambda x: (priority.get(x.lower(), other_priority), x)
    )

    # Create the final list by filtering out the 'cup' unit (often ambiguous or handled by other measures).
    final_options_list = [unit for unit in sorted_options if unit.lower() != 'cup']

    # Return the final sorted list of unit options.
    return final_options_list


# --- convert_to_grams Function ---
# Define the function to convert an amount of an ingredient in a specific unit to grams.
def convert_to_grams(
    # The ingredient label (lowercase).
    ingredient_label_lower: str,
    # The quantity of the ingredient (can be float or string).
    amount: float | str,
    # The unit of measurement for the amount.
    unit: str,
    # The loaded calorie data dictionary (needed for S/M/L conversions).
    calorie_data: dict # Still needed for S/M/L lookups from CSV
    # Specify the return type hint: a float (grams) or None if conversion fails.
    ) -> float | None:
    # Docstring explaining the function's purpose, arguments, and return value.
    """
    Converts a given amount and unit for an ingredient into grams.

    Prioritizes S/M/L lookup via calorie_data (CSV), then specific unit conversions
    from CONVERSIONS dict (checking base label as fallback), then generic fallbacks.
    Handles qualitative units where amount is implicitly 1.

    Args:
        ingredient_label_lower (str): The lowercase label of the food ingredient.
        amount (float | str): The quantity. Assumed 1.0 for qualitative units.
        unit (str): The unit of measurement.
        calorie_data (dict): Loaded calorie data for S/M/L gram lookups.

    Returns:
        float | None: Calculated weight in grams, or None if conversion fails.
                      Returns 0.0 for negative amounts.
    """
    # Basic input validation: check if essential arguments are provided.
    if not ingredient_label_lower or not unit or not calorie_data:
         # Print an error message if inputs are missing.
         print("Error: convert_to_grams received invalid input (label, unit, or calorie_data missing).", file=sys.stderr)
         # Return None to indicate failure.
         return None

    # Convert the unit string to lowercase for case-insensitive comparison.
    unit_lower = unit.lower()
    # Check if the unit is considered qualitative (implies quantity 1, like 'slice', 'small').
    is_qualitative = unit_lower in QUALITATIVE_UNIT_TERMS
    # Define units that strictly require a numeric amount to be provided by the user.
    needs_numeric_amount = unit_lower in ["grams", "oz", "tsp", "tbsp", "cup"]
    # Initialize the numeric amount variable, defaulting to 1.0 (used for qualitative units or if conversion fails).
    numeric_amount = 1.0 # Default for qualitative or if conversion fails below

    # --- Amount Validation ---
    # Validate the provided 'amount' only if the unit specifically requires it.
    if needs_numeric_amount:
        # Check if 'amount' is None when it's required.
        if amount is None: # Check if amount is missing when it's required
            # Print an error if the required amount is missing.
            print(f"Error: Numeric amount missing for required unit '{unit}' of '{ingredient_label_lower}'. Cannot convert.", file=sys.stderr)
            # Return None to indicate failure.
            return None
        # Try to convert the provided 'amount' to a float.
        try:
            # Attempt the conversion.
            numeric_amount = float(amount)
            # Check if the converted amount is negative.
            if numeric_amount < 0:
                # Print a warning and return 0.0 grams for negative amounts.
                print(f"Warning: Negative amount ({amount}) for {unit}. Treating as 0.")
                return 0.0
            # Allow explicit 0 grams.
            if numeric_amount == 0 and unit_lower == "grams":
                return 0.0 # Allow 0 grams explicitly
            # If amount is 0 for other units requiring amount, warn but allow calculation (will result in 0g).
            if numeric_amount == 0 and unit_lower != "grams":
                print(f"Warning: Zero amount provided for unit '{unit}' (other than grams). Result will be 0 grams.")
                # Allow calculation to proceed which will result in 0
        # If conversion to float fails (e.g., invalid text input).
        except (ValueError, TypeError):
            # Print an error message, indicating default amount 1.0 will be used for calculation attempt.
            print(f"Error: Invalid numeric amount ('{amount}') provided for unit '{unit}' of '{ingredient_label_lower}'. Defaulting to 1.0 for calculation attempt.", file=sys.stderr)
            # Set numeric_amount to 1.0 to allow the conversion attempt to proceed, although the result might be inaccurate.
            numeric_amount = 1.0 # Attempt with 1.0, but this might be misleading
            # Alternative: Return None here for stricter validation.
            # return None

    # If the unit is qualitative or doesn't strictly require numeric input, numeric_amount remains 1.0 or holds the validated value.

    # --- Conversion Logic ---

    # 1. Handle 'small', 'medium', 'large' sizes using data from the loaded calorie_data (CSV).
    if unit_lower in ["small", "medium", "large"]:
        # Initialize variable to hold the data tuple found in calorie_data.
        data_tuple = None
        # Get the base label for fallback lookup.
        base_label = _get_base_label(ingredient_label_lower)
        # Prioritize finding the exact label in the calorie data.
        if ingredient_label_lower in calorie_data:
            # If found, get the corresponding data tuple.
            data_tuple = calorie_data[ingredient_label_lower]
        # If exact label not found, and base label is different, try the base label.
        elif base_label != ingredient_label_lower and base_label in calorie_data: # Check base only if different
            # If base label found, get its data tuple.
            data_tuple = calorie_data[base_label]

        # If a data tuple (either from specific or base label) was found.
        if data_tuple:
            # Try to extract the correct gram value based on the unit (small/medium/large).
            try:
                # Map the unit name to the correct index in the data tuple (0=Label, 1=Cal/g, 2=Small_g, 3=Medium_g, 4=Large_g).
                size_index = {"small": 2, "medium": 3, "large": 4}[unit_lower]
                # Convert the gram value at the determined index to a float.
                gram_value = float(data_tuple[size_index])
                # Check if the gram value is valid (positive). Should be caught by loader, but double-check.
                if gram_value <=0: # Should be caught by loader, but double check
                    # Print an error if the S/M/L value from the CSV is invalid.
                    print(f"Error: S/M/L gram value is zero or negative for '{unit_lower}' of '{ingredient_label_lower}'. Check CSV data. Found: {gram_value}", file=sys.stderr)
                    # Return None as conversion failed.
                    return None
                # Return the fixed gram value directly for S/M/L sizes.
                return gram_value # Return the fixed S/M/L gram value directly
            # Handle potential errors during index lookup or float conversion.
            except (IndexError, ValueError, TypeError, KeyError):
                 # Print an error message if the data format in the CSV seems incorrect.
                 print(f"Error: Invalid S/M/L data format or index for '{ingredient_label_lower}' or base in calorie_data. Data: {data_tuple}", file=sys.stderr)
                 # Return None as conversion failed.
                 return None
        # If no data tuple was found for either the specific or base label.
        else:
            # This is critical because S/M/L was selected, but no corresponding data exists in the CSV.
            print(f"CRITICAL ERROR: Cannot find S/M/L gram data for '{ingredient_label_lower}' or its base label ('{base_label}') in calorie table (CSV). Conversion failed.", file=sys.stderr)
            # Return None as conversion cannot proceed.
            return None # Cannot perform conversion

    # 2. Handle the unit 'grams' directly.
    if unit_lower == "grams":
        # The numeric_amount has already been validated if needed; return it directly.
        return numeric_amount

    # 3. Handle the unit 'oz' (Ounces).
    if unit_lower == "oz":
        # The numeric_amount has been validated; multiply by the conversion factor (28.35 g/oz).
        return numeric_amount * 28.35

    # 4. Handle other units (tsp, tbsp, slice, each, etc.) using the CONVERSIONS dictionary.
    # Initialize the grams per unit factor.
    grams_per_unit = None
    # Get the base label once for potential fallback lookup.
    base_label = _get_base_label(ingredient_label_lower) # Get base label once

    # First, check if the specific ingredient label exists in CONVERSIONS and has the required unit defined.
    if ingredient_label_lower in CONVERSIONS and unit_lower in CONVERSIONS[ingredient_label_lower]:
        # If found, get the grams-per-unit value.
        grams_per_unit = CONVERSIONS[ingredient_label_lower][unit_lower]
    # If not found for the specific label, check if the base label (and if it's different) exists and has the unit.
    elif base_label != ingredient_label_lower and base_label in CONVERSIONS and unit_lower in CONVERSIONS[base_label]:
        # If found for the base label, get the grams-per-unit value.
        grams_per_unit = CONVERSIONS[base_label][unit_lower]

    # If a grams-per-unit value was found (either specific or base).
    if grams_per_unit is not None:
        # Try to convert the found value to a float and perform the calculation.
        try:
            # Convert the factor to float.
            gram_value_per_unit = float(grams_per_unit)
            # Check if the conversion factor is valid (positive).
            if gram_value_per_unit <=0:
                 # Print an error if the factor is non-positive.
                 print(f"Error: Gram value is zero or negative in CONVERSIONS for '{unit_lower}' of '{ingredient_label_lower}'. Value: {gram_value_per_unit}", file=sys.stderr)
                 # Allow falling through to generic fallbacks below if possible.
            # If the factor is valid.
            else:
                # Multiply the grams-per-unit factor by the validated numeric_amount (which is 1.0 for qualitative units).
                return gram_value_per_unit * numeric_amount
        # Handle potential errors during float conversion of the factor.
        except (ValueError, TypeError):
             # Print an error message if the value from CONVERSIONS is invalid.
             print(f"Error: Invalid grams_per_unit value ({grams_per_unit}) from CONVERSIONS for '{unit_lower}' of '{ingredient_label_lower}'.", file=sys.stderr)
             # Allow falling through to generic fallbacks below if possible.

    # 5. Generic Fallbacks (Least Preferred - used only if no specific/base conversion was found above).
    # Define very approximate gram equivalents for common units as a last resort.
    generic_fallbacks = {
        "tsp": 5.0, "tbsp": 15.0, "cup": 150.0, # Highly approximate liquid/powder refs
        "slice": 30.0, "piece": 50.0, "each": 100.0 # Highly approximate solid refs
    }
    # Check if the unit exists in the generic fallbacks dictionary.
    if unit_lower in generic_fallbacks:
         # Get the fallback gram value.
         fallback_grams = generic_fallbacks[unit_lower]
         # Print a warning indicating that a generic fallback is being used.
         print(f"Warning: Using GENERIC fallback '{unit_lower}' ({fallback_grams}g/unit) for '{ingredient_label_lower}'. Specific/base conversion data not found.", file=sys.stderr)
         # Multiply the fallback value by the validated numeric_amount.
         return numeric_amount * fallback_grams

    # --- Failure Case ---
    # If the unit did not match any conversion method (S/M/L, grams, oz, CONVERSIONS, generic fallbacks).
    print(f"ERROR: Conversion failed. Cannot determine gram equivalent for unit '{unit}' of '{ingredient_label_lower}'. No conversion method applicable.", file=sys.stderr)
    # Return None to indicate conversion failure.
    return None


# --- get_calories_per_gram Function ---
# Define the function to retrieve the calories per gram for a given label from the loaded data.
def get_calories_per_gram(label_lower: str, calorie_data: dict) -> float | None:
    # Docstring explaining the function's purpose, arguments, and return value.
    """
    Retrieves calories per gram from calorie_data (CSV), using fallbacks.

    Tries exact label -> base label -> first word.

    Args:
        label_lower (str): The lowercase food label.
        calorie_data (dict): The loaded calorie data dictionary from CSV.

    Returns:
        float | None: Calories per gram, or None if not found.
    """
    # Handle empty input label or missing calorie data.
    if not label_lower or not calorie_data: return None # Handle empty input

    # Remove leading/trailing whitespace from the label.
    label_lower = label_lower.strip()

    # 1. Try finding the exact lowercase label in the calorie data.
    if label_lower in calorie_data:
        # Try to access and convert the calories/gram value (index 1 in the tuple).
        try:
            # Convert the value to float.
            cal_value = float(calorie_data[label_lower][1])
            # Check if the calorie value is non-negative.
            if cal_value >= 0:
                # If valid, return the value.
                return cal_value
            # If negative, print a warning.
            else: print(f"Warning: Negative Calories_per_Gram found for '{label_lower}'. Ignoring.", file=sys.stderr)
        # Handle errors if the index is out of bounds or the value isn't a valid number.
        except (IndexError, ValueError, TypeError):
            # Print a warning indicating invalid format and that fallbacks will be tried.
            print(f"Warning: Invalid Calorie/Gram format for exact label '{label_lower}'. Trying fallbacks. Data: {calorie_data.get(label_lower)}", file=sys.stderr)
            # Allow the function to continue to the next fallback step.
            pass # Continue to fallbacks

    # 2. Try finding the base label (simplified label) in the calorie data.
    # Get the base label using the helper function.
    base_label = _get_base_label(label_lower)
    # Only attempt lookup if the base label is different from the original label and exists in the data.
    if base_label != label_lower and base_label in calorie_data: # Only check if base is different
         # Try to access and convert the calories/gram value for the base label.
         try:
             # Convert the value to float.
             cal_value = float(calorie_data[base_label][1])
             # Check if the calorie value is non-negative.
             if cal_value >= 0:
                 # If valid, return the value.
                 return cal_value
             # If negative, print a warning.
             else: print(f"Warning: Negative Calories_per_Gram found for base label '{base_label}'. Ignoring.", file=sys.stderr)
         # Handle errors if the index is out of bounds or the value isn't a valid number.
         except (IndexError, ValueError, TypeError):
             # Print a warning indicating invalid format and that the next fallback will be tried.
             print(f"Warning: Invalid Calorie/Gram format for base label '{base_label}'. Trying fallbacks. Data: {calorie_data.get(base_label)}", file=sys.stderr)
             # Allow the function to continue to the next fallback step.
             pass # Continue to fallbacks

    # 3. Last Resort: Try using only the first word of the original label.
    # Split the original label into words.
    parts = label_lower.split()
    # Get the first word, or an empty string if there are no parts.
    first_word_label = parts[0] if parts else ""
    # Attempt this fallback only if there was more than one word, the first word is reasonably long (>3 chars), and it exists in the data.
    if len(parts) > 1 and len(first_word_label) > 3 and first_word_label in calorie_data:
         # Try to access and convert the calories/gram value for the first word.
         try:
             # Convert the value to float.
             cal_value = float(calorie_data[first_word_label][1])
             # Check if the calorie value is non-negative.
             if cal_value >= 0:
                 # Print an info message indicating the first word fallback is being used.
                 print(f"Info: Using 1st word fallback '{first_word_label}' cals/g for '{label_lower}'.", file=sys.stderr)
                 # If valid, return the value.
                 return cal_value
             # If negative, print a warning.
             else: print(f"Warning: Negative Calories_per_Gram found for first word '{first_word_label}'. Ignoring.", file=sys.stderr)
         # Handle errors if the index is out of bounds or the value isn't a valid number.
         except (IndexError, ValueError, TypeError):
             # Print a warning indicating invalid format for the first word fallback.
             print(f"Warning: Invalid Calorie/Gram format for first word fallback '{first_word_label}'. Data: {calorie_data.get(first_word_label)}", file=sys.stderr)
             # If even the first word fallback fails, allow the function to proceed to the failure case.
             pass # If even first word fails, give up

    # --- Failure Case ---
    # If none of the lookup methods (exact, base, first word) yielded a valid result.
    print(f"ERROR: Could not find valid calories/gram data for '{label_lower}' or any suitable fallback in calorie table (CSV).", file=sys.stderr)
    # Return None to indicate failure.
    return None


# --- Calculate Total Calories Function ---
# Define the function to calculate total calories for a meal based on item gram weights.
def calculate_total_calories_new(
    # A dictionary where keys are lowercase ingredient labels and values are their gram weights.
    meal_items_grams: dict[str, float],
    # The loaded calorie data dictionary from the CSV.
    calorie_data: dict,
    # Specify the return type hint: a tuple containing a dictionary of item details and the total calories float.
    ) -> tuple[dict[str, tuple[float, str]], float]:
    # Docstring explaining the function's purpose, arguments, and return value.
    """
    Calculates total calories for a meal given ingredients and their gram weights.

    Args:
        meal_items_grams (dict[str, float]): Dict of {label: grams}. Grams should be valid float >= 0.
        calorie_data (dict): Loaded calorie data from CSV.

    Returns:
        tuple[dict[str, tuple[float, str]], float]:
            - Dict of {label: (item_calories, status_code)}
            - Total meal calories (float).
    """
    # Initialize an empty dictionary to store details about each item's calculation.
    item_details = {}
    # Initialize the total calorie count for the meal to zero.
    total_calories = 0.0

    # --- Input Validation ---
    # Check if the meal_items_grams argument is actually a dictionary.
    if not isinstance(meal_items_grams, dict):
        # Print an error if the input type is incorrect.
        print("Error: calculate_total_calories_new received invalid input type for meal_items_grams.", file=sys.stderr)
        # Return an empty details dictionary and zero total calories.
        return {}, 0.0
    # Check if the calorie_data argument is actually a dictionary.
    if not isinstance(calorie_data, dict):
        # Print an error if the input type is incorrect.
        print("Error: calculate_total_calories_new received invalid input type for calorie_data.", file=sys.stderr)
        # Return an empty details dictionary and zero total calories.
        return {}, 0.0

    # --- Process Each Item ---
    # Iterate through each item (label and grams) in the input meal dictionary.
    for label_lower, grams in meal_items_grams.items():
        # Initialize calories for the current item to zero.
        item_cal = 0.0
        # Initialize the float version of grams to zero.
        grams_float = 0.0
        # Initialize the calculation status code for this item.
        calculation_method = "error_initial" # Default status

        # Validate the 'grams' value received for this item.
        if grams is None:
             # Print an error if grams value is missing.
             print(f"Error: Grams value is None for item '{label_lower}'. Cannot calculate calories.", file=sys.stderr)
             # Store an error status for this item in the details dictionary.
             item_details[label_lower] = (0.0, "error_missing_grams")
             # Skip to the next item in the meal.
             continue
        # Try to convert the grams value to a float.
        try:
            # Attempt the conversion.
            grams_float = float(grams)
            # Check for negative grams (should ideally be caught earlier, but double-check).
            if grams_float < 0:
                # Print a warning and treat negative grams as zero.
                print(f"Warning: Negative grams ({grams}) passed to calorie calculation for '{label_lower}'. Treating as 0.", file=sys.stderr)
                # Set grams to zero.
                grams_float = 0.0
        # Handle errors if the grams value cannot be converted to a float.
        except (ValueError, TypeError):
            # Print an error message.
            print(f"Error: Invalid gram value ('{grams}') for item '{label_lower}' during calorie calculation.", file=sys.stderr)
            # Store an error status for this item.
            item_details[label_lower] = (0.0, "error_invalid_grams_calc")
            # Skip to the next item.
            continue # Skip to the next item

        # Attempt to get the calories per gram for this item using the helper function (includes fallbacks).
        cal_per_gram = get_calories_per_gram(label_lower, calorie_data)

        # Check if a valid (non-None, non-negative) calories per gram value was found.
        if cal_per_gram is not None and cal_per_gram >= 0:
            # Calculate the calories for this item (grams * calories/gram).
            item_cal = grams_float * cal_per_gram
            # Set the calculation method status to indicate success.
            calculation_method = "calculated_per_gram"
            # Add the item's calories to the running total for the meal.
            total_calories += item_cal # Add to the running total
        # If no valid calories per gram value was found after all fallbacks.
        else:
            # Set the item's calories to zero.
            item_cal = 0.0
            # Set the status code to indicate missing calorie data.
            calculation_method = "error_missing_cals_per_gram"
            # Print an error message (the get_calories_per_gram function likely already printed specifics).
            print(f"Error: Cannot calculate calories for '{label_lower}' due to missing/invalid cal/g data. Setting item calories to 0.", file=sys.stderr)

        # Store the calculated calories (or 0.0 on error) and the status code for this item.
        item_details[label_lower] = (item_cal, calculation_method)

    # After processing all items, return the dictionary of item details and the final total calories.
    return item_details, total_calories



# --- Predict Food Label via Roboflow Classification Function (MODIFIED) ---
def predict_food_label_roboflow(
    image_bytes: bytes,
    api_key: str,
    model_id: str,
    api_url: str = "https://serverless.roboflow.com" # Default URL, can be overridden
) -> tuple[str | None, float | None]:
    """
    Sends an image to a specified Roboflow CLASSIFICATION model for food label prediction.

    Parses the specific Roboflow classification response structure to extract
    the top predicted class label and its confidence score.
    Handles API key validation, temporary file management, and potential errors.

    Args:
        image_bytes (bytes): The image data as bytes.
        api_key (str): The Roboflow API key.
        model_id (str): The Roboflow Model ID (e.g., "your-project-name/version_number").
        api_url (str): The Roboflow API endpoint URL.
                       Defaults to "https://detect.roboflow.com".
                       Use "https://serverless.roboflow.com" for serverless deployments if needed.

    Returns:
        tuple[str | None, float | None]:
            - The predicted food label (lowercase string) if successful, else None.
            - The confidence score (float) for the predicted label, else None.
            - Returns (None, None) if prediction fails, API key is invalid/missing,
              model ID is missing, or the Roboflow SDK is not installed/functional.
    """
    predicted_label = None
    confidence = None

    # # --- Input Validation & SDK Check ---
    # if InferenceHTTPClient is None:
    #     print("CRITICAL Error: Roboflow SDK not installed or import failed. Please run: pip install roboflow", file=sys.stderr)
    #     return None, None

    if not api_key:
        print("Error: Roboflow API Key not provided.", file=sys.stderr)
        return None, None
    if isinstance(api_key, list):
        if len(api_key) == 1 and isinstance(api_key[0], str): api_key = api_key[0]
        else: print("Error: Invalid API Key format (expected string or list with one string).", file=sys.stderr); return None, None

    if not model_id:
         print("Error: Roboflow Model ID not provided.", file=sys.stderr)
         return None, None

    # --- Client Setup ---
    try:
        # *** Use the provided api_url parameter ***
        print(f"[Debug] Initializing Roboflow client with API URL: {api_url}")
        client = InferenceHTTPClient(api_url=api_url, api_key=api_key)
    except Exception as client_e:
        print(f"Error: Failed to initialize Roboflow client: {client_e}", file=sys.stderr)
        return None, None

    # --- Temporary File Handling & API Call ---
    temp_image_path = None
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as temp_image_file:
            temp_image_file.write(image_bytes)
            temp_image_path = temp_image_file.name

        print(f"[Debug] Calling Roboflow Model ID: '{model_id}' at URL: {api_url}")
        raw_result = client.infer(inference_input=temp_image_path, model_id=model_id)

        # --- Response Parsing (Specific for Classification) ---
        print("[Debug] --- Roboflow Raw Result ---")
        try:
            print(json.dumps(raw_result, indent=2))
        except TypeError:
            print(f"[Debug] Raw Value (not JSON serializable): {raw_result}")
        print("[Debug] ------------------------------------")

        # --- Validate top‑level structure ---
        if not isinstance(raw_result, dict):
            print(f"[Error] Expected a dict as the Roboflow response, but got: {type(raw_result)}", file=sys.stderr)
            return None, None

        # --- Pull out the predictions dict ---
        main_preds = raw_result.get("predictions")
        if not isinstance(main_preds, dict):
            print(f"[Error] Could not find 'predictions' dict in response: {raw_result}", file=sys.stderr)
            return None, None

        # --- Pull out the predicted_classes list ---
        predicted_classes_list = raw_result.get("predicted_classes")
        if not isinstance(predicted_classes_list, list):
            print(f"[Error] Expected 'predicted_classes' to be a list, but got: {type(predicted_classes_list)}", file=sys.stderr)
            return None, None
        if not predicted_classes_list:
            print("[Info] 'predicted_classes' is empty. No prediction.", file=sys.stderr)
            return None, None

        # --- Top label, normalized ---
        predicted_label_raw = predicted_classes_list[0]
        if not isinstance(predicted_label_raw, str):
            print(f"[Error] Expected string in 'predicted_classes', but got: {type(predicted_label_raw)}", file=sys.stderr)
            return None, None
        predicted_label = predicted_label_raw.strip().lower()

        # --- Look up its confidence ---
        details = main_preds.get(predicted_label_raw) or main_preds.get(predicted_label)
        confidence = 0.0
        if isinstance(details, dict):
            conf_value = details.get("confidence")
            if isinstance(conf_value, (int, float)):
                confidence = float(conf_value)
            else:
                print(f"[Warning] Confidence for '{predicted_label}' is not numeric: {conf_value}", file=sys.stderr)
        else:
            print(f"[Warning] No details found for predicted label '{predicted_label}'.", file=sys.stderr)

        # --- Final Output ---
        print(f"[Info] Predicted Label: '{predicted_label}' (Confidence: {confidence:.4f})")
        return predicted_label, confidence


    # --- Error Handling & Cleanup ---
    except Exception as e:
        print(f"[Error] An exception occurred during Roboflow prediction or response parsing: {e}", file=sys.stderr)
        # import traceback # Uncomment for detailed traceback
        # traceback.print_exc(file=sys.stderr)
        return None, None
    finally:
        if temp_image_path and os.path.exists(temp_image_path):
            try:
                os.unlink(temp_image_path)
            except Exception as e_unlink:
                print(f"[Error] Failed to delete temporary file {temp_image_path}: {e_unlink}", file=sys.stderr)

    return None, None # Fallback


# Set this once with your real Assistant ID
ASSISTANT_ID = "asst_Qwxm9bSS2gu771Cqx3jG46B6"  # ← Replace with your Assistant ID from OpenAI

def chatbot_response(user_input, thread_id, stage):
    # Step 1: Create thread if needed
    if thread_id == 0:
        thread = openai.beta.threads.create()
        thread_id = thread.id

    # Step 2: Define instructions per stage
    if stage == 1:
        instructions = (
            "You're given the name of a food identified by the model. Be warm and lively—compliment the user's choice with a short message that fits the food type. "
            "Mention if it's more of a snack, a breakfast pick, or a hearty dinner, but keep it casual and cheerful."
        )
    elif stage == 2:
        instructions = (
            "You'll now learn how much of the food the user plans to eat. React with a fun or witty line—something playful, curious, or encouraging. "
            "It can be light-hearted, teasing, or enthusiastic—just make it sound like a natural conversation."
        )
    elif stage == 3:
        instructions = (
            "You’ll now see the estimated calorie content of the meal. Offer a brief comment that reflects on the size of the meal—maybe it’s a light lunch, a filling dinner, or a treat. "
            "Feel free to get creative with tone, but stay supportive and helpful."
        )
    else:
        instructions = (
            "You’re now in an open chat with the user. You are CAMHEALTH, a friendly and smart nutrition assistant. "
            "Answer questions only about food, health, nutrition, ingredients, or calories. If someone asks about anything off-topic, gently remind them of your role. "
            "Keep replies short, smart, and evidence-based when needed—refer to sources like the USDA or WHO when you share facts."
            "Always be specific in answering quesions, and provide approximate calorie values always."
        )

    try:
        # Step 3: Add user's message to the thread
        openai.beta.threads.messages.create(
            thread_id=thread_id,
            role="user",
            content=user_input
        )

        # Step 4: Run assistant with updated instructions
        run = openai.beta.threads.runs.create(
            thread_id=thread_id,
            assistant_id=ASSISTANT_ID,
            instructions=instructions
        )

        # Step 5: Wait for completion
        while True:
            run_status = openai.beta.threads.runs.retrieve(thread_id=thread_id, run_id=run.id)
            if run_status.status in ["completed", "failed", "cancelled"]:
                break

        # Step 6: Return response or error
        if run_status.status == "completed":
            messages = openai.beta.threads.messages.list(thread_id=thread_id)
            latest = messages.data[0].content[0].text.value
            print(latest, thread_id)
            return latest, thread_id
        else:
            return f"Run error (status: {run_status.status})", thread_id

    except Exception as e:
        return f"Error: {e}", thread_id



# %%
