from langchain.agents import Tool, initialize_agent,AgentType
from langgraph.prebuilt import create_react_agent
from langgraph.checkpoint.memory import MemorySaver
from langchain_huggingface.llms import HuggingFacePipeline
import requests

from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline
import torch

def get_calc(input1:int, input2:int, mode:str):
    resp= requests.post("http://localhost:9900/calculator",
                        json={
                            "operation":mode,
                            "a": input1,
                            "b": input2
                        })
    return resp.json()["result"]

calculator_tool = Tool(
                    name="calculator",
                    func=get_calc,
                    description="Use this tool to get the two number mathematic operation including add, substract, multiply and divide."
                )



def get_dataentry(user_input:str):
    resp= requests.post("http://localhost:9900/data-entry",
                        json={
                            "text":user_input
                        })
    return resp.json()["extracted_data"]

data_entry_tool = Tool(
                    name="data_entry",
                    func=get_dataentry,
                    description="Use this tool to extract the keywords of a person in a sentences and this function will return result in defined JSON format."
                )


def get_rag(user_input:str):
    resp= requests.post("http://localhost:9900/rag-query",
                        json={
                            "question":user_input
                        })
    return resp.json()["answer"]

rag_tool = Tool(
                    name="rag_for_renewable_energy",
                    func=get_rag,
                    description="Use this tool to answer question on renewable energy affairs. This function will return a long text."
                )





LLM_MODEL = AutoModelForCausalLM.from_pretrained("Qwen/Qwen2.5-3B-Instruct-AWQ",device_map="cuda",torch_dtype=torch.float16) 
TOKENIZER = AutoTokenizer.from_pretrained("Qwen/Qwen2.5-3B-Instruct-AWQ") 

pipe = pipeline("text-generation", model=LLM_MODEL, tokenizer=TOKENIZER, max_new_tokens=8000)
hf = HuggingFacePipeline(pipeline=pipe)
tools = [calculator_tool,data_entry_tool,rag_tool]

memory = MemorySaver()
agent = initialize_agent(tools,hf,agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,verbose=False)


list_query = ["What is 10 multiply 150 equals to?","Adam Halen is our company Software Engineer, he is working at Kuala Lumpur. Extract information and reply in JSON format.","What are the main challenges in renewable energy storage technologies?"]


ag_respond = agent.invoke(list_query[2])
print(ag_respond)