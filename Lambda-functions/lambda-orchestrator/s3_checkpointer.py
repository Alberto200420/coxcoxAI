from contextlib import contextmanager
from typing import Any, Iterator, List, Optional, Tuple, Union
import json
import base64
import boto3
from botocore.exceptions import ClientError
from langchain_core.runnables import RunnableConfig
from langgraph.checkpoint.base import (
  WRITES_IDX_MAP,
  BaseCheckpointSaver,
  ChannelVersions,
  Checkpoint,
  CheckpointMetadata,
  CheckpointTuple,
  PendingWrite,
  get_checkpoint_id,
)

S3_KEY_SEPARATOR = "/"

class BytesEncoder(json.JSONEncoder):
  """Custom JSON encoder that handles bytes objects."""
  def default(self, obj):
    if isinstance(obj, bytes):
      return {
        "__type__": "bytes",
        "data": base64.b64encode(obj).decode('utf-8')
      }
    return super().default(obj)

def bytes_decoder(obj):
  """Custom JSON decoder that handles bytes objects."""
  if "__type__" in obj and obj["__type__"] == "bytes":
    return base64.b64decode(obj["data"].encode('utf-8'))
  return obj

def _make_s3_checkpoint_key( thread_id: int, checkpoint_ns: str, checkpoint_id: str) -> str:
  return f"checkpoints{S3_KEY_SEPARATOR}{thread_id}{S3_KEY_SEPARATOR}{checkpoint_ns}{S3_KEY_SEPARATOR}{checkpoint_id}.json"

def _make_s3_writes_key( thread_id: int, checkpoint_ns: str, checkpoint_id: str, task_id: str, idx: Optional[int], ) -> str:
  if idx is None:
    return f"writes{S3_KEY_SEPARATOR}{thread_id}{S3_KEY_SEPARATOR}{checkpoint_ns}{S3_KEY_SEPARATOR}{checkpoint_id}{S3_KEY_SEPARATOR}{task_id}.json"
  return f"writes{S3_KEY_SEPARATOR}{thread_id}{S3_KEY_SEPARATOR}{checkpoint_ns}{S3_KEY_SEPARATOR}{checkpoint_id}{S3_KEY_SEPARATOR}{task_id}{S3_KEY_SEPARATOR}{idx}.json"

def _parse_s3_checkpoint_key(s3_key: str) -> dict:
  parts = s3_key.replace(".json", "").split(S3_KEY_SEPARATOR)
  return {
    "thread_id": parts[1],
    "checkpoint_ns": parts[2],
    "checkpoint_id": parts[3]
  }

