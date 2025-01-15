from prompt_templates import DECISION_AGENT_TEMPLATE, ANSWERING_Q_AGENT_TEMPLATE, EXAMPLES_G_AGENT_TEMPLATE, CALL_TO_ACTION_AGENT_TEMPLATE
from langchain_core.messages import SystemMessage, HumanMessage
from langgraph.graph import StateGraph, START, END, MessagesState
from langchain_aws import ChatBedrockConverse
from dotenv import load_dotenv
load_dotenv()

llm_decision = ChatBedrockConverse(model="amazon.nova-micro-v1:0", temperature=0.5, top_p=0, max_tokens=20)
llm_answering_questions = ChatBedrockConverse(model="amazon.nova-lite-v1:0", temperature=0.7, top_p=0.9, max_tokens=512)
llm_example_generator = ChatBedrockConverse(model="amazon.nova-micro-v1:0", temperature=0.7, top_p=0.9, max_tokens=512)
llm_call_to_action = ChatBedrockConverse(model="amazon.nova-micro-v1:0", temperature=0.7, top_p=0.9, max_tokens=512)

class AgentState(MessagesState):
  """State for the multi-stage agent workflow"""
  decision: str
  company_name: str
  location: str
  installation_time: str
  contact: str

def decision_agent(state: AgentState):
  response = llm_decision.invoke([SystemMessage(content=DECISION_AGENT_TEMPLATE)] + state["messages"])
  return {"decision": response.content}

def answering_questions(state: AgentState):
  return {"messages": llm_answering_questions.invoke([SystemMessage(content=ANSWERING_Q_AGENT_TEMPLATE)] + state["messages"])}

def example_generator(state: AgentState):
  return {"messages": llm_example_generator.invoke([SystemMessage(content=EXAMPLES_G_AGENT_TEMPLATE)] + state["messages"])}

def call_to_action(state: AgentState):
  return {"messages": llm_call_to_action.invoke([SystemMessage(content=CALL_TO_ACTION_AGENT_TEMPLATE)] + state["messages"])}

# Build the state graph
builder = StateGraph(AgentState)
builder.add_node("decision_agent", decision_agent)
builder.add_node("answering_questions", answering_questions)
builder.add_node("example_generator", example_generator)
builder.add_node("call_to_action", call_to_action)

# Add edges and conditional logic
builder.add_edge(START, "decision_agent")

def route_decision(state: AgentState):
  decision = state["decision"]
  if "Use Case 1" in decision:
    return "answering_questions"
  elif "Use Case 2" in decision:
    return "example_generator"
  elif "Use Case 3" in decision:
    return "call_to_action"
  elif "Malicious Query" in decision:
    return END
  else:
    print(f"Unrecognized decision: {decision}")  # Debugging line
    return END  # Default case to avoid returning None

builder.add_conditional_edges("decision_agent", route_decision, ["answering_questions", "example_generator", "call_to_action", END])

# Compile the graph
graph = builder.compile()
# Initialize the state with messages
message = input("Mensaje para la IA: ")
initial_state = {
  "messages": [HumanMessage(content=message)],
  "decision": "",
  "company_name": "",
  "location": "",
  "installation_time": "",
  "contact": ""
}
# Invoke the graph
result = graph.invoke(initial_state) 

# Print the final output
print(f"result: {result}\n")

# Bedrock res:
# content='<category>\n"Use Case 2"\n</category>' additional_kwargs={} response_metadata={'ResponseMetadata': {'RequestId': 'b1c29feb-72a9-45c0-aa02-b2ccfc229253', 'HTTPStatusCode': 200, 'HTTPHeaders': {'date': 'Tue, 14 Jan 2025 04:59:14 GMT', 'content-type': 'application/json', 'content-length': '222', 'connection': 'keep-alive', 'x-amzn-requestid': 'b1c29feb-72a9-45c0-aa02-b2ccfc229253'}, 'RetryAttempts': 0}, 'stopReason': 'end_turn', 'metrics': {'latencyMs': [215]}} id='run-2f720b81-2cb4-4f5a-8679-951c2c0f5f4c-0' usage_metadata={'input_tokens': 567, 'output_tokens': 12, 'total_tokens': 579}

# LangGraph state:
# {'messages': [HumanMessage(content='Hola buena tarde, Mi empresa vende vinos y tomo mensajes por whatssapp, puedo implementar su IA?', additional_kwargs={}, response_metadata={}, id='3b3623f5-227e-4db1-90aa-344ea1b2e60c'), AIMessage(content='¡Hola! Buenas tardes. Sí, su empresa puede implementar el agente de inteligencia artificial de coxcox.ai, dado que actualmente solo trabaja con mensajes de WhatsApp y también vende productos.\n\n- **Para implementar el agente:**\n  - Envíe un correo electrónico a "albertog1meza@gmail.com" manifestando su interés en el agente de coxcox.ai.\n  - Adjunte el nombre de su empresa, su ubicación y el tiempo disponible para que una persona vaya e instale el agente en su empresa.\n\nEspero que esto le haya ayudado. ¡Que tenga un excelente día!', additional_kwargs={}, response_metadata={'ResponseMetadata': {'RequestId': '79a3c737-55e0-49ca-b05a-e4c63e7a7761', 'HTTPStatusCode': 200, 'HTTPHeaders': {'date': 'Wed, 15 Jan 2025 04:43:07 GMT', 'content-type': 'application/json', 'content-length': '737', 'connection': 'keep-alive', 'x-amzn-requestid': '79a3c737-55e0-49ca-b05a-e4c63e7a7761'}, 'RetryAttempts': 0}, 'stopReason': 'end_turn', 'metrics': {'latencyMs': [1367]}}, id='run-86075042-f84b-45f9-a8e8-12c4c86a7927-0', usage_metadata={'input_tokens': 896, 'output_tokens': 129, 'total_tokens': 1025})], 'decision': 'Use Case 1', 'company_name': '', 'location': '', 'installation_time': '', 'contact': ''}