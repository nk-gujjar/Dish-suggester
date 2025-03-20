from groq import Groq
import config
import json

class RecipeService:
    def __init__(self):
        """Initialize the recipe service with Groq client"""
        self.client = Groq(api_key=config.GROQ_API_KEY)
    
    def get_recipe_suggestions(self, ingredients, max_missing=3):
        """
        Get recipe suggestions based on available ingredients
        
        Args:
            ingredients: List of available ingredients
            max_missing: Maximum number of missing ingredients allowed
            
        Returns:
            Dictionary containing recipe suggestions
        """
        try:
            response = self.client.chat.completions.create(
                model="llama3-70b-8192",
                messages=[{
                    "role": "system",
                    "content": f"""You are a chef. Suggest recipes using {', '.join(ingredients)}.
                    Format as JSON with: recipes[name, available_ingredients[], missing_ingredients[], instructions]
                    Max {max_missing} missing ingredients. Sort by fewest missing."""
                }],
                temperature=0.7,
                response_format={"type": "json_object"}
            )
            return json.loads(response.choices[0].message.content)
        except Exception as e:
            print(f"Recipe error: {str(e)}")
            return {"recipes": []}
    
    def suggest_additional_ingredients(self, current_ingredients):
        """
        Get ingredient suggestions that complement current ingredients
        
        Args:
            current_ingredients: List of current ingredients
            
        Returns:
            Dictionary containing ingredient suggestions
        """
        try:
            response = self.client.chat.completions.create(
                model="llama3-70b-8192",
                messages=[{
                    "role": "system",
                    "content": f"Suggest 3 ingredients that complement {', '.join(current_ingredients)}. Format as JSON with suggestions[ingredient, enables_recipes[]]"
                }],
                temperature=0.7,
                response_format={"type": "json_object"}
            )
            return json.loads(response.choices[0].message.content)
        except Exception as e:
            print(f"Suggestion error: {str(e)}")
            return {"suggestions": []}