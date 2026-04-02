import google.generativeai as genai
from dotenv import load_dotenv
import os
from PIL import Image

load_dotenv()

genai.configure(api_key=os.getenv("GEMINI_API_KEY", ""))

model = genai.GenerativeModel("gemini-2.0-flash-exp")


async def generate_with_gemini(prompt: str, image_path: str = None) -> tuple:
    try:
        if image_path and os.path.exists(image_path):
            image = Image.open(image_path)
            response = model.generate_content([prompt, image])
        else:
            response = model.generate_content(prompt)

        return response.text, None
    except Exception as e:
        return f"Error: {str(e)}", None
