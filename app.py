import os, base64
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"status": "running"}

# -------- CHAT --------
class ChatRequest(BaseModel):
    message: str

@app.post("/chat")
async def chat(req: ChatRequest):
    try:
        r = client.responses.create(
            model="gpt-4o-mini",
            max_output_tokens=300,
            input=req.message
        )
        return {"reply": r.output_text.strip()}
    except Exception as e:
        raise HTTPException(500, str(e))

# -------- IMAGE + TEXT --------
@app.post("/analyze")
async def analyze(image: UploadFile = File(...), text: str = Form(...)):
    try:
        img = await image.read()
        if len(img) > 1_000_000:
            raise HTTPException(400, "Image too large")

        b64 = base64.b64encode(img).decode()

        r = client.responses.create(
            model="gpt-4o-mini",
            max_output_tokens=400,
            input=[{
                "role": "user",
                "content": [
                    {"type": "input_text", "text": text[:500]},
                    {"type": "input_image",
                     "image_url": f"data:{image.content_type};base64,{b64}"}
                ]
            }]
        )
        return {"result": r.output_text.strip()}
    except Exception as e:
        raise HTTPException(500, str(e))

# -------- AI APP BUILDER --------
class AppRequest(BaseModel):
    prompt: str

@app.post("/generate-app")
async def generate_app(req: AppRequest):
    try:
        r = client.responses.create(
            model="gpt-4o-mini",
            max_output_tokens=1200,
            input=f"""
Create a single-file interactive web app.

Rules:
- One HTML file
- Inline CSS & JS
- Functional
- No explanations
- Output only code

App:
{req.prompt}
"""
        )
        return {"code": r.output_text}
    except Exception as e:
        raise HTTPException(500, str(e))











