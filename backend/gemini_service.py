import requests
import os
from dotenv import load_dotenv
from PIL import Image

load_dotenv()

API_URL = "https://api-inference.huggingface.co/models/google/flan-t5-base"

headers = {
    "Authorization": f"Bearer {os.getenv('HF_API_KEY')}"
}

from PIL import Image

def analyze_image(input_data):
    try:
        if isinstance(input_data, str):
            text = input_data
        else:
            image = Image.open(input_data)
            text = "Plastic bottle"   # dummy prediction

        result = f"""
Waste Item: Plastic Bottle
Waste Category: Plastic
Recyclable: Yes
Sri Lanka Disposal Guide: Use blue recycling bin
Environmental Impact: Takes 400+ years to decompose
Reuse Idea: Use as plant pot
Eco Tip: Avoid single-use plastics
"""

        return {
            "success": True,
            "text": result,
            "model": "offline-demo"
        }

    except Exception as e:
        return {
            "success": False,
            "text": str(e),
            "model": None
        }