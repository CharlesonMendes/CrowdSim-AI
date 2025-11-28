import logging
import json
import time
import uuid
import os

class StructuredLogger:
    def __init__(self, name="CrowdSimAI"):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.INFO)
        
        # Create logs directory if it doesn't exist
        if not os.path.exists("logs"):
            os.makedirs("logs")
            
        # File handler for JSON logs
        handler = logging.FileHandler("logs/simulation.jsonl")
        formatter = logging.Formatter('%(message)s')
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
        
        self.trace_id = str(uuid.uuid4())

    def log(self, event_type, details):
        """Logs an event with a trace ID and timestamp."""
        entry = {
            "timestamp": time.time(),
            "trace_id": self.trace_id,
            "event_type": event_type,
            "details": details
        }
        self.logger.info(json.dumps(entry))
        # Also print to console for immediate feedback (optional)
        # print(f"[{event_type}] {json.dumps(details)}")

class Metrics:
    def __init__(self):
        self.metrics = []

    def record(self, name, value, tags=None):
        self.metrics.append({
            "name": name,
            "value": value,
            "tags": tags or {},
            "timestamp": time.time()
        })

    def get_summary(self):
        # Simple summary: average of values per metric name
        summary = {}
        for m in self.metrics:
            name = m["name"]
            if name not in summary:
                summary[name] = []
            summary[name].append(m["value"])
        
        return {k: sum(v)/len(v) for k, v in summary.items()}
