from spade.behaviour import PeriodicBehaviour
from models.task import Task, TaskType, TaskStatus
from models.enums import Priority
from datetime import datetime


class AssignTasksBehaviour(PeriodicBehaviour):
    
    async def run(self):
        if not self.agent.pending_requests:
            return
        
        self.agent.logger.debug(f"Processing {len(self.agent.pending_requests)} pending requests")
        
        # Sort requests by priority
        self.agent.pending_requests.sort(key=lambda r: r['priority'].value)
        
        # Process requests
        requests_to_remove = []
        
        for request in self.agent.pending_requests:
            request_type = request['type']
            request_data = request['data']
            
            try:
                # Special handling for non-worker tasks
                if request_type == 'adoption':
                    # Forward directly to AdoptionAgent
                    await self._forward_to_adoption_agent(request_data)
                    requests_to_remove.append(request)
                    self.agent.logger.info(f"Forwarded adoption application to AdoptionAgent")
                    continue
                
                # Create appropriate task for workers
                task = self._create_task_from_request(request_type, request_data, request['priority'])
                
                if task:
                    # Find available worker
                    available_workers = self.agent.get_available_workers(task.task_type)
                    self.agent.logger.info(f"Available workers for task {task.task_id}: {available_workers}")
                    if available_workers:
                        # Select worker
                        selected_worker = self.agent.select_worker(task.task_type, available_workers)
                        
                        if selected_worker:
                            # Assign task
                            task.assign(selected_worker)
                            self.agent.active_tasks[task.task_id] = task

                            # Send assignment to worker
                            await self._send_task_assignment(task, selected_worker)

                            # Update worker state - only track assignment history
                            # Worker will report their own load and availability
                            self.agent.last_assigned_worker[task.task_type] = selected_worker

                            # Mark for removal
                            requests_to_remove.append(request)

                            self.agent.stats['total_tasks_assigned'] += 1
                            self.agent.logger.info(f"Assigned task {task.task_id} to {selected_worker}")
                    else:
                        self.agent.logger.debug(f"No available workers for {task.task_type.value}")
                        
            except Exception as e:
                self.agent.logger.error(f"Error assigning task: {e}")
        
        # Remove assigned requests
        for request in requests_to_remove:
            self.agent.pending_requests.remove(request)
    
    def _create_task_from_request(self, request_type: str, request_data: dict, priority: Priority) -> Task:
        task_id = self.agent.generate_task_id()
        
        task_type_map = {
            'feed': TaskType.FEED,
            'walk': TaskType.WALK,
            'clean': TaskType.CLEAN,
            'health': TaskType.HEALTH_CHECK,
            'vaccination': TaskType.VACCINATION,
            'registration': TaskType.INITIAL_CHECKUP
            # Note: 'adoption' is handled separately, not as a worker task
        }
        
        task_type = task_type_map.get(request_type)
        self.agent.logger.info(f"Created task {task_id} of type {task_type}")

        if not task_type:
            return None
        
        return Task(
            task_id=task_id,
            task_type=task_type,
            priority=priority,
            parameters=request_data,
            status=TaskStatus.PENDING
        )
    
    async def _forward_to_adoption_agent(self, application_data: dict):
        from config.settings import Settings
        adoption_jid = Settings.get_adoption_jid()
        
        await self.agent.send_request(
            to=adoption_jid,
            protocol='AdoptionApplicationTask',
            content=application_data
        )
    
    async def _send_task_assignment(self, task: Task, worker_id: str):
        protocol_map = {
            TaskType.FEED: 'AssignFeedTask',
            TaskType.WALK: 'AssignWalkTask',
            TaskType.CLEAN: 'AssignCleanTask',
            TaskType.HEALTH_CHECK: 'HealthRequestTask',
            TaskType.VACCINATION: 'AssignVaccinationTask',
            TaskType.INITIAL_CHECKUP: 'AssignInitialCheckupTask'
            # Note: ADOPTION_APPLICATION is not sent to workers
        }

        protocol = protocol_map.get(task.task_type)

        # Use the stored worker JID from availability updates
        worker_jid = self.agent.worker_jids.get(worker_id)
        if not worker_jid:
            # Fallback to constructing JID (shouldn't happen if worker sent availability update)
            worker_jid = f"{worker_id}@{self.agent.config.get('domain', 'serverhello')}"
            self.agent.logger.warning(f"Worker JID not found for {worker_id}, using fallback: {worker_jid}")

        self.agent.logger.info(f"Sending task assignment to worker {worker_id} ({worker_jid}) with protocol {protocol}")

        content = {
            'task_id': task.task_id,
            'task_type': task.task_type.value,
            'priority': task.priority.value,
            'parameters': task.parameters,
            'assigned_to': task.assigned_to,
            'assigned_at': task.assigned_at.isoformat() if task.assigned_at else None,
            'created_at': task.created_at.isoformat(),
            'status': task.status.value
        }
        
        await self.agent.send_request(to=worker_jid, protocol=protocol, content=content)
