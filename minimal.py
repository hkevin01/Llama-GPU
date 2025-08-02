#!/usr/bin/env python3
"""Minimal FastAPI server."""

from fastapi import FastAPI

app = FastAPI()

@app.get("/")
async def root():
    """Root endpoint."""
    return {"message": "Hello World"}
