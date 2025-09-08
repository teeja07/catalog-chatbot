from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
import openai
import os

# Load environment variable (your OpenAI API key must be set in Render/locally)
openai.api_key = os.getenv("OPENAI_API_KEY")

# Load your pricelist (CSV with columns: Catalog No., Product Name, Description, Price (₹), Stock)
df = pd.read_csv("pricelist.csv")

app = FastAPI()

# Allow frontend (JS widget) to call API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # Replace "*" with your domain in production
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/chat")
async def chat(request: Request):
    data = await request.json()
    user_query = data.get("message", "")

    # Search product data
    matches = df[df.apply(lambda row: user_query.lower() in str(row).lower(), axis=1)]

    if not matches.empty:
        product_info = matches.iloc[0].to_dict()
        context = (
            f"Catalog No: {product_info['Catalog No.']}, "
            f"Product: {product_info['Product Name']}, "
            f"Price: ₹{product_info['Price (₹)']}, "
            f"Stock: {product_info['Stock']}, "
            f"Description: {product_info['Description']}"
        )
    else:
        context = "No exact match found. Suggest related products."

    # Ask ChatGPT to generate a nice response
    response = openai.ChatCompletion.create(
        model="gpt-4o-mini",   # you can also use "gpt-4o" or "gpt-3.5-turbo"
        messages=[
            {"role": "system", "content": "You are a helpful assistant for a product catalog."},
            {"role": "user", "content": f"Customer query: {user_query}\nRelevant product info: {context}"}
        ]
    )

    reply_text = response.choices[0].message.content
    return {"reply": reply_text}
