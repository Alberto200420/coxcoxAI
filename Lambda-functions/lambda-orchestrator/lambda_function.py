from orchestrator import graph, HumanMessage
import unicodedata
import json
import re

def normalize_text(text) -> str:
  # Remove markdown formatting
  text = re.sub(r'\*{1,2}', '', text)
  # Normalize unicode characters
  text = unicodedata.normalize('NFKD', text)
  # Remove non-printable characters
  text = re.sub(r'[^\x20-\x7E\n]', '', text)
  # Replace multiple newlines with a single newline
  text = re.sub(r'\n{2,}', '\n', text)
  # Remove extra whitespace
  text = re.sub(r'\s+', ' ', text).strip()
  return text

def lambda_handler(event, context):
  # Check the Referer header to ensure the request is from the allowed domain
  referer = event.get('headers', {}).get('referer', '')
  if referer != 'https://coxcoxai.com/':
    return {
      'statusCode': 403,
      'body': json.dumps({'error': 'Forbidden: Invalid Referer'})
    }
  try:
    # Parse the message body
    request_body = json.loads(event['body'])
    text: str = request_body['text']
    thread_id: str = request_body['thread_id']
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