import json
import boto3
import os
from datetime import datetime, timezone, timedelta
from typing import Dict, Optional, Any

class WhatsAppSQSHandler:
    def __init__(self, queue_url: str, timezone_offset: int = -6):
        """
        Initializes the WhatsAppSQSHandler.
        :param queue_url: The URL of the AWS SQS queue.
        :param timezone_offset: The offset from UTC to the desired timezone (default is -6 for CST).
        """
        self.sqs = boto3.client('sqs')  # Initialize the SQS client
        self.queue_url = queue_url  # Store the queue URL
        self.timezone_offset = timezone_offset  # Store the timezone offset

    def _convert_timestamp(self, timestamp: int) -> str:
        """
        Convert a Unix timestamp to a formatted datetime string with timezone offset.
        :param timestamp: Unix timestamp (in seconds).
        :return: A formatted datetime string in the local timezone.
        """
        try:
            utc_time = datetime.fromtimestamp(timestamp, timezone.utc)  # Convert to UTC time
            local_time = utc_time + timedelta(hours=self.timezone_offset)  # Apply timezone offset
            return local_time.strftime("%Y-%m-%d %H:%M:%S")  # Return formatted string
        except (ValueError, TypeError) as e:
            raise ValueError(f"Invalid timestamp format: {e}")

    def _extract_message_data(self, payload: Dict) -> Optional[Dict[str, Any]]:
        """
        Safely extract message data from the webhook payload.
        :param payload: The JSON payload received from the webhook.
        :return: A dictionary with the message details or None if the message is invalid.
        """
        try:
            # Navigate through nested structure to extract the first message
            message = payload["entry"][0]["changes"][0]["value"]["messages"][0]
            return {
                "from": message["from"],  # Sender's phone number
                "timestamp": self._convert_timestamp(int(message["timestamp"])),  # Convert timestamp
                "text": message["text"]["body"]  # Extract message text
            }
        except (IndexError, KeyError, ValueError) as e:
            print(f"Error extracting message data: {e}")
            return None

    def send_to_queue(self, message_data: Dict) -> None:
        """
        Send the processed message data to the SQS queue.
        :param message_data: The dictionary containing the processed message.
        """
        try:
            # Send the message to SQS as a JSON-encoded string
            self.sqs.send_message(
                QueueUrl=self.queue_url,
                MessageBody=json.dumps(message_data)
            )
        except Exception as e:
            raise IOError(f"Failed to send message to SQS: {e}")

def lambda_handler(event, context):
    """
    AWS Lambda handler function.
    Processes incoming webhook events and sends valid WhatsApp messages to SQS.
    :param event: The event payload from the webhook.
    :param context: The Lambda execution context (not used in this function).
    :return: An API Gateway-compatible response.
    """
    try:
        # Initialize the WhatsAppSQSHandler with the queue URL from environment variables
        handler = WhatsAppSQSHandler(
            queue_url=os.environ["QUEUE_URL"],
            timezone_offset=-6  # Default to CST
        )

        # Parse the incoming request body
        body = json.loads(event["body"])
        print(f"body: {body}")

        # Extract message data from the parsed payload
        message_data = handler._extract_message_data(body)
        print(f"message_data: {message_data}")

        # Skip processing if no valid message data is found
        if not message_data:
            return {"statusCode": 200}

        # Send the extracted message data to SQS
        try:
            handler.send_to_queue(message_data)
        except IOError as e:
            print(f"Error sending message to SQS: {e}")
            return {"statusCode": 200}

        return {"statusCode": 200}

    except json.JSONDecodeError as e:
        # Handle cases where the incoming payload is not valid JSON
        print(f"Invalid JSON in webhook payload: {e}")
        return {"statusCode": 200}

    except Exception as e:
        # Catch any other unexpected exceptions
        print(f"Unexpected error: {e}")
        return {"statusCode": 200}
