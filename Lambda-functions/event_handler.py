import json
import boto3
import os
from datetime import datetime, timezone, timedelta
from typing import Dict, Optional, Any
from io import BytesIO

class WhatsAppS3Handler:
    def __init__(self, bucket_name: str, timezone_offset: int = -6):
        self.s3 = boto3.client('s3')
        self.bucket_name = bucket_name
        self.timezone_offset = timezone_offset

    def _convert_timestamp(self, timestamp: int) -> str:
        """Convert Unix timestamp to formatted datetime string with timezone offset."""
        try:
            utc_time = datetime.fromtimestamp(timestamp, timezone.utc)
            local_time = utc_time + timedelta(hours=self.timezone_offset)
            return local_time.strftime("%Y-%m-%d %H:%M:%S")
        except (ValueError, TypeError) as e:
            raise ValueError(f"Invalid timestamp format: {e}")

    def _extract_message_data(self, payload: Dict) -> Optional[Dict[str, Any]]:
        """Safely extract message data from webhook payload."""
        try:
            message = payload["entry"][0]["changes"][0]["value"]["messages"][0]
            
            if message["type"] != "text":
                return None
                
            return {
                "from": message["from"],
                "timestamp": int(message["timestamp"]),
                "text": message["text"]["body"]
            }
        except (KeyError, IndexError, TypeError) as e:
            raise KeyError(f"Failed to extract message data: {e}")

    def _prepare_message_object(self, message_data: Dict) -> Dict:
        """Prepare message object for storage."""
        return {
            "messages": [{
                "from": message_data["from"],
                "timestamp": self._convert_timestamp(message_data["timestamp"]),
                "text": {"body": message_data["text"]}
            }]
        }

    def save_message(self, message_data: Dict) -> None:
        """Save message to S3 using upload_fileobj."""
        message_object = self._prepare_message_object(message_data)
        
        # Convert dictionary to JSON bytes
        json_data = json.dumps(message_object).encode('utf-8')
        file_obj = BytesIO(json_data)
        
        # Generate S3 key
        s3_key = f"messages/{message_data['from']}/message.json"
        
        # Upload to S3
        try:
            self.s3.upload_fileobj(
                file_obj,
                self.bucket_name,
                s3_key,
                ExtraArgs={'ContentType': 'application/json'}
            )
        except Exception as e:
            raise IOError(f"Failed to upload to S3: {e}")

def create_response(status_code: int, message: str = "") -> Dict:
    """Create standardized API response."""
    response = {"statusCode": status_code}
    if message:
        response["body"] = json.dumps({"message": message})
    return response

def lambda_handler(event, context):
    # Initialize handler with environment variables    
    try:
        handler = WhatsAppS3Handler(
            bucket_name=os.environ["BUCKET_NAME"],
            timezone_offset=-6
        )
        # Parse webhook payload
        if not event.get("body"):
            return create_response(200, "No body in request")
            
        body = json.loads(event["body"])
        
        # Extract message data
        try:
            message_data = handler._extract_message_data(body)
        except KeyError as e:
            print(f"Error extracting message data: {e}")
            return create_response(200, "Invalid message format")
            
        # Process only text messages
        if not message_data:
            return create_response(200, "Non-text message received")
            
        # Save message to S3
        try:
            handler.save_message(message_data)
        except IOError as e:
            print(f"Error saving to S3: {e}")
            return create_response(500, f"Failed to save message: {e}")
            
        return create_response(200, "Message processed successfully")
        
    except json.JSONDecodeError as e:
        print(f"Invalid JSON in webhook payload: {e}")
        return create_response(400, f"Invalid JSON payload: {e}")
        
    except Exception as e:
        print(f"Unexpected error: {e}")
        return create_response(500, f"Internal server error: {e}")
