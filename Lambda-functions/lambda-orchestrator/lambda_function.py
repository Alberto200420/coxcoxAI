from orchestrator import graph, HumanMessage
import json, os, requests
import unicodedata

def normalize_text(text) -> str:
  return unicodedata.normalize('NFKD', text).encode('ascii', 'ignore').decode('ascii')

def lambda_handler(event, context):
  api_url = os.environ["WHATSAPP_API_URL"]
  access_token = os.environ["WHATSAPP_ACCESS_TOKEN"]
  headers = {
    "Authorization": f"Bearer {access_token}",
    "Content-Type": "application/json"
  }

  for record in event['Records']:
    try:
      # Parse the message body
      message_body = json.loads(record['body'])
            
      # Extract values
      sender: str = message_body['from']
      text: str = message_body['text']
      print(f"From: {sender}\nText: {text}\n\nMessage ID: {record['messageId']}")

      # Invoke the graph
      result = graph.invoke({"messages": [HumanMessage(content=text)]}, {"configurable": {"thread_id": sender}})
      graph_response = normalize_text(result['messages'][-1].content)
      print(f"Graph Result: {graph_response}")

      payload = {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": sender,
        "type": "text",
        "text": {
          "preview_url": False,
          "body": graph_response
        }
      }
      response = requests.post(api_url, headers=headers, json=payload)
            
      print(f"WhatsApp API Status Code: {response.status_code}")
      # Raise an exception for bad status codes
      response.raise_for_status()

    except requests.exceptions.RequestException as e:
      print(f"Request Error: {str(e)}")
      if hasattr(e.response, 'text'):
        print(f"Error Response: {e.response.text}")
    except json.JSONDecodeError as e:
      print(f"JSON Parsing Error: {str(e)}")
    except Exception as e:
      print(f"Unexpected Error: {str(e)}")
      import traceback
      print("Traceback:", traceback.format_exc())
      continue

  return {"statusCode": 200}