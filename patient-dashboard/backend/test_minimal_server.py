#!/usr/bin/env python3
"""Minimal server test to isolate issues"""

from fastapi import FastAPI
import uvicorn

app = FastAPI()

@app.get("/health")
def health_check():
    return {"status": "healthy", "message": "Minimal server working"}

if __name__ == "__main__":
    print("Starting minimal test server on port 8002...")
    uvicorn.run(app, host="0.0.0.0", port=8002)