# 🥘 Dish Suggester

Welcome to **Dish Suggester**, a smart food assistant powered by AI that helps you generate recipes and get ingredient suggestions based on either a **manually written list** or an **image of ingredients**!

You can use it directly here:  
🌐 [https://dish-suggester.streamlit.app/](https://dish-suggester.streamlit.app/)

---

## 🚀 Features

- 📸 **Image-Based Ingredient Detection**  
  Upload an image of your ingredients – the app will analyze it using a Groq Vision API and extract the ingredients.

- 📝 **Manual Ingredient Entry**  
  Prefer typing it yourself? Just list out the ingredients manually.

- 🧠 **AI-Generated Recipes**  
  Using the LLaMA model via Groq APIs, the app suggests recipe ideas based on the available ingredients.

- 🔄 **Update Ingredients**  
  Easily add or remove ingredients at any step to refine your results.

- 💡 **Ingredient Suggestions**  
  Don’t have enough? The AI suggests extra ingredients to enhance your dish.

---

## 📂 Project Structure

```
├── app.py              # Main Streamlit app
├── image_proc.py       # Image processing and MongoDB GridFS storage
├── recipe_service.py   # LLaMA-based recipe generator using Groq APIs
├── requirements.txt    # Required dependencies
```

---

## ▶️ How to Run Locally

1. **Install Requirements**

```bash
pip install -r requirements.txt
```

2. **Set Credentials**

Before running the app, you need to configure your credentials:

- **Groq API Key**: Set your Groq API key as an environment variable or add it to the config file.

  ```bash
  export GROQ_API_KEY="your-groq-api-key"
  ```

- **MongoDB Credentials**: Set your MongoDB connection string (with credentials) as an environment variable or in the config file.

  ```bash
  export MONGODB_URI="mongodb+srv://<username>:<password>@cluster.mongodb.net/<dbname>"
  ```

3. **Start the App**

```bash
streamlit run app.py
```

> ⚠️ Make sure you have set the correct **Groq API key** and **MongoDB credentials** in your environment variables or configuration files.

---

## 🛠 Tech Stack

- **Streamlit** – Frontend framework
- **Groq Vision API** – For ingredient detection from images
- **LLaMA Model via Groq** – For recipe generation and suggestions
- **MongoDB + GridFS** – For storing images temporarily

---

## 📷 Image Handling

- Uploaded images are temporarily stored in **MongoDB GridFS**.
- After processing, ingredients are extracted and the image is deleted.

---

## 🔧 Core Features

- **Manual Ingredient Entry** – Type your ingredients to get recipe ideas.
- **Image-Based Ingredient Detection** – Upload a photo of ingredients.
- **Get Recipe Ideas** – LLaMA model generates recipes.
- **Update Ingredients** – Modify the list to improve results.
- **Ingredient Suggestions** – Get helpful additions to expand your options.

---

## 📌 Notes

- This project is part of a smart food assistant initiative by [Nitesh Kumar](https://www.linkedin.com/in/nitesh-kumar-gurjar/).
- Perfect for users who want to creatively use the ingredients they already have at home.

---

## 📃 License

This project is open-sourced under the **MIT License**.

---

Enjoy smarter cooking with AI! 🍳
```
