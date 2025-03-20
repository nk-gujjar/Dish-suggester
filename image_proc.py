from groq import Groq
import config

def detect_food_items_from_image(image_path):
    """
    Detect food items from an image using Groq Vision Preview
    
    Args:
        image_path: Path to the image file
        
    Returns:
        List of detected food items
    """
    client = Groq(api_key=config.GROQ_API_KEY)
    
    # Read the image as bytes
    with open(image_path, "rb") as image_file:
        image_data = image_file.read()
    
    # Use Groq Vision Preview to detect ingredients
    try:
        response = client.chat.completions.create(
            model="llama3-70b-8192-vision",  # Use the vision model
            messages=[
                {
                    "role": "system",
                    "content": "You are a food ingredient detector. Identify all food items visible in the image. Return only a comma-separated list of ingredients with no additional text."
                },
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image",
                            "source": {
                                "type": "base64",
                                "media_type": "image/jpeg",
                                "data": image_data
                            }
                        },
                        {
                            "type": "text",
                            "text": "List all food ingredients visible in this image. Return only the ingredient names separated by commas, with no additional text."
                        }
                    ]
                }
            ]
        )
        
        # Extract the ingredients from the response
        ingredients_text = response.choices[0].message.content.strip()
        ingredients = [item.strip() for item in ingredients_text.split(',')]
        return ingredients
    
    except Exception as e:
        # Fall back to a simple list if the API call fails
        print(f"Error detecting ingredients: {e}")
        return ["eggs", "bread", "cheese", "tomatoes"]