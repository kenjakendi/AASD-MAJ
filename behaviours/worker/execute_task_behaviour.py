from spade.behaviour import PeriodicBehaviour
from models.task import TaskStatus
from config.settings import Settings


class ExecuteTaskBehaviour(PeriodicBehaviour):
    
    async def run(self):
        # Pull tasks from queue to current_tasks if we have capacity
        while (len(self.agent.current_tasks) < self.agent.max_concurrent_tasks and
               len(self.agent.task_queue) > 0):
            task = self.agent.task_queue.pop(0)  # Get first task from queue (FIFO)
            self.agent.current_tasks.append(task)
            self.agent.logger.info(f"Pulled task {task.task_id} from queue to execute (queue: {len(self.agent.task_queue)}, executing: {len(self.agent.current_tasks)})")

        # Update availability based on current load
        self.agent.is_available = len(self.agent.current_tasks) < self.agent.max_concurrent_tasks

        if not self.agent.current_tasks:
            return

        for task in list(self.agent.current_tasks):
            try:
                # Mark as in progress
                task.start()
                
                self.agent.logger.info(f"Executing task {task.task_id}")
                
                # Execute task (delegated to agent-specific implementation)
                result = await self.agent.execute_task(task)
                
                if result.get('success'):
                    # Mark as complete
                    task.complete(result)
                    self.agent.logger.info(f"Task {task.task_id} completed successfully")
                    
                    # Send confirmation to coordinator
                    await self._send_confirmation(task, result)
                    
                    # Remove from current tasks
                    self.agent.complete_task(task.task_id)
                else:
                    # Handle failure
                    task.fail(result.get('error', 'Unknown error'))
                    self.agent.logger.error(f"Task {task.task_id} failed: {result.get('error')}")
                    self.agent.tasks_failed += 1
                    self.agent.current_tasks.remove(task)
                    
            except Exception as e:
                self.agent.logger.error(f"Error executing task {task.task_id}: {e}")
                task.fail(str(e))
                self.agent.tasks_failed += 1
                if task in self.agent.current_tasks:
                    self.agent.current_tasks.remove(task)
    
    async def _send_confirmation(self, task, result):
        coordinator_jid = f"coordinator@{Settings.XMPP_SERVER}"
        
        protocol_map = {
            'feed': 'ConfirmFeedTask',
            'walk': 'ConfirmWalkTask',
            'clean': 'ConfirmCleanTask',
            'health_check': 'ConfirmHealthRequestTask',
            'vaccination': 'ConfirmVaccinationTask',
            'initial_checkup': 'ConfirmInitialCheckupTask'
        }
        
        protocol = protocol_map.get(task.task_type.value, 'ConfirmTask')
        
        content = {
            'taskId': task.task_id,
            'workerId': self.agent.worker_id,
            **result
        }
        
        await self.agent.send_confirm(to=coordinator_jid, protocol=protocol, content=content)
