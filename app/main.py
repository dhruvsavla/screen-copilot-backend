# app/main.py
from fastapi import FastAPI
from app.routes import analyze, stream_ws
import uvicorn
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI(title="Screen Copilot Backend")

# Enable CORS for your frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # React app
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(analyze.router, prefix="/api")
app.include_router(stream_ws.router, prefix="/ws")

@app.get("/")
async def root():
    return {"ok": True, "msg": "Screen Copilot backend alive"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
