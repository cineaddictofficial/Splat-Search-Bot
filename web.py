from fastapi import FastAPI
import uvicorn
import threading
import os

app = FastAPI()

@app.get("/")
async def root():
    return {"status": "alive", "bot": "Popzy Movies Bot"}

def run():
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)

def keep_alive():
    t = threading.Thread(target=run)
    t.start()
