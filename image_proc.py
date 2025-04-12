

import tempfile
import os
import base64
from groq import Groq
from dotenv import load_dotenv
from pymongo import MongoClient
from gridfs import GridFS

# Load environment variables
load_dotenv()
MONGO_URI = os.getenv("MONGO_URI")
DB_NAME = os.getenv("DB_NAME")
GROQ_API_KEY = os.getenv("GROQ_API_KEY_VISION")

# MongoDB setup
client = MongoClient(MONGO_URI)
db = client[DB_NAME]
fs = GridFS(db)

def upload_image_to_mongodb(image_path):
    """
    Uploads the image to MongoDB using GridFS and returns its binary data.
    """
    with open(image_path, "rb") as f:
        binary_data = f.read()
        fs_id = fs.put(binary_data, filename=os.path.basename(image_path))
        return fs_id, binary_data

def generate_data_url(image_binary, mime_type="image/jpeg"):
    """
    Converts binary image data to a base64 data URL for use with Groq.
    """
    base64_str = base64.b64encode(image_binary).decode("utf-8")
    return f"data:{mime_type};base64,{base64_str}"

def detect_food_items_from_image(image_bytes):
    """
    Detect food items from an image using Groq Vision.
    Accepts image as bytes, writes temporarily, deletes after use.
    """
    temp_path = None
    try:
        # Save uploaded image bytes to a temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp_file:
            tmp_file.write(image_bytes)
            temp_path = tmp_file.name

        # Upload to MongoDB and get binary
        _, image_binary = upload_image_to_mongodb(temp_path)
        image_data_url = generate_data_url(image_binary)

        # Call Groq Vision
        client = Groq(api_key=GROQ_API_KEY)
        completion = client.chat.completions.create(
            model="llama-3.2-11b-vision-preview",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": "You are a food ingredient detector. Identify all food items visible in the image. Return only a comma-separated list of ingredients with no additional text."
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": image_data_url
                            }
                        }
                    ]
                }
            ],
            temperature=1,
            max_completion_tokens=1024,
            top_p=1,
            stream=False,
        )

        ingredients_text = completion.choices[0].message.content.strip()
        ingredients = [item.strip() for item in ingredients_text.split(',')]
        return ingredients

    except Exception as e:
        print(f"[ERROR] Detection failed: {e}")
        return ["Error: Detection failed"]

    finally:
        # Cleanup temp file if it exists
        if temp_path and os.path.exists(temp_path):
            os.remove(temp_path)
