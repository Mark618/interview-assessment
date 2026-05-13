import asyncio
import base64
from contextlib import asynccontextmanager
from pydantic import BaseModel
from typing import List, Optional
from io import BytesIO
import logging
import time

from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse,RedirectResponse
import numpy as np

import chromadb
from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline
import torch
import json

formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
ch.setFormatter(formatter)
logger.addHandler(ch)

uvicorn_logger = logging.getLogger("uvicorn")
uvicorn_logger.handlers.clear()
uvicorn_logger.setLevel(logging.DEBUG)
uvicorn_logger.addHandler(ch)

LLM_MODEL = None
TOKENIZER = None
CHROMA_DB_PATH = "chroma_db"
client = chromadb.PersistentClient(path=CHROMA_DB_PATH)
collection_name = "task_2_1"
collection = client.get_or_create_collection(collection_name)

@asynccontextmanager
async def load_model(app:FastAPI):
    global LLM_MODEL, TOKENIZER
    logger.info("Load LLM Model")
    
    try:
        LLM_MODEL = AutoModelForCausalLM.from_pretrained("Qwen/Qwen2.5-3B-Instruct-AWQ",device_map="cuda",torch_dtype=torch.float16) 
        TOKENIZER = AutoTokenizer.from_pretrained("Qwen/Qwen2.5-3B-Instruct-AWQ") 
    except Exception as e:
        logger.error(e)
        raise
    
    yield
    
    logger.info("API shutdown")
    del LLM_MODEL, TOKENIZER


app = FastAPI(title="Assignment 3 API",description="For Agent API",lifespan=load_model)

class CalcRequest(BaseModel):
    operation: str  # add, subtract, multiply, divide
    a: float
    b: float

@app.post("/calculator")
async def calculator(req: CalcRequest):
    if req.operation == "add":
        result = req.a + req.b
    elif req.operation == "subtract":
        result = req.a - req.b
    elif req.operation == "multiply":
        result = req.a * req.b
    elif req.operation == "divide":
        if req.b != 0 :
            result = req.a / req.b 
        else :
            result="Error: Division by zero"
    else:
        result = "Invalid operation"
    logger.info({"result": result})
    return {"result": result}




def extract_person_metadata(person_info,temperature,do_sample_flag=False):
  prompt_template=f"""
  You are an expert digital transformation specialist tasked with extracting person metadata.
  Your goal is to extract specific information from the provided person description and output it strictly as a JSON object.
  Ensure the JSON is perfectly valid and can be directly loaded by a JSON parser (e.g., `json.loads()` in Python).

  The JSON object must contain only the following keys with their specified data types:
  - "Name": (string) - Name of the person.
  - "position": (string) - The job position of the person.
  - "location": (string) - The working location of the person.  

  Example of expected JSON format:
  ```json
  {{
    "Name": "John Smith",
    "position": "technician",
    "location": "Block A",
  }}
  ```

  ---
  Person Information to Extract Metadata From:
  {person_info}
  ---

  Your JSON Metadata Output:
  ```json
  """
  
  messages = [{"role": "user", "content": prompt_template}]
  text = TOKENIZER.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
  model_inputs = TOKENIZER([text], return_tensors="pt").to(LLM_MODEL.device)
  outputs = LLM_MODEL.generate(**model_inputs,max_new_tokens=8000,
                           temperature=temperature,do_sample=do_sample_flag,)
  json_string = TOKENIZER.decode(outputs[0][model_inputs["input_ids"].shape[-1]:],skip_special_tokens=True)
  
  clean_json_string = json_string.strip()
  if clean_json_string.startswith("```json") and clean_json_string.endswith("```"):
      clean_json_string = clean_json_string[len("```json"): -len("```")].strip()
  
  return clean_json_string  

class DataEntryRequest(BaseModel):
    text: str

@app.post("/data-entry")
async def data_entry(req: DataEntryRequest):
    # Simulate keyword extraction (in real case, you'd use NLP)
    try:
        json_string=extract_person_metadata(req.text,0.0)
        parsed_json = json.loads(json_string)
        print("\n--- Parsed JSON Data ---")
        print(json.dumps(parsed_json, indent=2))
        print("\nJSON successfully parsed!")
    except Exception as e:
        print(f"Could not load json: {e}")
        return {"status": "Failed", "extracted_data": None}
    
    return {"status": "success", "extracted_data": parsed_json}



class RAGRequest(BaseModel):
    question: str

@app.post("/rag-query")
def rag_query(req: RAGRequest):
    user_query = req.question
    context = collection.query(
        query_texts=[user_query],
        n_results=5
    )['documents'][0]

    prompt = f"{user_query}. Use this as context for answering: {context}. Keep it short and simple."
    messages = [{"role": "user", "content": prompt}]
    inputs = TOKENIZER.apply_chat_template(
        messages,
        add_generation_prompt=True,
        tokenize=True,
        return_dict=True,
        return_tensors="pt",
    ).to(LLM_MODEL.device)

    outputs = LLM_MODEL.generate(**inputs,max_new_tokens=8000)
    answer=TOKENIZER.decode(outputs[0][inputs["input_ids"].shape[-1]:])
    return {"answer": answer}
        



@app.get("/", include_in_schema=False)
async def index():
    return RedirectResponse(url="/docs")