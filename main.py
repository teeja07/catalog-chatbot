from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
import openai
import os

# Get OpenAI key from environment
openai.api_key = os.getenv("OPENAI_API_KEY")
if not openai.api_key:
    raise ValueError("OPENAI_API_KEY not set!")

# Load pricelist CSV
df = pd.read_csv("pricelist.csv")

app = FastAPI()

# Allow frontend JS to call
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Replace "*" with your domain in production
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/chat")
async def chat(request: Request):
    try:
        data = await request.json()
        user_query = data.get("message", "").strip()
        if not user_query:
            return {"reply": "Please type a message."}

        # Search catalog
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

        # Call OpenAI
        response = openai.ChatCompletion.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a helpful assistant for a product catalog."},
                {"role": "user", "content": f"Customer query: {user_query}\nRelevant product info: {context}"}
            ]
        )
        reply_text = response.choices[0].message.content
        return {"reply": reply_text}

    except Exception as e:
        return {"reply": f"⚠️ Error: {str(e)}"}
