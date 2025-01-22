from orchestrator import graph, HumanMessage
import json
import unicodedata

def normalize_text(text) -> str:
  return unicodedata.normalize('NFKD', text).encode('ascii', 'ignore').decode('ascii')

def lambda_handler(event, context):
  try:
    # Parse the message body
    request_body = json.loads(event['body'])
    text = request_body['text']
    thread_id = request_body['thread_id']
    # Invoke the graph
    result = graph.invoke({"messages": [HumanMessage(content=text)]}, {"configurable": {"thread_id": thread_id}})
    graph_response = normalize_text(result['messages'][-1].content)
    print(f"Graph Result: {graph_response}")
    return {
      'statusCode': 200,
      'body': json.dumps(graph_response)
    }
  except Exception as e:
    return {
      'statusCode': 500,
      'body': json.dumps({
        'error': f'Internal server error: {str(e)}'
      })
    }