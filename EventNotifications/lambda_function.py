import json
import requests
import os
from typing import Dict, Optional

class WhatsAppHandler:
    """
    A class to handle WhatsApp webhook messages and responses.
    """
    def __init__(self, api_url: str, access_token: str):
        """
        Initializes the WhatsAppHandler with API URL and access token.

        Parameters:
        api_url (str): The URL of the WhatsApp API endpoint.
        access_token (str): The access token for authenticating API requests.
        """
        self.api_url = api_url
        self.headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }

    def _get_message_content(self, message: Dict) -> str:
        """
        Extracts content based on the message type.

        Parameters:
        message (dict): The message object.

        Returns:
        str: A descriptive string based on the message type.
        """
        msg_type = message["type"]
        if msg_type == "text":
            return f"Text message: {message['text']['body']}"
        elif msg_type == "image":
            return f"Image message with ID: {message['image']['id']}"
        elif msg_type == "audio":
            return f"Audio message with ID: {message['audio']['id']}"
        return f"Unsupported message type: {msg_type}"

    def extract_message_info(self, body: Dict) -> Optional[Dict]:
        """
        Extracts message type and details from the webhook body.

        Parameters:
        body (dict): The JSON body received from the webhook.

        Returns:
        dict: A dictionary containing 'type', 'from', and 'details' of the message,
              or None if no message is found.
        """
        try:
            # Navigate to the message content in the webhook body
            message = body["entry"][0]["changes"][0]["value"]["messages"][0]
            return {
                "type": message["type"],  # Type of the message (e.g., text, image)
                "from": message["from"],  # Sender's phone number
                "details": self._get_message_content(message)  # Message content
            }
        except (IndexError, KeyError):
            # Return None if the JSON structure is invalid or no message is found
            return None

    def send_response(self, to: str, message: str) -> Dict:
        """
        Sends a text response back to the user.

        Parameters:
        to (str): The recipient's phone number.
        message (str): The message to send.

        Returns:
        dict: The JSON response from the WhatsApp API.
        """
        # Construct the payload for the API request
        payload = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": to,
            "type": "text",
            "text": {
                "preview_url": False,
                "body": message
            }
        }
        
        # Send the POST request to the WhatsApp API
        response = requests.post(self.api_url, headers=self.headers, json=payload)
        return response.json()

def lambda_handler(event, context):
    """
    AWS Lambda handler to process WhatsApp webhook events and send responses.

    Parameters:
    event (dict): The event data received by the AWS Lambda function.
    context (object): The runtime information of the Lambda function.

    Returns:
    dict: The HTTP response with a status code.
    """
    try:
        # Initialize WhatsAppHandler with environment variables
        handler = WhatsAppHandler(
            api_url=os.environ["WHATSAPP_API_URL"],
            access_token=os.environ["WHATSAPP_ACCESS_TOKEN"]
        )

        # Parse the JSON body from the event
        body = json.loads(event.get("body", "{}"))
        print("Incoming webhook body:", json.dumps(body))
        
        # Extract message information
        message_info = handler.extract_message_info(body)
        if not message_info:
            print("No user message found; ignoring event.")
            return {"statusCode": 200}  # Acknowledge non-message events
        
        # Send a response about the received message type
        response = handler.send_response(
            to=message_info["from"],
            message=f"Received your {message_info['type']} message! {message_info['details']}"
        )
        print("WhatsApp API Response:", response)
        return {"statusCode": 200}

    except Exception as e:
        # Handle exceptions and return a 500 error response
        return {
            "statusCode": 500,
            "body": json.dumps({"error": str(e)})
        }
