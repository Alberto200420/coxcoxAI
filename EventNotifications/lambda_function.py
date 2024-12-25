import json
import requests
import os

# Function to extract message details from the incoming webhook body
def extract_message_details(body):
    """
    Extracts the sender's phone number and message text from the webhook body.

    Parameters:
    body (dict): The JSON body received from the webhook.

    Returns:
    dict: A dictionary containing 'from' (sender's number) and 'body' (message text),
          or None if the details are not found.
    """
    try:
        # Navigate through the JSON structure to find message details
        change = body.get("entry", [])[0].get("changes", [])[0]
        value = change.get("value", {})
        messages = value.get("messages", [])
        if messages:
            return {
                "from": messages[0]["from"],  # Sender's phone number
                "body": messages[0]["text"]["body"]  # Message text
            }
        return None
    except (IndexError, AttributeError, KeyError):
        # Return None if any part of the JSON structure is missing or malformed
        return None

# Main handler function for the Lambda
def lambda_handler(event, context):
    """
    Handles incoming webhooks and sends a template message response via WhatsApp.

    Parameters:
    event (dict): The event data received by the AWS Lambda function.
    context (object): The runtime information of the Lambda function.

    Returns:
    dict: The HTTP response with a status code.
    """
    # Fetch WhatsApp API URL and Access Token from environment variables
    WHATSAPP_API_URL = os.getenv("WHATSAPP_API_URL")
    ACCESS_TOKEN = os.getenv("WHATSAPP_ACCESS_TOKEN")

    try:
        # Parse the JSON body from the event
        body = json.loads(event.get("body", "{}"))
        print("Incoming webhook body:", json.dumps(body))

        # Extract message details from the webhook body
        message_details = extract_message_details(body)
        if not message_details:
            print("No user message found; ignoring event.")
            return {"statusCode": 200}

        # Extract the sender's phone number
        number_to = message_details["from"]
        print("number_to:", number_to)

        # Prepare the payload for the WhatsApp API
        whatsapp_payload = {
            "messaging_product": "whatsapp",
            "to": number_to,
            "type": "template",
            "template": {
                "name": "hello_world",  # Template name
                "language": {"code": "en_US"}  # Language code
            }
        }

        # Prepare the headers for the WhatsApp API request
        headers = {
            "Authorization": f"Bearer {ACCESS_TOKEN}",
            "Content-Type": "application/json"
        }

        # Send the POST request to the WhatsApp API
        response = requests.post(WHATSAPP_API_URL, headers=headers, json=whatsapp_payload)
        print("WhatsApp API Response:", response.status_code, response.text)

        # Return a 200 status code indicating success
        return {"statusCode": 200}

    except Exception as e:
        # Handle exceptions and log the error
        print("Error handling webhook:", str(e))
        return {
            "statusCode": 500,
            "body": json.dumps({"error": "Internal server error"})
        }