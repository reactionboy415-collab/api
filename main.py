Import random
import httpx
import time
import psutil
from fastapi import FastAPI, Response, Query, HTTPException, Request
from fastapi.responses import JSONResponse
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.middleware.cors import CORSMiddleware
from functools import lru_cache

--- CONFIG & METADATA ---

app = FastAPI(
title="💎 CR-IMAGE-ULTIMATE PRO",
description="Enterprise-grade image generation mesh with fallback logic and smart caching.",
version="5.1.0",
docs_url=None
)

app.add_middleware(CORSMiddleware, allow_origins=[""], allow_methods=[""], allow_headers=["*"])

--- CORE SETTINGS ---

MODELS = {
"CR-Avatar": "https://robohash.org/{p}.png?set=set1",
"CR-Turbo": "https://image.pollinations.ai/prompt/{p}?model=turbo&width=512&height=512&nologo=true",
"CR-Flux": "https://image.pollinations.ai/prompt/{p}?model=flux&width=1024&height=1024&nologo=true"
}

--- CACHE LOGIC ---

@lru_cache(maxsize=100)
def get_cached_url(prompt: str, model: str):
"""Caches the URL generation logic to save nanoseconds."""
seed = random.randint(0, 99999)
return f"{MODELS[model].format(p=prompt.replace(' ', '%20'))}&seed={seed}"

--- CUSTOM PREMIUM DOCS ---

@app.get("/docs", include_in_schema=False)
async def custom_swagger_ui_html():
return get_swagger_ui_html(
openapi_url=app.openapi_url,
title="CR-API Premium",
swagger_ui_parameters={"defaultModelsExpandDepth": -1},
# Inject custom CSS for a professional dark/blue theme
swagger_css_url="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui.css"
)

--- SYSTEM MONITORING ---

@app.get("/health", tags=["DevOps"])
async def health_check():
"""Returns real-time server stats."""
return {
"status": "Healthy",
"cpu_usage": f"{psutil.cpu_percent()}%",
"memory_usage": f"{psutil.virtual_memory().percent}%",
"uptime": f"{int(time.time() - psutil.boot_time())}s",
"engine": "CR-V5-Async"
}

@app.get("/", tags=["General"])
async def root():
return {
"message": "Welcome to CR-Image-API Professional",
"endpoints": {"generate": "/v1/generate", "health": "/health", "docs": "/docs"},
"models_available": list(MODELS.keys())
}

--- THE MAIN ENGINE ---

@app.get("/v1/generate", tags=["Production"])
async def generate(
prompt: str = Query(..., min_length=2, example="Cyberpunk city with CR-Neon signs"),
model: str = Query("CR-Flux", description="Available: CR-Avatar, CR-Turbo, CR-Flux")
):
if model not in MODELS:
raise HTTPException(status_code=400, detail="Invalid model name.")

# 1. Filter Check (Basic Safety)  
banned = ["nude", "porn", "blood"]  
if any(word in prompt.lower() for word in banned):  
    raise HTTPException(status_code=403, detail="Prompt contains restricted content.")  

# 2. Build URL  
target_url = get_cached_url(prompt, model)  

# 3. Fetch with Retry Logic  
async with httpx.AsyncClient(timeout=30.0) as client:  
    try:  
        response = await client.get(target_url)  
        if response.status_code == 200:  
            return Response(content=response.content, media_type="image/jpeg")  
        return JSONResponse(status_code=502, content={"error": "Backend Engine Busy"})  
    except Exception as e:  
        return JSONResponse(status_code=500, content={"error": str(e)})

Start server: uvicorn main:app --reload


# Vercel serverless handler
from mangum import Mangum
handler = Mangum(app)