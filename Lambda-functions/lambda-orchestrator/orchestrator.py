from langchain_core.messages import SystemMessage, HumanMessage
from prompt_templates import DECISION_AGENT_TEMPLATE, ANSWERING_Q_AGENT_TEMPLATE, EXAMPLES_G_AGENT_TEMPLATE, CALL_TO_ACTION_AGENT_TEMPLATE
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
  final_output: str

def decision_agent(state: AgentState):
  response = llm_decision.invoke([SystemMessage(content=DECISION_AGENT_TEMPLATE)] + state["messages"])
  return {"decision": response.content}

def answering_questions(state: AgentState):
  response = llm_answering_questions.invoke([SystemMessage(content=ANSWERING_Q_AGENT_TEMPLATE)] + state["messages"])
  return {"final_output": response.content}

def example_generator(state: AgentState):
  response = llm_example_generator.invoke([SystemMessage(content=EXAMPLES_G_AGENT_TEMPLATE)] + state["messages"])
  return {"final_output": response.content}

def call_to_action(state: AgentState):
  response = llm_call_to_action.invoke([SystemMessage(content=CALL_TO_ACTION_AGENT_TEMPLATE)] + state["messages"])
  return {"final_output": response.content}

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

builder.add_conditional_edges("decision_agent", route_decision, ["answering_questions", "example_generator", "call_to_action", END])

# Compile the graph
graph = builder.compile()
# Initialize the state with messages
initial_state = {
  "messages": [HumanMessage(content="Hola buena noche, recibi su propuesta hacerca del servicio de inteligencia artificial, me podria proporcionar un ejemplo de como funciona? para darme mas o menos una idea")],
  "decision": "",
  "final_output": ""
}
# Invoke the graph
result = graph.invoke(initial_state) 

# Print the final output
print(f"result: {result}\n")
print(result["final_output"])

# Bedrock res:
# content='<category>\n"Use Case 2"\n</category>' additional_kwargs={} response_metadata={'ResponseMetadata': {'RequestId': 'b1c29feb-72a9-45c0-aa02-b2ccfc229253', 'HTTPStatusCode': 200, 'HTTPHeaders': {'date': 'Tue, 14 Jan 2025 04:59:14 GMT', 'content-type': 'application/json', 'content-length': '222', 'connection': 'keep-alive', 'x-amzn-requestid': 'b1c29feb-72a9-45c0-aa02-b2ccfc229253'}, 'RetryAttempts': 0}, 'stopReason': 'end_turn', 'metrics': {'latencyMs': [215]}} id='run-2f720b81-2cb4-4f5a-8679-951c2c0f5f4c-0' usage_metadata={'input_tokens': 567, 'output_tokens': 12, 'total_tokens': 579}

# LangGraph state:
# {'messages': [HumanMessage(content='Hola buena noche, recibi su propuesta hacerca del servicio de inteligencia artificial, me podria proporcionar un ejemplo de como funciona? para darme mas o menos una idea', additional_kwargs={}, response_metadata={}, id='1da8f0e3-f523-4b11-a909-4b0e121c004a')], 'decision': '<category>\n"Use Case 2"\n</category>', 'final_output': '- Imaginemos una empresa que vende productos de belleza, como cremas, lociones y productos para el cuidado del cabello, y recibe mensajes de sus clientes a través de WhatsApp y correo electrónico. Un cliente envía un mensaje por WhatsApp preguntando si un producto específico de cuidado del cabello está disponible para su compra y si hay alguna oferta en curso. Un agente de inteligencia artificial, integrado con la base de datos de la empresa, responde a la consulta del cliente, verificando la disponibilidad del producto en el inventario. El agente AI informa al cliente que el producto está disponible y le proporciona detalles sobre las ofertas actuales, como un descuento del 20% por la compra de dos productos. El cliente decide realizar un pedido, y el agente AI ayuda con el proceso de pedido, solicitando la dirección de envío y los detalles de pago del cliente. Una vez que el pedido está completo, el agente AI envía el pedido a la base de datos de la empresa para su procesamiento, y el cliente recibe un mensaje de confirmación con los detalles del pedido e información de seguimiento.'}