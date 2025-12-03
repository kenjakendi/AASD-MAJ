import json
from spade.behaviour import CyclicBehaviour
from models.task import Task


class ReceiveTaskBehaviour(CyclicBehaviour):
    
    async def run(self):
        msg = await self.receive(timeout=10)
        if msg:
            try:
                content = json.loads(msg.body)
                protocol = msg.get_metadata("protocol")
                
                self.agent.logger.info(f"Received task assignment: {protocol}")
                
                # Create task from assignment
                task = Task.from_dict(content)
                
                # Add task to worker's queue
                if self.agent.add_task(task):
                    self.agent.logger.info(f"Added task {task.task_id} to queue")
                else:
                    self.agent.logger.error(f"Failed to add task {task.task_id} to queue")

            except Exception as e:
                self.agent.logger.error(f"Error processing task assignment: {e}")
