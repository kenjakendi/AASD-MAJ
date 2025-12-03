from typing import Dict, Optional
from datetime import datetime
import uuid

from models.task import Task, TaskType, TaskStatus
from models.enums import Priority


class TaskGenerator:
    
    def __init__(self):
        self.task_counter = 0
    
    def generate_task_id(self, prefix: str = "task") -> str:
        self.task_counter += 1
        timestamp = int(datetime.now().timestamp())
        return f"{prefix}_{timestamp}_{self.task_counter}"
    
    def create_feed_task(self, animal_id: str, animal_name: str, 
                        dietary_requirements: str = "standard",
                        priority: Priority = Priority.NORMAL) -> Task:
        task_id = self.generate_task_id("feed")
        
        return Task(
            task_id=task_id,
            task_type=TaskType.FEED,
            priority=priority,
            parameters={
                'animalId': animal_id,
                'animalName': animal_name,
                'dietaryRequirements': dietary_requirements
            },
            protocol_name='FeedRequest'
        )
    
    def create_walk_task(self, animal_id: str, animal_name: str,
                        behavioral_notes: str = "",
                        priority: Priority = Priority.NORMAL) -> Task:
        task_id = self.generate_task_id("walk")
        
        return Task(
            task_id=task_id,
            task_type=TaskType.WALK,
            priority=priority,
            parameters={
                'animalId': animal_id,
                'animalName': animal_name,
                'behavioralNotes': behavioral_notes
            },
            protocol_name='WalkRequest'
        )
    
    def create_clean_task(self, room_id: str, room_name: str,
                         requires_special_cleaning: bool = False,
                         special_notes: str = "",
                         priority: Priority = Priority.NORMAL) -> Task:
        task_id = self.generate_task_id("clean")
        
        return Task(
            task_id=task_id,
            task_type=TaskType.CLEAN,
            priority=priority,
            parameters={
                'roomId': room_id,
                'roomName': room_name,
                'requiresSpecialCleaning': requires_special_cleaning,
                'specialNotes': special_notes
            },
            protocol_name='CleanRequest'
        )
    
    def create_vaccination_task(self, animal_id: str, animal_name: str,
                               vaccination_type: str = "routine",
                               priority: Priority = Priority.HIGH) -> Task:
        task_id = self.generate_task_id("vacc")
        
        return Task(
            task_id=task_id,
            task_type=TaskType.VACCINATION,
            priority=priority,
            parameters={
                'animalId': animal_id,
                'animalName': animal_name,
                'vaccinationType': vaccination_type
            },
            protocol_name='VaccinationRequest'
        )
    
    def create_health_check_task(self, animal_id: str, animal_name: str,
                                 health_status: str = "unknown",
                                 medications: list = None,
                                 priority: Priority = Priority.HIGH) -> Task:
        task_id = self.generate_task_id("health")
        
        return Task(
            task_id=task_id,
            task_type=TaskType.HEALTH_CHECK,
            priority=priority,
            parameters={
                'animalId': animal_id,
                'animalName': animal_name,
                'healthStatus': health_status,
                'medications': medications or []
            },
            protocol_name='HealthRequest'
        )
    
    def create_initial_checkup_task(self, animal_id: str, animal_name: str,
                                   priority: Priority = Priority.URGENT) -> Task:
        task_id = self.generate_task_id("checkup")
        
        return Task(
            task_id=task_id,
            task_type=TaskType.INITIAL_CHECKUP,
            priority=priority,
            parameters={
                'animalId': animal_id,
                'animalName': animal_name,
                'isNewArrival': True
            },
            protocol_name='InitialCheckupRequest'
        )
    
    def create_adoption_task(self, application_id: str, animal_id: str,
                           applicant_id: str,
                           priority: Priority = Priority.NORMAL) -> Task:
        task_id = self.generate_task_id("adoption")
        
        return Task(
            task_id=task_id,
            task_type=TaskType.ADOPTION_APPLICATION,
            priority=priority,
            parameters={
                'applicationId': application_id,
                'animalId': animal_id,
                'applicantId': applicant_id
            },
            protocol_name='AdoptionApplicationRequest'
        )
