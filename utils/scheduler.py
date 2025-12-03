from typing import List, Dict, Optional
from datetime import datetime, date, timedelta
import asyncio

from models.animal import Animal
from config.settings import Settings


class VaccinationScheduler:
    
    def __init__(self):
        self.vaccination_window_days = Settings.VACCINATION_WINDOW_DAYS
    
    def is_due_for_vaccination(self, animal: Animal) -> bool:
        return animal.needs_vaccination()
    
    def get_due_vaccinations(self, animals: List[Animal]) -> List[Animal]:
        due_animals = []
        for animal in animals:
            if self.is_due_for_vaccination(animal):
                due_animals.append(animal)
        return due_animals
    
    def is_within_vaccination_window(self, next_due: str) -> bool:
        try:
            due_date = datetime.strptime(next_due, '%Y-%m-%d').date()
            today = date.today()
            window_start = today - timedelta(days=self.vaccination_window_days)
            window_end = today + timedelta(days=self.vaccination_window_days)
            
            return window_start <= due_date <= window_end
        except (ValueError, AttributeError):
            return False
    
    def calculate_next_vaccination_date(self, last_vaccination: str,
                                       vaccination_type: str = "routine") -> str:
        try:
            last_date = datetime.strptime(last_vaccination, '%Y-%m-%d').date()
        except (ValueError, AttributeError):
            last_date = date.today()
        
        # Different intervals for different vaccination types
        intervals = {
            'routine': 365,  # Annual
            'rabies': 365,
            'distemper': 365,
            'fvrcp': 365,  # For cats
            'booster': 180  # Semi-annual
        }
        
        interval_days = intervals.get(vaccination_type.lower(), 365)
        next_date = last_date + timedelta(days=interval_days)
        
        return next_date.strftime('%Y-%m-%d')
    
    def get_vaccination_priority(self, next_due: str) -> str:
        try:
            due_date = datetime.strptime(next_due, '%Y-%m-%d').date()
            today = date.today()
            days_until_due = (due_date - today).days
            
            if days_until_due < 0:
                return "urgent"  # Overdue
            elif days_until_due <= 7:
                return "high"
            elif days_until_due <= 30:
                return "normal"
            else:
                return "low"
        except (ValueError, AttributeError):
            return "normal"


class TaskScheduler:
    
    def __init__(self):
        self.scheduled_tasks = {}
    
    async def schedule_periodic_task(self, task_name: str, interval_seconds: int,
                                    callback, *args, **kwargs):
        async def periodic_execution():
            while True:
                try:
                    await callback(*args, **kwargs)
                except Exception as e:
                    print(f"Error in scheduled task {task_name}: {e}")
                await asyncio.sleep(interval_seconds)
        
        task = asyncio.create_task(periodic_execution())
        self.scheduled_tasks[task_name] = task
    
    def cancel_task(self, task_name: str):
        if task_name in self.scheduled_tasks:
            self.scheduled_tasks[task_name].cancel()
            del self.scheduled_tasks[task_name]
    
    def cancel_all_tasks(self):
        for task in self.scheduled_tasks.values():
            task.cancel()
        self.scheduled_tasks.clear()
