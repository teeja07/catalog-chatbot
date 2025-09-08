from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
import openai

app = FastAPI()

# Allow frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load pricelist
df = pd.read_csv("pricelist.csv")

openai.api_key = "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"

@app.post("/chat")
async def chat(request: Request):
    data = await request.json()
    user_query = data["message"]

    # Simple search in catalog
    matches = df[df.apply(lambda row: user_query.lower() in str(row).lower(), axis=1)]

    if not matches.empty:
        product_info = matches.iloc[0].to_dict()
        context = f"Catalog No: {product_info['Catalog No.']}, Product: {product_info['Product Name']}, Price: ₹{product_info['Price (₹)']}, Stock: {product_info['Stock']}, Description: {product_info['Description']}"
    else:
        context = "No exact match found. Suggest related products."

    # ChatGPT generates natural reply
    response = openai.ChatCompletion.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a helpful assistant for a product catalog."},
            {"role": "user", "content": f"Customer query: {user_query}\nRelevant product info: {context}"}
        ]
    )

    return {"reply": response.choices[0].message["content"]}
