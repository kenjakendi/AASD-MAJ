import json
from spade.behaviour import CyclicBehaviour


class WorkerAvailabilityBehaviour(CyclicBehaviour):
    
    async def run(self):
        msg = await self.receive(timeout=10)
        if msg:
            try:
                content = json.loads(msg.body)
                worker_id = content.get('workerId')
                
                if worker_id:
                    # Update worker availability and capacity
                    self.agent.worker_availability[worker_id] = content.get('isAvailable', True)
                    self.agent.worker_current_load[worker_id] = content.get('currentLoad', 0)
                    self.agent.worker_max_concurrent_tasks[worker_id] = content.get('maxConcurrentTasks', 1)

                    # Store worker's actual JID for routing
                    worker_jid = content.get('workerJid')
                    if worker_jid:
                        self.agent.worker_jids[worker_id] = worker_jid

                    # Update competencies
                    competencies = content.get('competencies', [])
                    self.agent.worker_competencies[worker_id] = set(competencies)

                    self.agent.logger.info(f"Updated availability for {worker_id} ({worker_jid}): " +
                                          f"available={content.get('isAvailable')}, " +
                                          f"load={content.get('currentLoad')}/{content.get('maxConcurrentTasks')}, " +
                                          f"competencies={competencies}")

                    # Send confirmation
                    sender_jid = str(msg.sender)
                    await self.agent.send_confirm(
                        to=sender_jid,
                        protocol='ConfirmUpdateWorkerAvailability',
                        content={'workerId': worker_id, 'success': True}
                    )
                    
            except Exception as e:
                self.agent.logger.error(f"Error processing availability update: {e}")