class S3Saver(BaseCheckpointSaver):
  """S3-based checkpoint saver implementation."""

  def __init__(self, bucket_name: str, s3_client=None):
    super().__init__()
    self.bucket_name = bucket_name
    self.s3_client = s3_client or boto3.client('s3')

  @classmethod
  @contextmanager
  def from_bucket(cls, *, bucket_name: str, **kwargs) -> Iterator["S3Saver"]:
    """Create an S3Saver instance from bucket information."""
    s3_client = boto3.client('s3', **kwargs)
    try:
      yield cls(bucket_name=bucket_name, s3_client=s3_client)
    finally:
      s3_client.close()

  def put( self, config: RunnableConfig, checkpoint: Checkpoint, metadata: CheckpointMetadata, new_versions: ChannelVersions, ) -> RunnableConfig:
    """Save a checkpoint to S3."""
    thread_id = int(config["configurable"]["thread_id"])
    checkpoint_ns = config["configurable"].get("checkpoint_ns", "")
    checkpoint_id = checkpoint["id"]
    parent_checkpoint_id = config["configurable"].get("checkpoint_id")
        
    key = _make_s3_checkpoint_key(thread_id, checkpoint_ns, checkpoint_id)
        
    type_, serialized_checkpoint = self.serde.dumps_typed(checkpoint)
    serialized_metadata = self.serde.dumps(metadata)
        
    data = {
      "checkpoint": serialized_checkpoint,
      "type": type_,
      "metadata": serialized_metadata,
      "parent_checkpoint_id": parent_checkpoint_id if parent_checkpoint_id else "",
    }
        
    # Use custom JSON encoder for bytes objects
    json_str = json.dumps(data, cls=BytesEncoder)
        
    self.s3_client.put_object(
      Bucket=self.bucket_name,
      Key=key,
      Body=json_str
    )
        
    return {
      "configurable": {
        "thread_id": thread_id,
        "checkpoint_ns": checkpoint_ns,
        "checkpoint_id": checkpoint_id,
      }
    }

  def put_writes( self, config: RunnableConfig, writes: List[Tuple[str, Any]], task_id: str, ) -> None:
    """Store intermediate writes linked to a checkpoint."""
    thread_id = int(config["configurable"]["thread_id"])
    checkpoint_ns = config["configurable"].get("checkpoint_ns", "")
    checkpoint_id = config["configurable"]["checkpoint_id"]

    for idx, (channel, value) in enumerate(writes):
      key = _make_s3_writes_key(
        thread_id,
        checkpoint_ns,
        checkpoint_id,
        task_id,
        WRITES_IDX_MAP.get(channel, idx),
      )
            
      type_, serialized_value = self.serde.dumps_typed(value)
      data = {
        "channel": channel,
        "type": type_,
        "value": serialized_value
      }
            
      # Use custom JSON encoder for bytes objects
      json_str = json.dumps(data, cls=BytesEncoder)
            
      self.s3_client.put_object(
        Bucket=self.bucket_name,
        Key=key,
        Body=json_str
      )

  def get(self, config: Union[str, dict, RunnableConfig]) -> Optional[Any]:
    """Get a checkpoint using a string thread_id or config dict."""
    if isinstance(config, str):
      config = {"configurable": {"thread_id": config}}
    return super().get(config)

  def get_tuple(self, config: Union[str, dict, RunnableConfig]) -> Optional[CheckpointTuple]:
    """Get a checkpoint tuple from S3."""
    if isinstance(config, str):
      config = {"configurable": {"thread_id": config}}
        
    thread_id = str(config["configurable"]["thread_id"])
    checkpoint_id = get_checkpoint_id(config)
    checkpoint_ns = config["configurable"].get("checkpoint_ns", "")

    key = self._get_checkpoint_key(thread_id, checkpoint_ns, checkpoint_id)
    if not key:
      return None

    try:
      response = self.s3_client.get_object(Bucket=self.bucket_name, Key=key)
      checkpoint_data = json.loads(
        response['Body'].read().decode('utf-8'),
        object_hook=bytes_decoder
      )
            
      checkpoint_id = checkpoint_id or _parse_s3_checkpoint_key(key)["checkpoint_id"]
      pending_writes = self._load_pending_writes(thread_id, checkpoint_ns, checkpoint_id)
            
      return self._parse_checkpoint_data(key, checkpoint_data, pending_writes)
            
    except ClientError:
      return None

  def list( self, config: Optional[RunnableConfig], *, filter: Optional[dict[str, Any]] = None, before: Optional[RunnableConfig] = None, limit: Optional[int] = None, ) -> Iterator[CheckpointTuple]:
    """List checkpoints from S3."""
        
    # Check if config is a string and convert it into a dictionary
    if isinstance(config, str):
      config = {"configurable": {"thread_id": config}}
        
    thread_id = int(config["configurable"]["thread_id"])
    checkpoint_ns = config["configurable"].get("checkpoint_ns", "")
    prefix = f"checkpoints{S3_KEY_SEPARATOR}{thread_id}{S3_KEY_SEPARATOR}{checkpoint_ns}"
        
    paginator = self.s3_client.get_paginator('list_objects_v2')
    pages = paginator.paginate(Bucket=self.bucket_name, Prefix=prefix)
        
    checkpoint_keys = []
    for page in pages:
      if 'Contents' not in page:
        continue
      for obj in page['Contents']:
        key = obj['Key']
        if before:
          checkpoint_id = _parse_s3_checkpoint_key(key)["checkpoint_id"]
          if checkpoint_id >= before["configurable"]["checkpoint_id"]:
            continue
        checkpoint_keys.append(key)
        
    checkpoint_keys.sort(key=lambda k: _parse_s3_checkpoint_key(k)["checkpoint_id"], reverse=True)
    if limit:
      checkpoint_keys = checkpoint_keys[:limit]
        
    for key in checkpoint_keys:
      try:
        response = self.s3_client.get_object(Bucket=self.bucket_name, Key=key)
        # Use custom JSON decoder for bytes objects
        data = json.loads(
          response['Body'].read().decode('utf-8'),
          object_hook=bytes_decoder
        )
                
        checkpoint_id = _parse_s3_checkpoint_key(key)["checkpoint_id"]
        pending_writes = self._load_pending_writes(thread_id, checkpoint_ns, checkpoint_id)
                
        checkpoint_tuple = self._parse_checkpoint_data(key, data, pending_writes)
        if checkpoint_tuple:
          yield checkpoint_tuple
      except ClientError:
        continue

  def _load_pending_writes( self, thread_id: int, checkpoint_ns: str, checkpoint_id: str ) -> List[PendingWrite]:
    """Load pending writes for a checkpoint from S3."""
    prefix = f"writes{S3_KEY_SEPARATOR}{thread_id}{S3_KEY_SEPARATOR}{checkpoint_ns}{S3_KEY_SEPARATOR}{checkpoint_id}"
        
    pending_writes = []
    paginator = self.s3_client.get_paginator('list_objects_v2')
        
    try:
      for page in paginator.paginate(Bucket=self.bucket_name, Prefix=prefix):
        if 'Contents' not in page:
          continue
                    
        for obj in page['Contents']:
          response = self.s3_client.get_object(Bucket=self.bucket_name, Key=obj['Key'])
          # Use custom JSON decoder for bytes objects
          data = json.loads(
            response['Body'].read().decode('utf-8'),
            object_hook=bytes_decoder
          )
                    
          pending_writes.append((
            obj['Key'].split(S3_KEY_SEPARATOR)[-2],  # task_id
            data["channel"],
            self.serde.loads_typed((data["type"], data["value"]))
          ))
                    
      return sorted(pending_writes, key=lambda x: x[0])
    except ClientError:
      return []

  def _get_checkpoint_key( self, thread_id: int, checkpoint_ns: str, checkpoint_id: Optional[str] ) -> Optional[str]:
    """Get the S3 key for a checkpoint."""
    if checkpoint_id:
      return _make_s3_checkpoint_key(thread_id, checkpoint_ns, checkpoint_id)

    prefix = f"checkpoints{S3_KEY_SEPARATOR}{thread_id}{S3_KEY_SEPARATOR}{checkpoint_ns}"
        
    try:
      response = self.s3_client.list_objects_v2(
        Bucket=self.bucket_name,
        Prefix=prefix
      )
            
      if 'Contents' not in response:
        return None
                
      latest_key = max(
        response['Contents'],
        key=lambda x: _parse_s3_checkpoint_key(x['Key'])["checkpoint_id"]
      )['Key']
            
      return latest_key
    except ClientError:
      return None

  def _parse_checkpoint_data( self, key: str, data: dict, pending_writes: Optional[List[PendingWrite]] = None ) -> Optional[CheckpointTuple]:
    """Parse checkpoint data retrieved from S3."""
    if not data:
      return None

    parsed_key = _parse_s3_checkpoint_key(key)
    config = {
      "configurable": {
        "thread_id": parsed_key["thread_id"],
        "checkpoint_ns": parsed_key["checkpoint_ns"],
        "checkpoint_id": parsed_key["checkpoint_id"],
      }
    }

    checkpoint = self.serde.loads_typed((data["type"], data["checkpoint"]))
    metadata = self.serde.loads(data["metadata"])
    parent_checkpoint_id = data.get("parent_checkpoint_id", "")
        
    parent_config = (
      {
        "configurable": {
          "thread_id": parsed_key["thread_id"],
          "checkpoint_ns": parsed_key["checkpoint_ns"],
          "checkpoint_id": parent_checkpoint_id,
        }
      }
      if parent_checkpoint_id
      else None
    )
        
    return CheckpointTuple(
      config=config,
      checkpoint=checkpoint,
      metadata=metadata,
      parent_config=parent_config,
      pending_writes=pending_writes,
    )