

import streamlit as st
import os
import numpy as np
from PIL import Image
import requests
import json
import base64
from io import BytesIO
from groq import Groq
import config  # Import the config file

# Initialize Groq client
client = Groq(api_key=config.GROQ_API_KEY)

# Mock food detection system (replace with actual CV model in production)
MOCK_FOOD_ITEMS = [
    ["eggs", "bread", "cheese", "tomatoes"],
    ["chicken", "rice", "broccoli", "soy sauce"],
    ["flour", "sugar", "butter", "eggs"],
    ["pasta", "tomato sauce", "basil", "garlic"],
    ["beef", "lettuce", "tomatoes", "buns"]
]

def detect_food_items(image):
    """Mock food detection system for demonstration purposes"""
    # In a real application, replace this with actual computer vision logic
    # and a proper image recognition API/service
    return np.random.choice(MOCK_FOOD_ITEMS[np.random.randint(0, len(MOCK_FOOD_ITEMS))])

def get_recipe_suggestions(ingredients, max_missing=3):
    """Get recipe suggestions based on available ingredients."""
    ingredients_str = ", ".join(ingredients)
    
    try:
        response = client.chat.completions.create(
            model="llama3-70b-8192",
            messages=[
                {"role": "system", "content": """You are a culinary expert. Suggest recipes based on available ingredients.
                Format your response as JSON with:
                {
                    "recipes": [
                        {
                            "name": "Recipe Name",
                            "available_ingredients": ["list", "of", "ingredients"],
                            "missing_ingredients": ["list", "of", "missing", "ingredients"],
                            "instructions": "Brief instructions"
                        }
                    ]
                }
                Include only recipes with ≤3 missing ingredients. Sort by fewest missing."""},
                {"role": "user", "content": f"I have: {ingredients_str}. What can I make? Provide 5 recipes."}
            ],
            temperature=0.7,
            max_tokens=1000,
            response_format={"type": "json_object"}
        )
        
        return json.loads(response.choices[0].message.content)
    except Exception as e:
        st.error(f"Error getting recipes: {str(e)}")
        return {"recipes": []}

def suggest_additional_ingredients(current_ingredients):
    """Suggest additional ingredients that would enable more recipes."""
    ingredients_str = ", ".join(current_ingredients)
    
    try:
        response = client.chat.completions.create(
            model="llama3-70b-8192",
            messages=[
                {"role": "system", "content": """You are a culinary expert. Suggest additional ingredients.
                Format response as JSON with:
                {
                    "suggestions": [
                        {
                            "ingredient": "Ingredient Name",
                            "enables_recipes": ["Recipe 1", "Recipe 2"]
                        }
                    ]
                }"""},
                {"role": "user", "content": f"I have: {ingredients_str}. What should I add to enable more recipes?"}
            ],
            temperature=0.7,
            max_tokens=500,
            response_format={"type": "json_object"}
        )
        
        return json.loads(response.choices[0].message.content)
    except Exception as e:
        st.error(f"Error getting suggestions: {str(e)}")
        return {"suggestions": []}

# Streamlit UI Configuration
st.set_page_config(page_title="Recipe Suggestion App", layout="wide")
st.title("🍳 What Can I Cook?")
st.subheader("Get recipe suggestions based on ingredients you have")

# Input Methods
st.sidebar.title("Input Methods")
input_method = st.sidebar.radio("Choose input method:", ["Upload Image", "Enter Ingredients"])

ingredients = []

if input_method == "Upload Image":
    uploaded_file = st.sidebar.file_uploader("Upload ingredients image", type=["jpg", "jpeg", "png"])
    if uploaded_file:
        image = Image.open(uploaded_file)
        st.sidebar.image(image, use_column_width=True)
        
        if st.sidebar.button("Detect Ingredients"):
            with st.spinner("Detecting ingredients..."):
                try:
                    ingredients = detect_food_items(image)
                    st.session_state.ingredients = ingredients
                except Exception as e:
                    st.error(f"Detection error: {str(e)}")
else:
    manual_input = st.sidebar.text_area("Enter ingredients (comma-separated)")
    if st.sidebar.button("Set Ingredients"):
        ingredients = [x.strip() for x in manual_input.split(",") if x.strip()]
        st.session_state.ingredients = ingredients

# Display Ingredients
st.subheader("Your Ingredients")
if 'ingredients' in st.session_state and st.session_state.ingredients:
    ingredients = st.session_state.ingredients
    edited = st.text_area("Edit ingredients:", value="\n".join(ingredients), height=150)
    updated = [x.strip() for x in edited.split("\n") if x.strip()]
    
    if updated != ingredients:
        st.session_state.ingredients = updated
        st.experimental_rerun()
else:
    st.info("No ingredients added. Use the sidebar to add ingredients.")

# Recipe Suggestions
if 'ingredients' in st.session_state and st.session_state.ingredients:
    if st.button("Get Recipe Suggestions"):
        with st.spinner("Finding recipes..."):
            recipes = get_recipe_suggestions(st.session_state.ingredients)
            st.session_state.recipes = recipes

if 'recipes' in st.session_state:
    st.subheader("Suggested Recipes")
    recipes = st.session_state.recipes.get('recipes', [])
    
    if recipes:
        for recipe in recipes:
            with st.expander(f"{recipe['name']} (Missing: {len(recipe['missing_ingredients'])})"):
                cols = st.columns(3)
                cols[0].write("**You Have:**")
                cols[0].write(", ".join(recipe['available_ingredients']))
                
                cols[1].write("**Missing:**")
                cols[1].write(", ".join(recipe['missing_ingredients']))
                
                cols[2].write("**Instructions:**")
                cols[2].write(recipe['instructions'])
    else:
        st.info("No recipes found with current ingredients.")

# Ingredient Suggestions
if 'ingredients' in st.session_state and st.session_state.ingredients:
    if st.button("Suggest Additional Ingredients"):
        with st.spinner("Finding suggestions..."):
            suggestions = suggest_additional_ingredients(st.session_state.ingredients)
            st.session_state.suggestions = suggestions

if 'suggestions' in st.session_state:
    st.subheader("Ingredient Suggestions")
    for suggestion in st.session_state.suggestions.get('suggestions', []):
        with st.expander(f"Add {suggestion['ingredient']}"):
            st.write("**Enables Recipes:**")
            st.write(", ".join(suggestion['enables_recipes']))
            if st.button(f"Add {suggestion['ingredient']}", key=suggestion['ingredient']):
                if suggestion['ingredient'] not in st.session_state.ingredients:
                    st.session_state.ingredients.append(suggestion['ingredient'])
                    st.experimental_rerun()

st.markdown("---")
st.caption("Powered by Groq LLM and Streamlit")