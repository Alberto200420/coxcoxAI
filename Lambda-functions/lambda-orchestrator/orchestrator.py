from prompt_templates import DECISION_AGENT_TEMPLATE, ANSWERING_Q_AGENT_TEMPLATE, EXAMPLES_G_AGENT_TEMPLATE, CALL_TO_ACTION_AGENT_TEMPLATE
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from langgraph.graph import StateGraph, START, END, MessagesState
from langchain_core.prompts import SystemMessagePromptTemplate
from langchain_aws import ChatBedrockConverse
from s3_checkpointer import S3Saver
import os

llm_decision = ChatBedrockConverse(model="amazon.nova-micro-v1:0", temperature=0, top_p=0, max_tokens=20)
llm_answering_questions = ChatBedrockConverse(model="amazon.nova-lite-v1:0", temperature=0.7, top_p=0.9, max_tokens=512)
llm_example_generator = ChatBedrockConverse(model="amazon.nova-micro-v1:0", temperature=0.7, top_p=0.9, max_tokens=512)
llm_call_to_action = ChatBedrockConverse(model="amazon.nova-micro-v1:0", temperature=0.7, top_p=0.9, max_tokens=512)

class AgentState(MessagesState):
  """State for the multi-stage agent workflow"""
  decision: str

def decision_agent(state: AgentState):
  # Function to format the messages
  def format_messages(messages):
    formatted = "Analyze the following chat memory to find its appropriate category:\n"
    for message in messages:
      if isinstance(message, HumanMessage):
        formatted += f"USER:\n{message.content}\n"
      elif isinstance(message, AIMessage):
        formatted += f"AI Message:\n{message.content}\n"
    return formatted

  if len(state["messages"]) > 2:
    formatted_context = format_messages(state["messages"])
    system_prompt_template = SystemMessagePromptTemplate.from_template(DECISION_AGENT_TEMPLATE)
    system_message = system_prompt_template.format(context=formatted_context)
    print(f"Formatted system_message:\n{formatted_context}\n")
    response = llm_decision.invoke([system_message] + state["messages"][-1:])
  else:
    response = llm_decision.invoke([SystemMessage(content=DECISION_AGENT_TEMPLATE)] + state["messages"])
  print(f"Decision agent response:\n{response.content}\n")
  return {"decision": response.content}

def answering_questions(state: AgentState):
  return {"messages": llm_answering_questions.invoke([SystemMessage(content=ANSWERING_Q_AGENT_TEMPLATE)] + state["messages"])}

def example_generator(state: AgentState):
  return {"messages": llm_example_generator.invoke([SystemMessage(content=EXAMPLES_G_AGENT_TEMPLATE)] + state["messages"])}

def call_to_action(state: AgentState):
  # Maybe do something like save the values on the state
  return {"messages": llm_call_to_action.invoke([SystemMessage(content=CALL_TO_ACTION_AGENT_TEMPLATE)] + state["messages"])}

def malicious_query(state: AgentState):
  # Maybe do something like alert to a person
  pass

# Build the state graph
builder = StateGraph(AgentState)
builder.add_node("decision_agent", decision_agent)
builder.add_node("answering_questions", answering_questions)
builder.add_node("example_generator", example_generator)
builder.add_node("call_to_action", call_to_action)
builder.add_node("malicious_query", malicious_query)

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
    return "malicious_query"
  else:
    print(f"Unrecognized decision: {decision}")  # Debugging line
    return END  # Default case to avoid returning None

builder.add_conditional_edges("decision_agent", route_decision, ["answering_questions", "example_generator", "call_to_action", "malicious_query"])

builder.add_edge("answering_questions", END)
builder.add_edge("example_generator", END)
builder.add_edge("call_to_action", END)
builder.add_edge("malicious_query", END)

# Compile the graph with memory and start conversation
with S3Saver.from_bucket(bucket_name=os.getenv('AWS_S3_BUCKET_NAME'), region_name=os.getenv('AWS_DEFAULT_REGION')) as checkpointer:
  graph = builder.compile(checkpointer=checkpointer)