from langchain_core.messages import SystemMessage, HumanMessage
from prompt_templates import DECISION_AGENT_TEMPLATE
from langgraph.graph import StateGraph, START, END
from model_configs import get_bedrock_llm

llm_decision = get_bedrock_llm(temperature=0, max_tokens=20)
llm_answering_questions = get_bedrock_llm(model="amazon.nova-lite-v1:0")
llm_call_to_action = get_bedrock_llm()
llm_example_generator = get_bedrock_llm()

response = llm_decision.invoke([
  SystemMessage(content=DECISION_AGENT_TEMPLATE), 
  HumanMessage(content="Hola buena noche, quisiera saber de que trata el servicio de IA que ofrecen")
])

print(response)
# content='Use Case 1' 
# additional_kwargs={} 
# response_metadata={'ResponseMetadata': {'RequestId': '451d7812-62fd-4c97-8f1d-d5e931af35ac', 'HTTPStatusCode': 200, 'HTTPHeaders': {'date': 'Mon, 13 Jan 2025 03:53:29 GMT', 'content-type': 'application/json', 'content-length': '192', 'connection': 'keep-alive', 'x-amzn-requestid': '451d7812-62fd-4c97-8f1d-d5e931af35ac'}, 'RetryAttempts': 0}, 'stopReason': 'end_turn', 'metrics': {'latencyMs': [189]}} 
# id='run-daa8f015-ad4c-4943-9aad-ff9fa1c85777-0' 
# usage_metadata={'input_tokens': 548, 'output_tokens': 4, 'total_tokens': 552}