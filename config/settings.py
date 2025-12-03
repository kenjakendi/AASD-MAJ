import os
from pathlib import Path


class Settings:
    
    # XMPP Server Configuration
    XMPP_SERVER = os.getenv('XMPP_SERVER', 'serverhello')
    XMPP_PORT = int(os.getenv('XMPP_PORT', '5222'))
    AGENT_PASSWORD = os.getenv('AGENT_PASSWORD', 'shelter123')
    
    # Retry Configuration
    MAX_RETRIES = int(os.getenv('MAX_RETRIES', '5'))
    RETRY_DELAY = int(os.getenv('RETRY_DELAY', '3'))
    
    # Task Configuration
    TASK_TIMEOUT = int(os.getenv('TASK_TIMEOUT', '300'))  # 5 minutes
    TASK_CHECK_INTERVAL = int(os.getenv('TASK_CHECK_INTERVAL', '5'))  # seconds
    
    # Animal Care Intervals (in seconds)
    FEED_INTERVAL = int(os.getenv('FEED_INTERVAL', '28800'))  # 8 hours
    WALK_INTERVAL = int(os.getenv('WALK_INTERVAL', '21600'))  # 6 hours
    HEALTH_CHECK_INTERVAL = int(os.getenv('HEALTH_CHECK_INTERVAL', '86400'))  # 24 hours
    
    # Room Cleaning Intervals
    DAILY_CLEAN_TIME = os.getenv('DAILY_CLEAN_TIME', '08:00')
    CLEAN_CHECK_INTERVAL = int(os.getenv('CLEAN_CHECK_INTERVAL', '3600'))  # 1 hour
    
    # Vaccination
    VACCINATION_WINDOW_DAYS = int(os.getenv('VACCINATION_WINDOW_DAYS', '7'))
    
    # Logging
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    LOG_DIR = Path(os.getenv('LOG_DIR', '/app/logs'))
    LOG_FORMAT = os.getenv('LOG_FORMAT', 
                          '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    
    # Coordinator Settings
    COORDINATOR_JID = f"coordinator@{XMPP_SERVER}"
    ASSIGNMENT_STRATEGY = os.getenv('ASSIGNMENT_STRATEGY', 'round_robin')  # round_robin, least_loaded, priority
    
    # Worker Settings
    WORKER_AVAILABILITY_UPDATE_INTERVAL = int(
        os.getenv('WORKER_AVAILABILITY_UPDATE_INTERVAL', '30')
    )
    
    # Priorities
    PRIORITY_URGENT = 1
    PRIORITY_HIGH = 2
    PRIORITY_NORMAL = 3
    PRIORITY_LOW = 4
    
    # Task Execution Times (simulation in seconds)
    FEED_TASK_DURATION = int(os.getenv('FEED_TASK_DURATION', '5'))
    WALK_TASK_DURATION = int(os.getenv('WALK_TASK_DURATION', '15'))
    CLEAN_TASK_DURATION = int(os.getenv('CLEAN_TASK_DURATION', '10'))
    VACCINATION_TASK_DURATION = int(os.getenv('VACCINATION_TASK_DURATION', '20'))
    HEALTH_CHECK_DURATION = int(os.getenv('HEALTH_CHECK_DURATION', '15'))
    INITIAL_CHECKUP_DURATION = int(os.getenv('INITIAL_CHECKUP_DURATION', '30'))
    
    @classmethod
    def get_coordinator_jid(cls) -> str:
        return cls.COORDINATOR_JID
    
    @classmethod
    def get_reception_jid(cls) -> str:
        return f"reception@{cls.XMPP_SERVER}"
    
    @classmethod
    def get_adoption_jid(cls) -> str:
        return f"adoption@{cls.XMPP_SERVER}"
