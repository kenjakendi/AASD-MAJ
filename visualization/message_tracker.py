import asyncio
import json
from datetime import datetime
from typing import Dict, List, Any, Optional
from collections import defaultdict, deque
import threading


class MessageTracker:
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
            
        self.messages: deque = deque(maxlen=1000)  # Keep last 1000 messages
        self.agents: Dict[str, Dict[str, Any]] = {}
        self.message_count: int = 0
        self.start_time: datetime = datetime.now()
        
        # Statistics
        self.stats = {
            'total_messages': 0,
            'messages_by_type': defaultdict(int),
            'messages_by_agent': defaultdict(int),
            'active_agents': set(),
        }
        
        # Subscribers for real-time updates
        self.subscribers: List[callable] = []
        
        self._initialized = True
    
    def register_agent(self, jid: str, role: str, metadata: Optional[Dict] = None):
        with self._lock:
            agent_name = jid.split('@')[0]
            self.agents[agent_name] = {
                'jid': jid,
                'role': role,
                'metadata': metadata or {},
                'registered_at': datetime.now().isoformat(),
                'status': 'online',
                'message_count': 0,
                'last_seen': datetime.now().isoformat()
            }
            self.stats['active_agents'].add(agent_name)
    
    def track_message(self, from_jid: str, to_jid: str, content: Dict[str, Any], 
                     metadata: Optional[Dict] = None):
        with self._lock:
            self.message_count += 1
            
            # Extract agent names
            from_agent = from_jid.split('@')[0]
            to_agent = to_jid.split('@')[0]
            
            # Create message record
            message_record = {
                'id': self.message_count,
                'timestamp': datetime.now().isoformat(),
                'from': from_agent,
                'to': to_agent,
                'from_jid': from_jid,
                'to_jid': to_jid,
                'content': content,
                'metadata': metadata or {},
                'performative': metadata.get('performative', 'inform') if metadata else 'inform',
                'protocol': metadata.get('protocol', 'unknown') if metadata else 'unknown'
            }
            
            # Store message
            self.messages.append(message_record)
            
            # Update statistics
            self.stats['total_messages'] += 1
            self.stats['messages_by_agent'][from_agent] += 1
            performative = message_record['performative']
            self.stats['messages_by_type'][performative] += 1
            
            # Update agent info
            for agent_name in [from_agent, to_agent]:
                if agent_name in self.agents:
                    self.agents[agent_name]['last_seen'] = datetime.now().isoformat()
                    if agent_name == from_agent:
                        self.agents[agent_name]['message_count'] += 1
            
            # Notify subscribers
            self._notify_subscribers(message_record)
            
            return message_record
    
    def subscribe(self, callback: callable):
        if callback not in self.subscribers:
            self.subscribers.append(callback)
    
    def unsubscribe(self, callback: callable):
        if callback in self.subscribers:
            self.subscribers.remove(callback)
    
    def _notify_subscribers(self, message: Dict[str, Any]):
        for callback in self.subscribers:
            try:
                callback(message)
            except Exception as e:
                print(f"Error notifying subscriber: {e}")
    
    def get_recent_messages(self, limit: int = 50) -> List[Dict[str, Any]]:
        with self._lock:
            messages = list(self.messages)
            return messages[-limit:]
    
    def get_agents(self) -> Dict[str, Dict[str, Any]]:
        with self._lock:
            return dict(self.agents)
    
    def get_statistics(self) -> Dict[str, Any]:
        with self._lock:
            uptime = (datetime.now() - self.start_time).total_seconds()
            return {
                'total_messages': self.stats['total_messages'],
                'active_agents': len(self.stats['active_agents']),
                'messages_by_type': dict(self.stats['messages_by_type']),
                'messages_by_agent': dict(self.stats['messages_by_agent']),
                'uptime_seconds': uptime,
                'messages_per_second': self.stats['total_messages'] / uptime if uptime > 0 else 0
            }
    
    def get_agent_connections(self) -> List[Dict[str, Any]]:
        with self._lock:
            connections = defaultdict(lambda: {'count': 0, 'protocols': set()})
            
            for msg in self.messages:
                key = f"{msg['from']}->{msg['to']}"
                connections[key]['count'] += 1
                connections[key]['protocols'].add(msg['protocol'])
            
            result = []
            for key, data in connections.items():
                from_agent, to_agent = key.split('->')
                result.append({
                    'from': from_agent,
                    'to': to_agent,
                    'count': data['count'],
                    'protocols': list(data['protocols'])
                })
            
            return result
    
    def clear_data(self):
        with self._lock:
            self.messages.clear()
            self.message_count = 0
            self.stats = {
                'total_messages': 0,
                'messages_by_type': defaultdict(int),
                'messages_by_agent': defaultdict(int),
                'active_agents': set(),
            }


# Global tracker instance
tracker = MessageTracker()
