from spade.behaviour import PeriodicBehaviour
from models.enums import Priority
from datetime import datetime, timedelta


class PriorityManagementBehaviour(PeriodicBehaviour):
    
    async def run(self):
        current_time = datetime.now()
        
        # Check pending requests
        for request in self.agent.pending_requests:
            request_time = request['timestamp']
            waiting_time = (current_time - request_time).total_seconds() / 60  # minutes
            
            # Escalate priority for long-waiting tasks
            if waiting_time > 30 and request['priority'] != Priority.URGENT:
                if request['priority'] == Priority.LOW:
                    request['priority'] = Priority.NORMAL
                    self.agent.logger.info(f"Escalated task priority: LOW -> NORMAL")
                elif request['priority'] == Priority.NORMAL:
                    request['priority'] = Priority.HIGH
                    self.agent.logger.info(f"Escalated task priority: NORMAL -> HIGH")
                elif request['priority'] == Priority.HIGH:
                    request['priority'] = Priority.URGENT
                    self.agent.logger.info(f"Escalated task priority: HIGH -> URGENT")
        
        # Check active tasks for timeouts
        for task_id, task in list(self.agent.active_tasks.items()):
            if task.is_overdue(timeout_seconds=300):  # 5 minutes
                self.agent.logger.warning(f"Task {task_id} is overdue")
                
                # Try to reassign if possible
                if task.can_retry():
                    self.agent.logger.info(f"Attempting to reassign task {task_id}")
                    task.status = 'failed'
                    self.agent.failed_tasks.append(task)
                    del self.agent.active_tasks[task_id]
                    
                    # Add back to pending with higher priority
                    request = {
                        'type': task.task_type.value,
                        'data': task.parameters,
                        'priority': Priority.URGENT,
                        'timestamp': datetime.now(),
                        'attempts': task.attempts
                    }
                    self.agent.pending_requests.append(request)
