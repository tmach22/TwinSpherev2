from fastapi import FastAPI, File, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
from typing import List
from pydantic import BaseModel
import tempfile
import shutil
import uuid
import asyncio
import os
from letta_client import Letta
from simulation import run_simulation_with_image
from dotenv import load_dotenv
load_dotenv()

SHARED_BLOCK_LABEL = "public_reactions"

client = Letta(token=os.getenv("LETTA_API_KEY"))

app = FastAPI()

# CORS setup for Streamlit UI
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/simulate/")
async def simulate_post_with_image(
    image_url: str = Form(...),
    post_text: str = Form(...),
    post_id: str = Form(...)
):
    # Save uploaded image to temp file
    # image_path = None
    # if image:
    #     with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp:
    #         shutil.copyfileobj(image.file, tmp)
    #         image_path = tmp.name

    # Load all active agents
    try:
        agents = client.agents.list()
    except Exception as e:
        return {"error": f"Failed to list agents: {str(e)}"}
    
    existing = client.blocks.list(label=SHARED_BLOCK_LABEL)

    # Run simulation
    try:
        results = await run_simulation_with_image(
            agents=agents,
            post_id=post_id,
            post_text=post_text,
            image_url=image_url,
            shared_block_id=existing[0].id
        )
        return results
    except Exception as e:
        return {"error": f"Simulation failed: {str(e)}"}
