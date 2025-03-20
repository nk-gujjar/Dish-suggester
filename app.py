
import streamlit as st
import random
from PIL import Image
from groq import Groq
import config
import json

# Initialize Groq client
client = Groq(api_key=config.GROQ_API_KEY)

# Improved mock food detection system
MOCK_FOOD_ITEMS = [
    ["eggs", "bread", "cheese", "tomatoes"],
    ["chicken", "rice", "broccoli", "soy sauce"],
    ["flour", "sugar", "butter", "eggs"],
    ["pasta", "tomato sauce", "basil", "garlic"],
    ["beef", "lettuce", "tomatoes", "buns"]
]

def detect_food_items(image):
    """Improved mock food detection with proper list handling"""
    return random.choice(MOCK_FOOD_ITEMS)

def get_recipe_suggestions(ingredients, max_missing=3):
    """Get recipe suggestions based on available ingredients."""
    try:
        response = client.chat.completions.create(
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
        st.error(f"Recipe error: {str(e)}")
        return {"recipes": []}

def suggest_additional_ingredients(current_ingredients):
    """Get ingredient suggestions with proper error handling"""
    try:
        response = client.chat.completions.create(
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
        st.error(f"Suggestion error: {str(e)}")
        return {"suggestions": []}

# Streamlit UI Setup
st.set_page_config(page_title="Smart Recipe Assistant", layout="wide")
st.title("🍳 Smart Recipe Assistant")

# Session state initialization
if 'ingredients' not in st.session_state:
    st.session_state.ingredients = []
if 'recipes' not in st.session_state:
    st.session_state.recipes = {}
if 'suggestions' not in st.session_state:
    st.session_state.suggestions = {}

# Sidebar Inputs
st.sidebar.header("Input Methods")
input_method = st.sidebar.radio("Select input:", ["📷 Camera Upload", "✍️ Manual Input"])

if input_method == "📷 Camera Upload":
    uploaded_file = st.sidebar.file_uploader("Upload ingredients photo", type=["jpg", "jpeg", "png"])
    if uploaded_file:
        image = Image.open(uploaded_file)
        st.sidebar.image(image, caption="Uploaded Ingredients", use_container_width=True)
        
        if st.sidebar.button("🔍 Analyze Image"):
            with st.spinner("Analyzing ingredients..."):
                try:
                    detected = detect_food_items(image)
                    st.session_state.ingredients = list(set(detected))  # Ensure unique items
                    st.success(f"Detected: {', '.join(detected)}")
                except Exception as e:
                    st.error(f"Detection failed: {str(e)}")

else:
    manual_input = st.sidebar.text_area("List ingredients (comma-separated)", height=150)
    if st.sidebar.button("✅ Save Ingredients"):
        if manual_input:
            ingredients = [x.strip() for x in manual_input.split(",") if x.strip()]
            st.session_state.ingredients = list(set(ingredients))  # Remove duplicates
            st.success("Ingredients saved!")

# Main Interface
st.subheader("Your Ingredients 🛒")
if st.session_state.ingredients:
    edited = st.text_area("Edit your ingredients list:", 
                         value="\n".join(st.session_state.ingredients),
                         height=150,
                         key="ingredients_editor")
    
    if st.button("🔄 Update Ingredients"):
        updated = [x.strip() for x in edited.split("\n") if x.strip()]
        st.session_state.ingredients = list(set(updated))
        st.rerun()
else:
    st.info("No ingredients added yet. Use the sidebar to get started!")

# Recipe Generation
if st.session_state.ingredients:
    if st.button("🧑‍🍳 Get Recipe Ideas"):
        with st.spinner("Generating recipe ideas..."):
            try:
                st.session_state.recipes = get_recipe_suggestions(st.session_state.ingredients)
            except Exception as e:
                st.error(f"Failed to generate recipes: {str(e)}")

# Display Recipes
if st.session_state.recipes.get('recipes'):
    st.subheader("Recommended Recipes 📜")
    for idx, recipe in enumerate(st.session_state.recipes['recipes']):
        with st.expander(f"{recipe['name']} ({len(recipe['missing_ingredients'])} missing)"):
            col1, col2 = st.columns([1, 3])
            with col1:
                st.markdown("**Available Ingredients**")
                st.write(", ".join(recipe['available_ingredients']))
                st.markdown("**Missing Ingredients**")
                st.write(", ".join(recipe['missing_ingredients']) or "None")
            with col2:
                st.markdown("**Instructions**")
                st.write(recipe['instructions'])

# Ingredient Suggestions
if st.session_state.ingredients:
    if st.button("💡 Get Ingredient Suggestions"):
        with st.spinner("Finding smart additions..."):
            try:
                st.session_state.suggestions = suggest_additional_ingredients(st.session_state.ingredients)
            except Exception as e:
                st.error(f"Failed to get suggestions: {str(e)}")

# Display Suggestions
if st.session_state.suggestions.get('suggestions'):
    st.subheader("Smart Additions 🛍️")
    for sug in st.session_state.suggestions['suggestions']:
        col1, col2 = st.columns([2, 3])
        with col1:
            st.markdown(f"**{sug['ingredient']}**")
        with col2:
            if st.button(f"Add {sug['ingredient']}", key=f"add_{sug['ingredient']}"):
                if sug['ingredient'] not in st.session_state.ingredients:
                    st.session_state.ingredients.append(sug['ingredient'])
                    st.rerun()
            st.caption(f"Enables: {', '.join(sug['enables_recipes'][:3])}")

st.markdown("---")
st.caption("Powered by Groq's Llama 3 AI • 🍳 Happy Cooking!")