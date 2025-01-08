import json
import os

def lambda_handler(event, context):
  # Define the token you set in the App Dashboard
  VERIFY_TOKEN = os.environ["VERIFY_TOKEN"]
    
  # Extract query parameters from the event object
  query_params = event.get('queryStringParameters', {})
    
  # Retrieve values from query parameters
  hub_mode = query_params.get('hub.mode')
  hub_verify_token = query_params.get('hub.verify_token')
  hub_challenge = query_params.get('hub.challenge')
    
  # Validate the token and respond with the challenge
  if hub_mode == "subscribe" and hub_verify_token == VERIFY_TOKEN:
    return {
      "statusCode": 200,
      "body": hub_challenge
    }
  else:
    # Respond with 400 Bad Request if verification fails
    return {
      "statusCode": 400,
      "body": json.dumps({"error": "Invalid token"})
    }