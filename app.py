import os
import base64
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
from openai import OpenAI

# ---------------- Load environment variables ----------------
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Initialize OpenAI client
if not OPENAI_API_KEY:
    raise ValueError("⚠️ OPENAI_API_KEY not found in environment variables.")
client = OpenAI(api_key=OPENAI_API_KEY)

# ---------------- FastAPI setup ----------------
app = FastAPI(title="AI Builder Backend")

# Enable CORS (allow all origins for testing)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Change to your frontend URL in production
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------- Root ----------------
@app.get("/")
def root():
    return {"status": "AI Builder Backend running"}

# ---------------- Text Chat ----------------
class ChatRequest(BaseModel):
    message: str

@app.post("/chat")
async def chat(req: ChatRequest):
    try:
        response = client.responses.create(
            model="gpt-4.1-mini",
            input=req.message
        )
        return {"reply": response.output_text}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ---------------- Image + Text Analysis ----------------
@app.post("/analyze")
async def analyze(
    image: UploadFile = File(...),
    text: str = Form(...)
):
    try:
        image_bytes = await image.read()
        image_base64 = base64.b64encode(image_bytes).decode("utf-8")

        response = client.responses.create(
            model="gpt-4.1-mini",
            input=[
                {
                    "role": "user",
                    "content": [
                        {"type": "input_text", "text": text},
                        {"type": "input_image", "image_base64": image_base64}
                    ]
                }
            ]
        )
        return {"result": response.output_text}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ---------------- Website Generator ----------------
class WebsiteRequest(BaseModel):
    prompt: str
    language: str = "html"  # default output language

@app.post("/generate-website")
async def generate_website(req: WebsiteRequest):
    try:
        response = client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=[
                {
                    "role": "user",
                    "content": (
                        f"Generate a complete {req.language} website for the following description:\n"
                        f"{req.prompt}\nProvide only the code without explanations."
                    )
                }
            ],
            max_tokens=3000
        )
        return {"website_code": response.choices[0].message.content}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))










