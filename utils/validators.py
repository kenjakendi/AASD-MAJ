from typing import Dict, Any, List, Optional
from datetime import datetime


def validate_task(task_data: Dict[str, Any]) -> tuple[bool, Optional[str]]:
    required_fields = ['task_id', 'task_type', 'priority', 'parameters']
    
    for field in required_fields:
        if field not in task_data:
            return False, f"Missing required field: {field}"
    
    valid_task_types = ['feed', 'walk', 'clean', 'vaccination', 
                       'health_check', 'initial_checkup', 'adoption_application']
    if task_data['task_type'] not in valid_task_types:
        return False, f"Invalid task type: {task_data['task_type']}"
    
    valid_priorities = ['urgent', 'high', 'normal', 'low']
    if task_data['priority'] not in valid_priorities:
        return False, f"Invalid priority: {task_data['priority']}"
    
    if not isinstance(task_data['parameters'], dict):
        return False, "Parameters must be a dictionary"
    
    return True, None


def validate_animal_data(animal_data: Dict[str, Any]) -> tuple[bool, Optional[str]]:
    required_fields = ['id', 'name', 'species', 'age', 'sex']
    
    for field in required_fields:
        if field not in animal_data:
            return False, f"Missing required field: {field}"
    
    if not isinstance(animal_data['age'], (int, float)) or animal_data['age'] < 0:
        return False, "Age must be a non-negative number"
    
    valid_species = ['dog', 'cat', 'rabbit', 'bird', 'hamster', 'guinea_pig', 'other']
    if animal_data['species'].lower() not in valid_species:
        return False, f"Invalid species: {animal_data['species']}"
    
    valid_sexes = ['male', 'female', 'unknown']
    if animal_data['sex'].lower() not in valid_sexes:
        return False, f"Invalid sex: {animal_data['sex']}"
    
    return True, None


def validate_room_data(room_data: Dict[str, Any]) -> tuple[bool, Optional[str]]:
    required_fields = ['id', 'name', 'type', 'capacity']
    
    for field in required_fields:
        if field not in room_data:
            return False, f"Missing required field: {field}"
    
    if not isinstance(room_data['capacity'], int) or room_data['capacity'] < 0:
        return False, "Capacity must be a non-negative integer"
    
    valid_room_types = ['animal_housing', 'medical', 'quarantine', 'common']
    if room_data['type'] not in valid_room_types:
        return False, f"Invalid room type: {room_data['type']}"
    
    return True, None


def validate_worker_data(worker_data: Dict[str, Any]) -> tuple[bool, Optional[str]]:
    required_fields = ['worker_id', 'name', 'role', 'competencies']
    
    for field in required_fields:
        if field not in worker_data:
            return False, f"Missing required field: {field}"
    
    valid_roles = ['caretaker', 'cleaner', 'veterinarian']
    if worker_data['role'] not in valid_roles:
        return False, f"Invalid role: {worker_data['role']}"
    
    if not isinstance(worker_data['competencies'], list):
        return False, "Competencies must be a list"
    
    return True, None


def validate_adoption_application(application_data: Dict[str, Any]) -> tuple[bool, Optional[str]]:
    required_fields = ['application_id', 'applicant_id', 'animal_id',
                      'applicant_name', 'applicant_age', 'applicant_contact']
    
    for field in required_fields:
        if field not in application_data:
            return False, f"Missing required field: {field}"
    
    if not isinstance(application_data['applicant_age'], int) or application_data['applicant_age'] < 18:
        return False, "Applicant must be at least 18 years old"
    
    if not application_data['applicant_contact']:
        return False, "Contact information is required"
    
    return True, None


def validate_jid(jid: str) -> tuple[bool, Optional[str]]:
    if '@' not in jid:
        return False, "JID must contain @ symbol"
    
    parts = jid.split('@')
    if len(parts) != 2:
        return False, "Invalid JID format"
    
    username, domain = parts
    if not username or not domain:
        return False, "JID username and domain cannot be empty"
    
    return True, None


def validate_time_format(time_str: str) -> tuple[bool, Optional[str]]:
    try:
        datetime.strptime(time_str, '%H:%M')
        return True, None
    except ValueError:
        return False, f"Invalid time format: {time_str}. Expected HH:MM"


def validate_date_format(date_str: str) -> tuple[bool, Optional[str]]:
    try:
        datetime.strptime(date_str, '%Y-%m-%d')
        return True, None
    except ValueError:
        return False, f"Invalid date format: {date_str}. Expected YYYY-MM-DD"
