import streamlit as st
import os
import tempfile
from PIL import Image
import image_proc
from recipe_service import RecipeService

# Initialize the recipe service
recipe_service = RecipeService()

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
                    # Save the uploaded image to a temporary file
                    with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp_file:
                        image.save(tmp_file.name)
                        temp_path = tmp_file.name
                    
                    # Use the image processor to detect ingredients
                    detected = image_proc.detect_food_items_from_image(temp_path)
                    
                    # Clean up the temporary file
                    os.unlink(temp_path)
                    
                    # Update the ingredients list
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
        st.rerun()  # Fixed: Using st.rerun() instead of st.experimental_rerun()
else:
    st.info("No ingredients added yet. Use the sidebar to get started!")

# Recipe Generation
if st.session_state.ingredients:
    if st.button("🧑‍🍳 Get Recipe Ideas"):
        with st.spinner("Generating recipe ideas..."):
            try:
                st.session_state.recipes = recipe_service.get_recipe_suggestions(st.session_state.ingredients)
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
                st.session_state.suggestions = recipe_service.suggest_additional_ingredients(st.session_state.ingredients)
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
                    st.rerun()  # Fixed: Using st.rerun() instead of st.experimental_rerun()
            st.caption(f"Enables: {', '.join(sug['enables_recipes'][:3])}")

st.markdown("---")
st.caption("Powered by Groq's Llama 3 AI • 🍳 Happy Cooking!")