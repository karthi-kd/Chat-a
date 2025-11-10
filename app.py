 
from fastapi import FastAPI, Form
from fastapi.middleware.cors import CORSMiddleware
from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()  # Loads .env
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

app = FastAPI(title="My ChatGPT AI")

# Allow frontend requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ChatGPT-style endpoint
@app.post("/chat")
def chat(prompt: str = Form(...)):
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",  # or "gpt-4-turbo"
            messages=[
                {"role": "system", "content": "You are a helpful AI named Karthi AI."},
                {"role": "user", "content": prompt}
            ]
        )
        reply = response.choices[0].message.content
        return {"reply": reply}
    except Exception as e:
        return {"error": str(e)}