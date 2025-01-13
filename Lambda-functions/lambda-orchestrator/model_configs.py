from langchain_aws import ChatBedrockConverse
from dotenv import load_dotenv
load_dotenv()

def get_bedrock_llm(model="amazon.nova-micro-v1:0", temperature=0.7, top_p=0.9, max_tokens=512):
  llm = ChatBedrockConverse(model=model, temperature=temperature, max_tokens=max_tokens, top_p=top_p)
  return llm