"""
Agent Router - Shack Entertainment
Routes messages and tasks between agents
"""

import json
from typing import Dict, Any, Optional
from datetime import datetime

class AgentRouter:
    """Routes messages between agents based on agent IDs"""
    
    def __init__(self):
        self.message_queue = []
        self.agent_registry = {
            "0fjr9eavdp2o": "Chief of Staff",
            "ee30846e": "Creative Director",
            "16d35d97": "Shack News Editor",
            "m9cuyi4170nb": "Site Ops",
            "e95ce80f": "Shack Finance",
            "55294ff9": "Communications Hub",
            "vpys8rw63c09": "Content Studio",
            "2b0s3pogrh1k": "Research Analyst"
        }
    
    def route_message(self, from_agent: str, to_agent: str, message: Dict[str, Any]):
        """Route a message from one agent to another"""
        envelope = {
            "timestamp": datetime.now().isoformat(),
            "from": from_agent,
            "from_name": self.agent_registry.get(from_agent, "Unknown"),
            "to": to_agent,
            "to_name": self.agent_registry.get(to_agent, "Unknown"),
            "message": message,
            "status": "pending"
        }
        
        self.message_queue.append(envelope)
        print(f"→ Message routed: {envelope['from_name']} → {envelope['to_name']}")
        return envelope
    
    def get_pending_messages(self, agent_id: str):
        """Get all pending messages for an agent"""
        return [
            msg for msg in self.message_queue 
            if msg["to"] == agent_id and msg["status"] == "pending"
        ]
    
    def mark_read(self, agent_id: str, message_index: int):
        """Mark a message as read"""
        if 0 <= message_index < len(self.message_queue):
            self.message_queue[message_index]["status"] = "read"


if __name__ == "__main__":
    router = AgentRouter()
    
    # Test routing
    router.route_message(
        "0fjr9eavdp2o",
        "ee30846e",
        {"action": "create_bio", "artist": "Paul Duncan"}
    )
    
    print(f"\nPending messages for Creative Director:")
    for msg in router.get_pending_messages("ee30846e"):
        print(f"  - {msg['message']}")