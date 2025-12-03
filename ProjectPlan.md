# Szczegółowy Plan Implementacji - System Zarządzania Schroniskiem dla Zwierząt

## Struktura Projektu

```
animal-shelter-mas/
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
├── README.md
├── main.py
├── config/
│   ├── __init__.py
│   ├── settings.py
│   ├── coordinator.json
│   ├── caretaker_01.json
│   ├── caretaker_02.json
│   ├── cleaner_01.json
│   ├── veterinarian_01.json
│   ├── animals.json
│   ├── rooms.json
│   └── adoption.json
├── agents/
│   ├── __init__.py
│   ├── base_agent.py
│   ├── coordinator_agent.py
│   ├── worker_agent.py
│   ├── caretaker_agent.py
│   ├── cleaner_agent.py
│   ├── veterinarian_agent.py
│   ├── animal_assistant_agent.py
│   ├── room_agent.py
│   ├── reception_agent.py
│   ├── adoption_agent.py
│   └── applicant_agent.py
├── behaviours/
│   ├── __init__.py
│   ├── coordinator/
│   │   ├── __init__.py
│   │   ├── receive_requests_behaviour.py
│   │   ├── assign_tasks_behaviour.py
│   │   ├── monitor_completion_behaviour.py
│   │   ├── priority_management_behaviour.py
│   │   └── worker_availability_behaviour.py
│   ├── worker/
│   │   ├── __init__.py
│   │   ├── receive_task_behaviour.py
│   │   ├── execute_task_behaviour.py
│   │   └── update_availability_behaviour.py
│   ├── animal/
│   │   ├── __init__.py
│   │   ├── monitor_needs_behaviour.py
│   │   └── receive_confirmation_behaviour.py
│   ├── room/
│   │   ├── __init__.py
│   │   ├── monitor_cleanliness_behaviour.py
│   │   └── receive_clean_confirmation_behaviour.py
│   ├── reception/
│   │   ├── __init__.py
│   │   └── register_animal_behaviour.py
│   └── adoption/
│       ├── __init__.py
│       ├── receive_application_behaviour.py
│       └── process_adoption_behaviour.py
├── models/
│   ├── __init__.py
│   ├── task.py
│   ├── animal.py
│   ├── worker.py
│   ├── room.py
│   ├── adoption_application.py
│   └── enums.py
├── protocols/
│   ├── __init__.py
│   ├── feed_protocol.py
│   ├── walk_protocol.py
│   ├── clean_protocol.py
│   ├── health_protocol.py
│   ├── vaccination_protocol.py
│   ├── adoption_protocol.py
│   ├── registration_protocol.py
│   └── availability_protocol.py
├── utils/
│   ├── __init__.py
│   ├── message_builder.py
│   ├── task_generator.py
│   ├── scheduler.py
│   ├── logger.py
│   └── validators.py
├── data/
│   ├── __init__.py
│   └── storage.py
└── prosody/
    └── conf/
        └── prosody.cfg.lua
```

---

## ROOT DIRECTORY FILES

### `docker-compose.yml`
```yaml
version: '3.8'

services:
  # Serwer XMPP Prosody
  xmpp_server:
    image: prosody/prosody:latest
    container_name: shelter_xmpp
    hostname: serverhello
    environment:
      PROSODY_VIRTUAL_HOSTS: "serverhello"
      PROSODY_ADMINS: "admin@serverhello"
    ports:
      - "5222:5222"  # Client connections
      - "5269:5269"  # Server-to-server
      - "5280:5280"  # HTTP
    volumes:
      - ./prosody/conf/prosody.cfg.lua:/etc/prosody/prosody.cfg.lua
      - prosody_data:/var/lib/prosody
    networks:
      - shelter_net
    healthcheck:
      test: ["CMD", "prosodyctl", "status"]
      interval: 10s
      timeout: 5s
      retries: 5
    restart: unless-stopped

  # Coordinator Agent
  coordinator:
    build: .
    container_name: shelter_coordinator
    command: python -u main.py --role coordinator --config config/coordinator.json
    depends_on:
      xmpp_server:
        condition: service_healthy
    networks:
      - shelter_net
    environment:
      - XMPP_SERVER=serverhello
      - AGENT_PASSWORD=shelter123
      - LOG_LEVEL=INFO
    volumes:
      - ./logs:/app/logs
    restart: unless-stopped

  # Caretaker Agents
  caretaker_01:
    build: .
    container_name: shelter_caretaker_01
    command: python -u main.py --role caretaker --config config/caretaker_01.json
    depends_on:
      - coordinator
    networks:
      - shelter_net
    environment:
      - XMPP_SERVER=serverhello
      - AGENT_PASSWORD=shelter123
    volumes:
      - ./logs:/app/logs
    restart: unless-stopped

  caretaker_02:
    build: .
    container_name: shelter_caretaker_02
    command: python -u main.py --role caretaker --config config/caretaker_02.json
    depends_on:
      - coordinator
    networks:
      - shelter_net
    environment:
      - XMPP_SERVER=serverhello
      - AGENT_PASSWORD=shelter123
    volumes:
      - ./logs:/app/logs
    restart: unless-stopped

  # Cleaner Agent
  cleaner_01:
    build: .
    container_name: shelter_cleaner_01
    command: python -u main.py --role cleaner --config config/cleaner_01.json
    depends_on:
      - coordinator
    networks:
      - shelter_net
    environment:
      - XMPP_SERVER=serverhello
      - AGENT_PASSWORD=shelter123
    volumes:
      - ./logs:/app/logs
    restart: unless-stopped

  # Veterinarian Agent
  veterinarian_01:
    build: .
    container_name: shelter_veterinarian_01
    command: python -u main.py --role veterinarian --config config/veterinarian_01.json
    depends_on:
      - coordinator
    networks:
      - shelter_net
    environment:
      - XMPP_SERVER=serverhello
      - AGENT_PASSWORD=shelter123
    volumes:
      - ./logs:/app/logs
    restart: unless-stopped

  # Reception Agent
  reception:
    build: .
    container_name: shelter_reception
    command: python -u main.py --role reception --config config/reception.json
    depends_on:
      - coordinator
    networks:
      - shelter_net
    environment:
      - XMPP_SERVER=serverhello
      - AGENT_PASSWORD=shelter123
    volumes:
      - ./logs:/app/logs
    restart: unless-stopped

  # Adoption Agent
  adoption:
    build: .
    container_name: shelter_adoption
    command: python -u main.py --role adoption --config config/adoption.json
    depends_on:
      - coordinator
    networks:
      - shelter_net
    environment:
      - XMPP_SERVER=serverhello
      - AGENT_PASSWORD=shelter123
    volumes:
      - ./logs:/app/logs
    restart: unless-stopped

  # Animal Assistant Agents (dynamically created)
  animal_assistant:
    build: .
    container_name: shelter_animals
    command: python -u main.py --role animal_assistant --config config/animals.json
    depends_on:
      - coordinator
    networks:
      - shelter_net
    environment:
      - XMPP_SERVER=serverhello
      - AGENT_PASSWORD=shelter123
    volumes:
      - ./logs:/app/logs
    deploy:
      replicas: 1
    restart: unless-stopped

  # Room Agents
  rooms:
    build: .
    container_name: shelter_rooms
    command: python -u main.py --role room --config config/rooms.json
    depends_on:
      - coordinator
    networks:
      - shelter_net
    environment:
      - XMPP_SERVER=serverhello
      - AGENT_PASSWORD=shelter123
    volumes:
      - ./logs:/app/logs
    restart: unless-stopped

volumes:
  prosody_data:

networks:
  shelter_net:
    driver: bridge
```

**Opis:** Główny plik konfiguracyjny Docker Compose. Definiuje wszystkie kontenery systemu, ich zależności, zmienne środowiskowe i sieci. Każdy typ agenta ma własny kontener. Prosody jest serwerem XMPP z healthcheckiem zapewniającym, że agenci startują dopiero gdy serwer jest gotowy.

---

### `Dockerfile`
```dockerfile
FROM python:3.9-slim

# Metadane
LABEL maintainer="Team MAJ"
LABEL description="Animal Shelter Management System - Multi-Agent System"

# Ustaw workdir
WORKDIR /app

# Zainstaluj zależności systemowe
RUN apt-get update && apt-get install -y \
    gcc \
    libssl-dev \
    && rm -rf /var/lib/apt/lists/*

# Skopiuj requirements
COPY requirements.txt .

# Zainstaluj zależności Python
RUN pip install --no-cache-dir -r requirements.txt

# Skopiuj kod aplikacji
COPY . .

# Utwórz katalog na logi
RUN mkdir -p /app/logs

# Ustaw zmienne środowiskowe
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app

# Domyślne polecenie
CMD ["python", "-u", "main.py"]
```

**Opis:** Dockerfile definiujący obraz Docker dla wszystkich agentów. Bazuje na Python 3.9, instaluje zależności systemowe potrzebne do SPADE i XMPP, kopiuje kod aplikacji i tworzy katalog na logi. PYTHONUNBUFFERED=1 zapewnia natychmiastowe wyświetlanie logów.

---

### `requirements.txt`
```txt
# SPADE Framework
spade==3.3.2

# XMPP Client
aioxmpp==0.13.3
slixmpp==1.8.5

# Async support
aiohttp==3.9.1
asyncio==3.4.3

# Data handling
pydantic==2.5.3
python-dateutil==2.8.2

# Configuration
pyyaml==6.0.1
python-dotenv==1.0.0

# Logging
colorlog==6.8.0
python-json-logger==2.0.7

# Utilities
schedule==1.2.0
```

**Opis:** Lista wszystkich zależności Python wymaganych przez projekt. SPADE to główny framework agentowy, pydantic do walidacji danych, colorlog do kolorowych logów w konsoli.

---

### `README.md`
```markdown
# System Zarządzania Schroniskiem dla Zwierząt
## Multi-Agent System (MAS)

### Zespół MAJ
- Michał Laskowski 310181
- Adam Dąbkowski 310035
- Jarosław (Yaroslav) Harbar 317044

### Opis projektu
System wieloagentowy do zarządzania schroniskiem dla zwierząt wykorzystujący framework SPADE i protokół XMPP.

### Architektura
System składa się z następujących typów agentów:
- **CoordinatorAgent** - centralny koordynator zadań
- **WorkerAgent** - pracownicy (Caretaker, Cleaner, Veterinarian)
- **AnimalAssistantAgent** - reprezentacja zwierząt
- **RoomAgent** - reprezentacja pomieszczeń
- **ReceptionAgent** - obsługa przyjęć zwierząt
- **AdoptionAgent** - proces adopcyjny
- **ApplicantAgent** - osoby ubiegające się o adopcję

### Wymagania
- Docker >= 20.10
- Docker Compose >= 2.0
- Python >= 3.9 (dla lokalnego developmentu)

### Instalacja i uruchomienie

#### Uruchomienie całego systemu:
```bash
docker-compose up --build
```

#### Uruchomienie pojedynczego agenta:
```bash
docker-compose up coordinator
```

#### Monitoring logów:
```bash
docker-compose logs -f coordinator
```

#### Zatrzymanie systemu:
```bash
docker-compose down
```

### Struktura projektu
[Zobacz dokumentację w docs/architecture.md]

### Konfiguracja
Pliki konfiguracyjne znajdują się w katalogu `config/`. Każdy agent ma własny plik JSON z parametrami.

### Protokoły komunikacji
System implementuje następujące protokoły:
- Feed Protocol (karmienie)
- Walk Protocol (spacery)
- Clean Protocol (sprzątanie)
- Health Protocol (opieka zdrowotna)
- Vaccination Protocol (szczepienia)
- Adoption Protocol (adopcja)
- Registration Protocol (rejestracja zwierząt)

### Licencja
MIT License
```

**Opis:** Plik dokumentacji projektu zawierający podstawowe informacje o systemie, instrukcje instalacji i uruchomienia, opis architektury i struktury projektu.

---

### `main.py`
```python
"""
Main entry point for Animal Shelter Management System
Handles agent initialization and lifecycle management
"""

import asyncio
import argparse
import json
import os
import sys
import signal
from typing import List, Optional
from pathlib import Path

from agents.coordinator_agent import CoordinatorAgent
from agents.caretaker_agent import CaretakerAgent
from agents.cleaner_agent import CleanerAgent
from agents.veterinarian_agent import VeterinarianAgent
from agents.animal_assistant_agent import AnimalAssistantAgent
from agents.room_agent import RoomAgent
from agents.reception_agent import ReceptionAgent
from agents.adoption_agent import AdoptionAgent
from agents.applicant_agent import ApplicantAgent

from config.settings import Settings
from utils.logger import setup_logger

# Global list to track active agents
active_agents: List = []
logger = None


def load_config(config_path: str) -> dict:
    """Load configuration from JSON file"""
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        logger.error(f"Configuration file not found: {config_path}")
        sys.exit(1)
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON in configuration file: {e}")
        sys.exit(1)


async def create_coordinator(config: dict) -> CoordinatorAgent:
    """Create and start coordinator agent"""
    jid = config.get('jid', f"coordinator@{Settings.XMPP_SERVER}")
    password = config.get('password', Settings.AGENT_PASSWORD)
    
    logger.info(f"Creating Coordinator Agent: {jid}")
    agent = CoordinatorAgent(jid, password, config)
    await agent.start_with_retry(max_retries=Settings.MAX_RETRIES)
    return agent


async def create_caretaker(config: dict) -> CaretakerAgent:
    """Create and start caretaker agent"""
    jid = config['jid']
    password = config.get('password', Settings.AGENT_PASSWORD)
    
    logger.info(f"Creating Caretaker Agent: {jid}")
    agent = CaretakerAgent(jid, password, config)
    await agent.start_with_retry(max_retries=Settings.MAX_RETRIES)
    return agent


async def create_cleaner(config: dict) -> CleanerAgent:
    """Create and start cleaner agent"""
    jid = config['jid']
    password = config.get('password', Settings.AGENT_PASSWORD)
    
    logger.info(f"Creating Cleaner Agent: {jid}")
    agent = CleanerAgent(jid, password, config)
    await agent.start_with_retry(max_retries=Settings.MAX_RETRIES)
    return agent


async def create_veterinarian(config: dict) -> VeterinarianAgent:
    """Create and start veterinarian agent"""
    jid = config['jid']
    password = config.get('password', Settings.AGENT_PASSWORD)
    
    logger.info(f"Creating Veterinarian Agent: {jid}")
    agent = VeterinarianAgent(jid, password, config)
    await agent.start_with_retry(max_retries=Settings.MAX_RETRIES)
    return agent


async def create_animal_assistants(config: dict) -> List[AnimalAssistantAgent]:
    """Create and start multiple animal assistant agents"""
    agents = []
    animals = config.get('animals', [])
    
    for animal_data in animals:
        jid = f"animal_{animal_data['id']}@{Settings.XMPP_SERVER}"
        password = Settings.AGENT_PASSWORD
        
        logger.info(f"Creating Animal Assistant Agent: {jid} ({animal_data['name']})")
        agent = AnimalAssistantAgent(jid, password, animal_data)
        await agent.start_with_retry(max_retries=Settings.MAX_RETRIES)
        agents.append(agent)
    
    return agents


async def create_rooms(config: dict) -> List[RoomAgent]:
    """Create and start multiple room agents"""
    agents = []
    rooms = config.get('rooms', [])
    
    for room_data in rooms:
        jid = f"room_{room_data['id']}@{Settings.XMPP_SERVER}"
        password = Settings.AGENT_PASSWORD
        
        logger.info(f"Creating Room Agent: {jid} ({room_data['name']})")
        agent = RoomAgent(jid, password, room_data)
        await agent.start_with_retry(max_retries=Settings.MAX_RETRIES)
        agents.append(agent)
    
    return agents


async def create_reception(config: dict) -> ReceptionAgent:
    """Create and start reception agent"""
    jid = config.get('jid', f"reception@{Settings.XMPP_SERVER}")
    password = config.get('password', Settings.AGENT_PASSWORD)
    
    logger.info(f"Creating Reception Agent: {jid}")
    agent = ReceptionAgent(jid, password, config)
    await agent.start_with_retry(max_retries=Settings.MAX_RETRIES)
    return agent


async def create_adoption(config: dict) -> AdoptionAgent:
    """Create and start adoption agent"""
    jid = config.get('jid', f"adoption@{Settings.XMPP_SERVER}")
    password = config.get('password', Settings.AGENT_PASSWORD)
    
    logger.info(f"Creating Adoption Agent: {jid}")
    agent = AdoptionAgent(jid, password, config)
    await agent.start_with_retry(max_retries=Settings.MAX_RETRIES)
    return agent


async def create_applicants(config: dict) -> List[ApplicantAgent]:
    """Create and start applicant agents"""
    agents = []
    applicants = config.get('applicants', [])
    
    for applicant_data in applicants:
        jid = f"applicant_{applicant_data['id']}@{Settings.XMPP_SERVER}"
        password = Settings.AGENT_PASSWORD
        
        logger.info(f"Creating Applicant Agent: {jid}")
        agent = ApplicantAgent(jid, password, applicant_data)
        await agent.start_with_retry(max_retries=Settings.MAX_RETRIES)
        agents.append(agent)
    
    return agents


async def shutdown_agents():
    """Gracefully shutdown all active agents"""
    logger.info("Shutting down all agents...")
    for agent in active_agents:
        try:
            await agent.stop()
            logger.info(f"Agent {agent.jid} stopped successfully")
        except Exception as e:
            logger.error(f"Error stopping agent {agent.jid}: {e}")


def signal_handler(signum, frame):
    """Handle shutdown signals"""
    logger.info(f"Received signal {signum}, initiating shutdown...")
    asyncio.create_task(shutdown_agents())
    sys.exit(0)


async def main():
    """Main entry point"""
    global logger
    
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Animal Shelter Management System')
    parser.add_argument('--role', required=True, 
                       choices=['coordinator', 'caretaker', 'cleaner', 'veterinarian',
                               'animal_assistant', 'room', 'reception', 'adoption', 'applicant'],
                       help='Role of the agent to start')
    parser.add_argument('--config', required=True,
                       help='Path to configuration file')
    parser.add_argument('--log-level', default='INFO',
                       choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
                       help='Logging level')
    
    args = parser.parse_args()
    
    # Setup logger
    logger = setup_logger(args.role, args.log_level)
    logger.info(f"Starting Animal Shelter MAS - Role: {args.role}")
    
    # Register signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Load configuration
    config = load_config(args.config)
    
    # Create and start agents based on role
    try:
        if args.role == 'coordinator':
            agent = await create_coordinator(config)
            active_agents.append(agent)
            
        elif args.role == 'caretaker':
            agent = await create_caretaker(config)
            active_agents.append(agent)
            
        elif args.role == 'cleaner':
            agent = await create_cleaner(config)
            active_agents.append(agent)
            
        elif args.role == 'veterinarian':
            agent = await create_veterinarian(config)
            active_agents.append(agent)
            
        elif args.role == 'animal_assistant':
            agents = await create_animal_assistants(config)
            active_agents.extend(agents)
            
        elif args.role == 'room':
            agents = await create_rooms(config)
            active_agents.extend(agents)
            
        elif args.role == 'reception':
            agent = await create_reception(config)
            active_agents.append(agent)
            
        elif args.role == 'adoption':
            agent = await create_adoption(config)
            active_agents.append(agent)
            
        elif args.role == 'applicant':
            agents = await create_applicants(config)
            active_agents.extend(agents)
        
        logger.info(f"All agents for role '{args.role}' started successfully")
        
        # Keep running until interrupted
        try:
            while True:
                await asyncio.sleep(1)
        except KeyboardInterrupt:
            logger.info("Keyboard interrupt received")
            
    except Exception as e:
        logger.error(f"Error during agent initialization: {e}", exc_info=True)
        sys.exit(1)
    finally:
        await shutdown_agents()


if __name__ == "__main__":
    asyncio.run(main())
```

**Opis:** Główny punkt wejścia aplikacji. Parsuje argumenty linii poleceń, ładuje konfigurację, tworzy i zarządza cyklem życia agentów. Obsługuje sygnały zamknięcia (SIGINT, SIGTERM) zapewniając graceful shutdown. Każda rola (coordinator, caretaker, etc.) ma dedykowaną funkcję tworzącą odpowiedniego agenta.

---

## CONFIG DIRECTORY

### `config/__init__.py`
```python
"""
Configuration package for Animal Shelter MAS
"""

from .settings import Settings

__all__ = ['Settings']
```

**Opis:** Inicjalizacja pakietu konfiguracji, eksportuje klasę Settings.

---

### `config/settings.py`
```python
"""
Global settings and constants for the Animal Shelter MAS
"""

import os
from pathlib import Path


class Settings:
    """Global application settings"""
    
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
        """Get coordinator JID"""
        return cls.COORDINATOR_JID
    
    @classmethod
    def get_reception_jid(cls) -> str:
        """Get reception JID"""
        return f"reception@{cls.XMPP_SERVER}"
    
    @classmethod
    def get_adoption_jid(cls) -> str:
        """Get adoption JID"""
        return f"adoption@{cls.XMPP_SERVER}"
```

**Opis:** Centralna klasa konfiguracyjna zawierająca wszystkie globalne ustawienia systemu. Czyta zmienne środowiskowe z możliwością ustawienia wartości domyślnych. Definiuje interwały czasowe, timeouty, priorytety i czasy symulacji wykonania zadań.

---

### `config/coordinator.json`
```json
{
  "jid": "coordinator@serverhello",
  "password": "shelter123",
  "role": "coordinator",
  "assignment_strategy": "round_robin",
  "task_check_interval": 5,
  "max_concurrent_tasks_per_worker": 3,
  "enable_priority_management": true,
  "enable_fair_rotation": true,
  "emergency_response_enabled": true,
  "log_level": "INFO"
}
```

**Opis:** Konfiguracja dla agenta Coordinator. Określa strategię przydzielania zadań (round-robin), maksymalną liczbę zadań na pracownika, włącza zarządzanie priorytetami i sprawiedliwą rotację.

---

### `config/caretaker_01.json`
```json
{
  "jid": "caretaker_01@serverhello",
  "password": "shelter123",
  "role": "caretaker",
  "worker_id": "caretaker_01",
  "name": "Anna Kowalska",
  "competencies": ["feed", "walk"],
  "max_concurrent_tasks": 2,
  "availability": {
    "monday": ["08:00-16:00"],
    "tuesday": ["08:00-16:00"],
    "wednesday": ["08:00-16:00"],
    "thursday": ["08:00-16:00"],
    "friday": ["08:00-16:00"],
    "saturday": ["09:00-13:00"],
    "sunday": []
  },
  "preferences": {
    "preferred_animals": ["dog", "cat"],
    "avoid_tasks": []
  },
  "log_level": "INFO"
}
```

**Opis:** Konfiguracja dla agenta Caretaker #1. Definiuje kompetencje (karmienie, spacery), dostępność w poszczególne dni tygodnia, preferencje dotyczące zwierząt. Każdy caretaker ma unikalne ID i dane personalne.

---

### `config/caretaker_02.json`
```json
{
  "jid": "caretaker_02@serverhello",
  "password": "shelter123",
  "role": "caretaker",
  "worker_id": "caretaker_02",
  "name": "Jan Nowak",
  "competencies": ["feed", "walk"],
  "max_concurrent_tasks": 3,
  "availability": {
    "monday": ["14:00-22:00"],
    "tuesday": ["14:00-22:00"],
    "wednesday": ["14:00-22:00"],
    "thursday": ["14:00-22:00"],
    "friday": ["14:00-22:00"],
    "saturday": ["14:00-18:00"],
    "sunday": ["10:00-14:00"]
  },
  "preferences": {
    "preferred_animals": ["dog"],
    "avoid_tasks": []
  },
  "log_level": "INFO"
}
```

**Opis:** Konfiguracja dla agenta Caretaker #2 z innymi godzinami pracy (popołudniowo-wieczorne) zapewniając coverage przez cały dzień.

---

### `config/cleaner_01.json`
```json
{
  "jid": "cleaner_01@serverhello",
  "password": "shelter123",
  "role": "cleaner",
  "worker_id": "cleaner_01",
  "name": "Maria Wiśniewska",
  "competencies": ["clean"],
  "max_concurrent_tasks": 4,
  "availability": {
    "monday": ["06:00-14:00"],
    "tuesday": ["06:00-14:00"],
    "wednesday": ["06:00-14:00"],
    "thursday": ["06:00-14:00"],
    "friday": ["06:00-14:00"],
    "saturday": ["07:00-11:00"],
    "sunday": []
  },
  "preferences": {
    "preferred_rooms": [],
    "daily_routine_start": "07:00"
  },
  "log_level": "INFO"
}
```

**Opis:** Konfiguracja dla agenta Cleaner. Pracuje w wczesnych godzinach rannych, może obsługiwać więcej zadań jednocześnie (4) gdyż sprzątanie jest bardziej powtarzalne.

---

### `config/veterinarian_01.json`
```json
{
  "jid": "veterinarian_01@serverhello",
  "password": "shelter123",
  "role": "veterinarian",
  "worker_id": "vet_01",
  "name": "Dr. Piotr Kamiński",
  "competencies": ["vaccination", "health_check", "initial_checkup"],
  "max_concurrent_tasks": 1,
  "availability": {
    "monday": ["09:00-17:00"],
    "tuesday": ["09:00-17:00"],
    "wednesday": ["09:00-17:00"],
    "thursday": ["09:00-17:00"],
    "friday": ["09:00-13:00"],
    "saturday": [],
    "sunday": []
  },
  "specializations": ["dogs", "cats", "small_animals"],
  "emergency_available": true,
  "log_level": "INFO"
}
```

**Opis:** Konfiguracja dla agenta Veterinarian. Może obsługiwać tylko jedno zadanie jednocześnie (wymaga koncentracji), ma określone specjalizacje i dostępność w nagłych przypadkach.

---

### `config/animals.json`
```json
{
  "animals": [
    {
      "id": "001",
      "name": "Burek",
      "species": "dog",
      "breed": "Mixed",
      "age": 3,
      "sex": "male",
      "health_status": "healthy",
      "vaccination_status": {
        "rabies": "2024-06-15",
        "distemper": "2024-06-15"
      },
      "next_vaccination_due": "2025-06-15",
      "dietary_requirements": "standard",
      "behavioral_notes": "Friendly, loves walks",
      "adoption_status": "available"
    },
    {
      "id": "002",
      "name": "Mruczek",
      "species": "cat",
      "breed": "Persian",
      "age": 2,
      "sex": "female",
      "health_status": "healthy",
      "vaccination_status": {
        "fvrcp": "2024-08-20"
      },
      "next_vaccination_due": "2025-08-20",
      "dietary_requirements": "sensitive_stomach",
      "behavioral_notes": "Shy, needs quiet environment",
      "adoption_status": "available"
    },
    {
      "id": "003",
      "name": "Reksio",
      "species": "dog",
      "breed": "German Shepherd",
      "age": 5,
      "sex": "male",
      "health_status": "chronic_condition",
      "vaccination_status": {
        "rabies": "2024-03-10",
        "distemper": "2024-03-10"
      },
      "next_vaccination_due": "2025-03-10",
      "dietary_requirements": "special_diet",
      "behavioral_notes": "Needs experienced owner, good with kids",
      "adoption_status": "available",
      "medications": ["Joint supplement", "Pain management"]
    }
  ]
}
```

**Opis:** Konfiguracja definiująca wszystkie zwierzęta w schronisku. Każde zwierzę ma kompletny profil medyczny, behawioralny i status adopcyjny. System automatycznie tworzy AnimalAssistantAgent dla każdego zwierzęcia.

---

### `config/rooms.json`
```json
{
  "rooms": [
    {
      "id": "R001",
      "name": "Dog Room A",
      "type": "animal_housing",
      "capacity": 8,
      "current_occupants": ["001", "003"],
      "cleanliness_state": "clean",
      "daily_clean_time": "07:00",
      "clean_frequency_hours": 24,
      "requires_special_cleaning": false
    },
    {
      "id": "R002",
      "name": "Cat Room A",
      "type": "animal_housing",
      "capacity": 10,
      "current_occupants": ["002"],
      "cleanliness_state": "clean",
      "daily_clean_time": "07:30",
      "clean_frequency_hours": 24,
      "requires_special_cleaning": false
    },
    {
      "id": "R003",
      "name": "Veterinary Office",
      "type": "medical",
      "capacity": 2,
      "current_occupants": [],
      "cleanliness_state": "clean",
      "daily_clean_time": "08:00",
      "clean_frequency_hours": 12,
      "requires_special_cleaning": true,
      "special_cleaning_notes": "Medical-grade disinfection required"
    },
    {
      "id": "R004",
      "name": "Quarantine Room",
      "type": "quarantine",
      "capacity": 4,
      "current_occupants": [],
      "cleanliness_state": "clean",
      "daily_clean_time": "07:00",
      "clean_frequency_hours": 8,
      "requires_special_cleaning": true,
      "special_cleaning_notes": "Isolation protocols"
    },
    {
      "id": "R005",
      "name": "Common Area",
      "type": "common",
      "capacity": 0,
      "current_occupants": [],
      "cleanliness_state": "clean",
      "daily_clean_time": "06:30",
      "clean_frequency_hours": 8,
      "requires_special_cleaning": false
    }
  ]
}
```

**Opis:** Konfiguracja wszystkich pomieszczeń w schronisku. Każde pomieszczenie ma typ, pojemność, aktualnych mieszkańców, harmonogram sprzątania. Pomieszczenia medyczne i kwarantanny wymagają specjalnego czyszczenia.

---

### `config/reception.json`
```json
{
  "jid": "reception@serverhello",
  "password": "shelter123",
  "role": "reception",
  "operating_hours": {
    "monday": ["09:00-17:00"],
    "tuesday": ["09:00-17:00"],
    "wednesday": ["09:00-17:00"],
    "thursday": ["09:00-17:00"],
    "friday": ["09:00-17:00"],
    "saturday": ["10:00-14:00"],
    "sunday": []
  },
  "quarantine_room_id": "R004",
  "default_initial_checkup_priority": "high",
  "log_level": "INFO"
}
```

**Opis:** Konfiguracja dla agenta Reception odpowiedzialnego za przyjmowanie nowych zwierząt. Definiuje godziny otwarcia i pokój kwarantanny dla nowo przyjętych zwierząt.

---

### `config/adoption.json`
```json
{
  "jid": "adoption@serverhello",
  "password": "shelter123",
  "role": "adoption",
  "processing_interval": 60,
  "application_review_time": 300,
  "adoption_criteria": {
    "min_age": 21,
    "requires_home_visit": true,
    "requires_reference": true,
    "requires_previous_pet_experience": false
  },
  "adoption_fee": {
    "dog": 500,
    "cat": 300,
    "small_animal": 100
  },
  "log_level": "INFO"
}
```

**Opis:** Konfiguracja dla agenta Adoption. Definiuje kryteria adopcyjne, opłaty adopcyjne dla różnych typów zwierząt, czas przetwarzania wniosków.

---

## AGENTS DIRECTORY

### `agents/__init__.py`
```python
"""
Agents package for Animal Shelter MAS
Contains all agent implementations
"""

from .base_agent import BaseAgent
from .coordinator_agent import CoordinatorAgent
from .worker_agent import WorkerAgent
from .caretaker_agent import CaretakerAgent
from .cleaner_agent import CleanerAgent
from .veterinarian_agent import VeterinarianAgent
from .animal_assistant_agent import AnimalAssistantAgent
from .room_agent import RoomAgent
from .reception_agent import ReceptionAgent
from .adoption_agent import AdoptionAgent
from .applicant_agent import ApplicantAgent

__all__ = [
    'BaseAgent',
    'CoordinatorAgent',
    'WorkerAgent',
    'CaretakerAgent',
    'CleanerAgent',
    'VeterinarianAgent',
    'AnimalAssistantAgent',
    'RoomAgent',
    'ReceptionAgent',
    'AdoptionAgent',
    'ApplicantAgent'
]
```

**Opis:** Inicjalizacja pakietu agents, eksportuje wszystkie klasy agentów.

---

### `agents/base_agent.py`
```python
"""
Base Agent class - parent for all agents in the system
Provides common functionality for XMPP communication and lifecycle management
"""

from spade.agent import Agent
from spade.message import Message
from spade.template import Template
import json
import time
import asyncio
from typing import Dict, Any, Optional
from datetime import datetime

from config.settings import Settings
from utils.logger import get_logger
from utils.message_builder import MessageBuilder


class BaseAgent(Agent):
    """Base class for all agents in the Animal Shelter MAS"""
    
    def __init__(self, jid: str, password: str, config: Optional[Dict] = None,
                 verify_security: bool = False):
        """
        Initialize base agent
        
        Args:
            jid: Jabber ID of the agent
            password: Password for XMPP server
            config: Configuration dictionary
            verify_security: Whether to verify SSL certificates
        """
        super().__init__(jid, password, verify_security)
        self.config = config or {}
        self.logger = get_logger(self.name)
        self.message_builder = MessageBuilder()
        self.start_time = None
        
    @property
    def name(self) -> str:
        """Get agent name from JID"""
        return str(self.jid).split('@')[0]
    
    async def setup(self):
        """Setup agent - called when agent starts"""
        self.start_time = datetime.now()
        self.logger.info(f"Agent {self.jid} is starting up")
        
    async def start_with_retry(self, max_retries: int = 5, delay: int = 3) -> bool:
        """
        Start agent with retry mechanism
        
        Args:
            max_retries: Maximum number of retry attempts
            delay: Delay between retries in seconds
            
        Returns:
            bool: True if started successfully, False otherwise
        """
        for attempt in range(1, max_retries + 1):
            try:
                await self.start(auto_register=True)
                self.logger.info(f"Agent {self.jid} registered successfully (attempt {attempt})")
                return True
            except Exception as e:
                self.logger.warning(f"Attempt {attempt}/{max_retries} failed: {e}")
                if attempt < max_retries:
                    self.logger.info(f"Retrying in {delay} seconds...")
                    await asyncio.sleep(delay)
                else:
                    self.logger.error(f"Failed to start agent after {max_retries} attempts")
                    raise
        return False
    
    async def send_message(self, to: str, content: Dict[str, Any], 
                          metadata: Optional[Dict[str, str]] = None) -> None:
        """
        Send message to another agent
        
        Args:
            to: Recipient JID
            content: Message content (will be JSON serialized)
            metadata: Optional metadata for message
        """
        msg = Message(to=to)
        msg.set_metadata("performative", "inform")
        
        if metadata:
            for key, value in metadata.items():
                msg.set_metadata(key, str(value))
        
        msg.body = json.dumps(content, default=str)
        
        await self.send(msg)
        self.logger.debug(f"Sent message to {to}: {content}")
    
    async def send_request(self, to: str, protocol: str, content: Dict[str, Any]) -> None:
        """
        Send a request message
        
        Args:
            to: Recipient JID
            protocol: Protocol name
            content: Request content
        """
        await self.send_message(
            to=to,
            content=content,
            metadata={
                'protocol': protocol,
                'performative': 'request',
                'timestamp': datetime.now().isoformat()
            }
        )
    
    async def send_confirm(self, to: str, protocol: str, content: Dict[str, Any]) -> None:
        """
        Send a confirmation message
        
        Args:
            to: Recipient JID
            protocol: Protocol name
            content: Confirmation content
        """
        await self.send_message(
            to=to,
            content=content,
            metadata={
                'protocol': protocol,
                'performative': 'confirm',
                'timestamp': datetime.now().isoformat()
            }
        )
    
    async def send_inform(self, to: str, protocol: str, content: Dict[str, Any]) -> None:
        """
        Send an inform message
        
        Args:
            to: Recipient JID
            protocol: Protocol name
            content: Information content
        """
        await self.send_message(
            to=to,
            content=content,
            metadata={
                'protocol': protocol,
                'performative': 'inform',
                'timestamp': datetime.now().isoformat()
            }
        )
    
    def get_uptime(self) -> float:
        """Get agent uptime in seconds"""
        if self.start_time:
            return (datetime.now() - self.start_time).total_seconds()
        return 0
    
    def get_config_value(self, key: str, default: Any = None) -> Any:
        """
        Get configuration value
        
        Args:
            key: Configuration key
            default: Default value if key not found
            
        Returns:
            Configuration value or default
        """
        return self.config.get(key, default)
```

**Opis:** Bazowa klasa dla wszystkich agentów. Implementuje wspólną funkcjonalność: mechanizm retry przy starcie, wysyłanie wiadomości z różnymi performatives (request, inform, confirm), logowanie, zarządzanie konfiguracją. Wszystkie agenty dziedziczą po tej klasie.

---

### `agents/coordinator_agent.py`
```python
"""
Coordinator Agent - Central task coordinator
Responsible for receiving requests, assigning tasks, and monitoring completion
"""

from typing import Dict, List, Set, Optional
from datetime import datetime, timedelta
import asyncio

from spade.template import Template

from agents.base_agent import BaseAgent
from models.task import Task, TaskStatus, TaskType
from models.enums import Priority
from behaviours.coordinator.receive_requests_behaviour import (
    ReceiveCleanRequestBehaviour,
    ReceiveFeedRequestBehaviour,
    ReceiveWalkRequestBehaviour,
    ReceiveHealthRequestBehaviour,
    ReceiveNewAnimalBehaviour,
    ReceiveAdoptionApplicationBehaviour
)
from behaviours.coordinator.assign_tasks_behaviour import AssignTasksBehaviour
from behaviours.coordinator.monitor_completion_behaviour import MonitorCompletionBehaviour
from behaviours.coordinator.priority_management_behaviour import PriorityManagementBehaviour
from behaviours.coordinator.worker_availability_behaviour import WorkerAvailabilityBehaviour
from utils.task_generator import TaskGenerator
from utils.scheduler import VaccinationScheduler


class CoordinatorAgent(BaseAgent):
    """
    Coordinator Agent
    Central coordinator responsible for:
    - Receiving care requests from animals, rooms, etc.
    - Managing worker availability
    - Assigning tasks to available workers
    - Monitoring task completion
    - Handling emergency situations
    - Managing priorities
    """
    
    def __init__(self, jid: str, password: str, config: Dict):
        super().__init__(jid, password, config)
        
        # Task management
        self.pending_requests: List[Dict] = []
        self.active_tasks: Dict[str, Task] = {}
        self.completed_tasks: List[Task] = []
        self.failed_tasks: List[Task] = []
        
        # Worker management
        self.worker_availability: Dict[str, bool] = {}
        self.worker_competencies: Dict[str, Set[str]] = {}
        self.worker_current_load: Dict[str, int] = {}
        self.worker_preferences: Dict[str, Dict] = {}
        
        # Animal and room tracking
        self.animal_task_history: Dict[str, List[str]] = {}
        self.room_last_cleaned: Dict[str, datetime] = {}
        
        # Assignment strategy
        self.assignment_strategy = config.get('assignment_strategy', 'round_robin')
        self.last_assigned_worker: Dict[TaskType, str] = {}
        
        # Task generator and scheduler
        self.task_generator = TaskGenerator()
        self.vaccination_scheduler = VaccinationScheduler()
        
        # Statistics
        self.stats = {
            'total_tasks_assigned': 0,
            'total_tasks_completed': 0,
            'total_tasks_failed': 0,
            'emergency_tasks_handled': 0
        }
    
    async def setup(self):
        """Setup coordinator agent and behaviours"""
        await super().setup()
        
        self.logger.info("Setting up Coordinator Agent")
        
        # Behaviour 1: Receive Clean Requests
        clean_template = Template()
        clean_template.set_metadata("protocol", "CleanRequest")
        self.add_behaviour(ReceiveCleanRequestBehaviour(), clean_template)
        
        # Behaviour 2: Receive Feed Requests
        feed_template = Template()
        feed_template.set_metadata("protocol", "FeedRequest")
        self.add_behaviour(ReceiveFeedRequestBehaviour(), feed_template)
        
        # Behaviour 3: Receive Walk Requests
        walk_template = Template()
        walk_template.set_metadata("protocol", "WalkRequest")
        self.add_behaviour(ReceiveWalkRequestBehaviour(), walk_template)
        
        # Behaviour 4: Receive Health Requests
        health_template = Template()
        health_template.set_metadata("protocol", "HealthRequest")
        self.add_behaviour(ReceiveHealthRequestBehaviour(), health_template)
        
        # Behaviour 5: Receive New Animal Registrations
        registration_template = Template()
        registration_template.set_metadata("protocol", "RegisterNewAnimal")
        self.add_behaviour(ReceiveNewAnimalBehaviour(), registration_template)
        
        # Behaviour 6: Receive Adoption Applications
        adoption_template = Template()
        adoption_template.set_metadata("protocol", "AdoptionApplicationRequest")
        self.add_behaviour(ReceiveAdoptionApplicationBehaviour(), adoption_template)
        
        # Behaviour 7: Monitor Worker Availability
        availability_template = Template()
        availability_template.set_metadata("protocol", "UpdateWorkerAvailability")
        self.add_behaviour(WorkerAvailabilityBehaviour(), availability_template)
        
        # Behaviour 8: Assign Tasks (Periodic)
        task_check_interval = self.config.get('task_check_interval', 5)
        self.add_behaviour(AssignTasksBehaviour(period=task_check_interval))
        
        # Behaviour 9: Monitor Task Completion
        completion_template = Template()
        completion_template.set_metadata("performative", "confirm")
        self.add_behaviour(MonitorCompletionBehaviour(), completion_template)
        
        # Behaviour 10: Priority Management (Periodic)
        if self.config.get('enable_priority_management', True):
            self.add_behaviour(PriorityManagementBehaviour(period=10))
        
        self.logger.info("Coordinator Agent setup complete")
    
    def add_request(self, request_type: str, request_data: Dict, priority: Priority = Priority.NORMAL):
        """Add a new request to pending queue"""
        request = {
            'type': request_type,
            'data': request_data,
            'priority': priority,
            'timestamp': datetime.now(),
            'attempts': 0
        }
        self.pending_requests.append(request)
        self.logger.info(f"Added {request_type} request: {request_data}")
    
    def get_available_workers(self, task_type: TaskType) -> List[str]:
        """Get list of available workers for specific task type"""
        available = []
        for worker_id, is_available in self.worker_availability.items():
            if is_available and task_type.value in self.worker_competencies.get(worker_id, set()):
                available.append(worker_id)
        return available
    
    def select_worker(self, task_type: TaskType, available_workers: List[str]) -> Optional[str]:
        """Select worker based on assignment strategy"""
        if not available_workers:
            return None
        
        if self.assignment_strategy == 'round_robin':
            # Simple round-robin
            last_worker = self.last_assigned_worker.get(task_type)
            if last_worker in available_workers:
                idx = available_workers.index(last_worker)
                next_idx = (idx + 1) % len(available_workers)
                return available_workers[next_idx]
            return available_workers[0]
        
        elif self.assignment_strategy == 'least_loaded':
            # Assign to worker with least current load
            return min(available_workers, 
                      key=lambda w: self.worker_current_load.get(w, 0))
        
        elif self.assignment_strategy == 'priority':
            # Consider worker preferences
            # TODO: Implement preference-based selection
            return available_workers[0]
        
        return available_workers[0]
    
    def generate_task_id(self) -> str:
        """Generate unique task ID"""
        timestamp = datetime.now().timestamp()
        count = len(self.active_tasks) + len(self.completed_tasks)
        return f"task_{int(timestamp)}_{count}"
    
    def mark_task_complete(self, task_id: str, result: Dict):
        """Mark task as completed"""
        if task_id in self.active_tasks:
            task = self.active_tasks[task_id]
            task.status = TaskStatus.DONE
            task.completed_at = datetime.now()
            task.result = result
            
            self.completed_tasks.append(task)
            del self.active_tasks[task_id]
            
            # Update worker availability
            if task.assigned_to:
                self.worker_availability[task.assigned_to] = True
                self.worker_current_load[task.assigned_to] -= 1
            
            self.stats['total_tasks_completed'] += 1
            self.logger.info(f"Task {task_id} completed successfully")
    
    def get_statistics(self) -> Dict:
        """Get coordinator statistics"""
        return {
            **self.stats,
            'pending_requests': len(self.pending_requests),
            'active_tasks': len(self.active_tasks),
            'completed_tasks': len(self.completed_tasks),
            'failed_tasks': len(self.failed_tasks),
            'available_workers': sum(1 for av in self.worker_availability.values() if av)
        }
```

**Opis:** Agent Coordinator - centralny koordynator systemu. Zarządza kolejkami requestów, dostępnością pracowników, przydziela zadania według wybranej strategii (round-robin, least-loaded, priority). Monitoruje wykonanie zadań, zbiera statystyki. Implementuje wszystkie protocoły komunikacyjne z dokumentacji (CleanRequest, FeedRequest, etc.).

---

### `agents/worker_agent.py`
```python
"""
Worker Agent - Base class for all worker types
Abstract base for Caretaker, Cleaner, and Veterinarian
"""

from typing import Dict, List, Optional, Set
from datetime import datetime, time as dt_time
from abc import ABC, abstractmethod

from agents.base_agent import BaseAgent
from models.task import Task, TaskStatus
from models.enums import WorkerRole


class WorkerAgent(BaseAgent, ABC):
    """
    Base Worker Agent
    Abstract base class for all worker types (Caretaker, Cleaner, Veterinarian)
    """
    
    def __init__(self, jid: str, password: str, config: Dict):
        super().__init__(jid, password, config)
        
        # Worker identity
        self.worker_id = config['worker_id']
        self.worker_name = config.get('name', self.worker_id)
        self.role = WorkerRole(config['role'])
        
        # Competencies and limits
        self.competencies: Set[str] = set(config.get('competencies', []))
        self.max_concurrent_tasks = config.get('max_concurrent_tasks', 2)
        
        # Availability
        self.availability_schedule = config.get('availability', {})
        self.is_available = True
        self.current_tasks: List[Task] = []
        
        # Preferences
        self.preferences = config.get('preferences', {})
        
        # Statistics
        self.tasks_completed = 0
        self.tasks_failed = 0
        self.total_work_time = 0.0
    
    def is_currently_available(self) -> bool:
        """Check if worker is currently available based on schedule and load"""
        # Check time-based availability
        now = datetime.now()
        day_name = now.strftime('%A').lower()
        
        if day_name not in self.availability_schedule:
            return False
        
        time_slots = self.availability_schedule[day_name]
        if not time_slots:
            return False
        
        current_time = now.time()
        for slot in time_slots:
            start_str, end_str = slot.split('-')
            start_time = dt_time.fromisoformat(start_str)
            end_time = dt_time.fromisoformat(end_str)
            
            if start_time <= current_time <= end_time:
                # Within working hours, check load
                return len(self.current_tasks) < self.max_concurrent_tasks
        
        return False
    
    def can_handle_task(self, task_type: str) -> bool:
        """Check if worker has competency for task type"""
        return task_type in self.competencies
    
    def add_task(self, task: Task):
        """Add task to current tasks"""
        if len(self.current_tasks) >= self.max_concurrent_tasks:
            self.logger.warning(f"Worker {self.worker_id} is at capacity")
            return False
        
        self.current_tasks.append(task)
        self.is_available = len(self.current_tasks) < self.max_concurrent_tasks
        return True
    
    def complete_task(self, task_id: str):
        """Mark task as completed and remove from current tasks"""
        self.current_tasks = [t for t in self.current_tasks if t.task_id != task_id]
        self.is_available = len(self.current_tasks) < self.max_concurrent_tasks
        self.tasks_completed += 1
    
    def get_current_load(self) -> int:
        """Get number of current tasks"""
        return len(self.current_tasks)
    
    @abstractmethod
    async def execute_task(self, task: Task) -> Dict:
        """Execute task - to be implemented by subclasses"""
        pass
    
    def get_statistics(self) -> Dict:
        """Get worker statistics"""
        return {
            'worker_id': self.worker_id,
            'role': self.role.value,
            'tasks_completed': self.tasks_completed,
            'tasks_failed': self.tasks_failed,
            'current_load': self.get_current_load(),
            'is_available': self.is_available,
            'total_work_time': self.total_work_time
        }
```

**Opis:** Abstrakcyjna klasa bazowa dla wszystkich pracowników. Implementuje wspólną logikę: sprawdzanie dostępności według harmonogramu, zarządzanie kompetencjami, śledzenie aktualnych zadań i statystyk. Metoda execute_task jest abstrakcyjna - każdy typ pracownika implementuje ją inaczej.

---

### `agents/caretaker_agent.py`
```python
"""
Caretaker Agent - Animal caretaker worker
Responsible for feeding and walking animals
"""

from typing import Dict
import asyncio

from spade.template import Template

from agents.worker_agent import WorkerAgent
from models.task import Task, TaskType
from behaviours.worker.receive_task_behaviour import ReceiveTaskBehaviour
from behaviours.worker.execute_task_behaviour import ExecuteTaskBehaviour
from behaviours.worker.update_availability_behaviour import UpdateAvailabilityBehaviour
from config.settings import Settings


class CaretakerAgent(WorkerAgent):
    """
    Caretaker Agent
    Worker responsible for:
    - Feeding animals
    - Walking animals
    - Basic animal care
    """
    
    async def setup(self):
        """Setup caretaker agent and behaviours"""
        await super().setup()
        
        self.logger.info(f"Setting up Caretaker Agent: {self.worker_name}")
        
        # Behaviour 1: Receive Feed Tasks
        feed_template = Template()
        feed_template.set_metadata("protocol", "AssignFeedTask")
        self.add_behaviour(ReceiveTaskBehaviour(), feed_template)
        
        # Behaviour 2: Receive Walk Tasks
        walk_template = Template()
        walk_template.set_metadata("protocol", "AssignWalkTask")
        self.add_behaviour(ReceiveTaskBehaviour(), walk_template)
        
        # Behaviour 3: Execute Tasks
        self.add_behaviour(ExecuteTaskBehaviour(period=2))
        
        # Behaviour 4: Update Availability
        update_interval = Settings.WORKER_AVAILABILITY_UPDATE_INTERVAL
        self.add_behaviour(UpdateAvailabilityBehaviour(period=update_interval))
        
        self.logger.info(f"Caretaker {self.worker_name} is ready")
    
    async def execute_task(self, task: Task) -> Dict:
        """
        Execute caretaker task
        
        Args:
            task: Task to execute
            
        Returns:
            Dict with execution results
        """
        self.logger.info(f"Caretaker {self.worker_id} executing {task.task_type.value} task {task.task_id}")
        
        start_time = asyncio.get_event_loop().time()
        
        if task.task_type == TaskType.FEED:
            result = await self._execute_feed_task(task)
        elif task.task_type == TaskType.WALK:
            result = await self._execute_walk_task(task)
        else:
            self.logger.error(f"Unknown task type: {task.task_type}")
            return {'success': False, 'error': 'Unknown task type'}
        
        end_time = asyncio.get_event_loop().time()
        execution_time = end_time - start_time
        self.total_work_time += execution_time
        
        result['execution_time'] = execution_time
        return result
    
    async def _execute_feed_task(self, task: Task) -> Dict:
        """Execute feeding task"""
        animal_id = task.parameters.get('animalId')
        
        self.logger.info(f"Feeding animal {animal_id}")
        
        # Simulate feeding
        await asyncio.sleep(Settings.FEED_TASK_DURATION)
        
        self.logger.info(f"Animal {animal_id} has been fed")
        
        return {
            'success': True,
            'animalId': animal_id,
            'newState': 'fed',
            'worker': self.worker_id,
            'timestamp': asyncio.get_event_loop().time()
        }
    
    async def _execute_walk_task(self, task: Task) -> Dict:
        """Execute walking task"""
        animal_id = task.parameters.get('animalId')
        
        self.logger.info(f"Walking animal {animal_id}")
        
        # Simulate walking
        await asyncio.sleep(Settings.WALK_TASK_DURATION)
        
        self.logger.info(f"Animal {animal_id} has been walked")
        
        return {
            'success': True,
            'animalId': animal_id,
            'newState': 'walked',
            'worker': self.worker_id,
            'timestamp': asyncio.get_event_loop().time()
        }
```

**Opis:** Agent Caretaker (Opiekun) dziedziczący po WorkerAgent. Obsługuje zadania karmienia i spacerów. Implementuje specyficzną logikę wykonania tych zadań z symulacją czasu trwania. Automatycznie aktualizuje swoją dostępność w Coordinatorze.

---

### `agents/cleaner_agent.py`
```python
"""
Cleaner Agent - Room cleaning worker
Responsible for cleaning and maintaining rooms
"""

from typing import Dict
import asyncio

from spade.template import Template

from agents.worker_agent import WorkerAgent
from models.task import Task, TaskType
from behaviours.worker.receive_task_behaviour import ReceiveTaskBehaviour
from behaviours.worker.execute_task_behaviour import ExecuteTaskBehaviour
from behaviours.worker.update_availability_behaviour import UpdateAvailabilityBehaviour
from config.settings import Settings


class CleanerAgent(WorkerAgent):
    """
    Cleaner Agent
    Worker responsible for:
    - Daily room cleaning
    - On-demand cleaning
    - Special cleaning procedures
    """
    
    async def setup(self):
        """Setup cleaner agent and behaviours"""
        await super().setup()
        
        self.logger.info(f"Setting up Cleaner Agent: {self.worker_name}")
        
        # Behaviour 1: Receive Clean Tasks
        clean_template = Template()
        clean_template.set_metadata("protocol", "AssignCleanTask")
        self.add_behaviour(ReceiveTaskBehaviour(), clean_template)
        
        # Behaviour 2: Execute Tasks
        self.add_behaviour(ExecuteTaskBehaviour(period=2))
        
        # Behaviour 3: Update Availability
        update_interval = Settings.WORKER_AVAILABILITY_UPDATE_INTERVAL
        self.add_behaviour(UpdateAvailabilityBehaviour(period=update_interval))
        
        self.logger.info(f"Cleaner {self.worker_name} is ready")
    
    async def execute_task(self, task: Task) -> Dict:
        """
        Execute cleaning task
        
        Args:
            task: Task to execute
            
        Returns:
            Dict with execution results
        """
        self.logger.info(f"Cleaner {self.worker_id} executing clean task {task.task_id}")
        
        start_time = asyncio.get_event_loop().time()
        
        result = await self._execute_clean_task(task)
        
        end_time = asyncio.get_event_loop().time()
        execution_time = end_time - start_time
        self.total_work_time += execution_time
        
        result['execution_time'] = execution_time
        return result
    
    async def _execute_clean_task(self, task: Task) -> Dict:
        """Execute room cleaning task"""
        room_id = task.parameters.get('roomId')
        special_cleaning = task.parameters.get('requiresSpecialCleaning', False)
        
        self.logger.info(f"Cleaning room {room_id}" + 
                        (" (special cleaning)" if special_cleaning else ""))
        
        # Simulate cleaning (longer for special cleaning)
        duration = Settings.CLEAN_TASK_DURATION
        if special_cleaning:
            duration *= 1.5
        
        await asyncio.sleep(duration)
        
        self.logger.info(f"Room {room_id} has been cleaned")
        
        return {
            'success': True,
            'roomId': room_id,
            'newState': 'clean',
            'specialCleaning': special_cleaning,
            'worker': self.worker_id,
            'timestamp': asyncio.get_event_loop().time()
        }
```

**Opis:** Agent Cleaner (Sprzątacz) odpowiedzialny za czyszczenie pomieszczeń. Obsługuje zarówno rutynowe sprzątanie jak i specjalne procedury czyszczenia (np. dla pomieszczeń medycznych). Symuluje dłuższy czas dla specjalnego czyszczenia.

---

### `agents/veterinarian_agent.py`
```python
"""
Veterinarian Agent - Veterinary medical worker
Responsible for animal health care and vaccinations
"""

from typing import Dict
import asyncio

from spade.template import Template

from agents.worker_agent import WorkerAgent
from models.task import Task, TaskType
from behaviours.worker.receive_task_behaviour import ReceiveTaskBehaviour
from behaviours.worker.execute_task_behaviour import ExecuteTaskBehaviour
from behaviours.worker.update_availability_behaviour import UpdateAvailabilityBehaviour
from config.settings import Settings


class VeterinarianAgent(WorkerAgent):
    """
    Veterinarian Agent
    Worker responsible for:
    - Vaccinations
    - Health checks
    - Initial checkups for new animals
    - Medical emergencies
    """
    
    def __init__(self, jid: str, password: str, config: Dict):
        super().__init__(jid, password, config)
        self.specializations = set(config.get('specializations', []))
        self.emergency_available = config.get('emergency_available', False)
    
    async def setup(self):
        """Setup veterinarian agent and behaviours"""
        await super().setup()
        
        self.logger.info(f"Setting up Veterinarian Agent: {self.worker_name}")
        
        # Behaviour 1: Receive Vaccination Tasks
        vacc_template = Template()
        vacc_template.set_metadata("protocol", "AssignVaccinationTask")
        self.add_behaviour(ReceiveTaskBehaviour(), vacc_template)
        
        # Behaviour 2: Receive Health Check Tasks
        health_template = Template()
        health_template.set_metadata("protocol", "HealthRequestTask")
        self.add_behaviour(ReceiveTaskBehaviour(), health_template)
        
        # Behaviour 3: Receive Initial Checkup Tasks
        checkup_template = Template()
        checkup_template.set_metadata("protocol", "AssignInitialCheckupTask")
        self.add_behaviour(ReceiveTaskBehaviour(), checkup_template)
        
        # Behaviour 4: Execute Tasks
        self.add_behaviour(ExecuteTaskBehaviour(period=2))
        
        # Behaviour 5: Update Availability
        update_interval = Settings.WORKER_AVAILABILITY_UPDATE_INTERVAL
        self.add_behaviour(UpdateAvailabilityBehaviour(period=update_interval))
        
        self.logger.info(f"Veterinarian {self.worker_name} is ready")
    
    async def execute_task(self, task: Task) -> Dict:
        """
        Execute veterinary task
        
        Args:
            task: Task to execute
            
        Returns:
            Dict with execution results
        """
        self.logger.info(f"Veterinarian {self.worker_id} executing {task.task_type.value} task {task.task_id}")
        
        start_time = asyncio.get_event_loop().time()
        
        if task.task_type == TaskType.VACCINATION:
            result = await self._execute_vaccination_task(task)
        elif task.task_type == TaskType.HEALTH_CHECK:
            result = await self._execute_health_check_task(task)
        elif task.task_type == TaskType.INITIAL_CHECKUP:
            result = await self._execute_initial_checkup_task(task)
        else:
            self.logger.error(f"Unknown task type: {task.task_type}")
            return {'success': False, 'error': 'Unknown task type'}
        
        end_time = asyncio.get_event_loop().time()
        execution_time = end_time - start_time
        self.total_work_time += execution_time
        
        result['execution_time'] = execution_time
        return result
    
    async def _execute_vaccination_task(self, task: Task) -> Dict:
        """Execute vaccination task"""
        animal_id = task.parameters.get('animalId')
        vaccination_type = task.parameters.get('vaccinationType', 'routine')
        
        self.logger.info(f"Vaccinating animal {animal_id} ({vaccination_type})")
        
        await asyncio.sleep(Settings.VACCINATION_TASK_DURATION)
        
        self.logger.info(f"Animal {animal_id} has been vaccinated")
        
        return {
            'success': True,
            'animalId': animal_id,
            'vaccinationType': vaccination_type,
            'vaccinated': True,
            'worker': self.worker_id,
            'timestamp': asyncio.get_event_loop().time()
        }
    
    async def _execute_health_check_task(self, task: Task) -> Dict:
        """Execute health check task"""
        animal_id = task.parameters.get('animalId')
        
        self.logger.info(f"Performing health check for animal {animal_id}")
        
        await asyncio.sleep(Settings.HEALTH_CHECK_DURATION)
        
        # Simulate health check result
        health_status = 'healthy'  # In real system, would be determined by examination
        
        self.logger.info(f"Health check complete for animal {animal_id}: {health_status}")
        
        return {
            'success': True,
            'animalId': animal_id,
            'healthStatus': health_status,
            'newState': 'healthy',
            'worker': self.worker_id,
            'timestamp': asyncio.get_event_loop().time()
        }
    
    async def _execute_initial_checkup_task(self, task: Task) -> Dict:
        """Execute initial checkup for new animal"""
        animal_id = task.parameters.get('animalId')
        
        self.logger.info(f"Performing initial checkup for new animal {animal_id}")
        
        await asyncio.sleep(Settings.INITIAL_CHECKUP_DURATION)
        
        # Comprehensive initial examination
        health_status = 'healthy'
        vaccinations_needed = task.parameters.get('vaccinationsNeeded', [])
        
        self.logger.info(f"Initial checkup complete for animal {animal_id}")
        
        return {
            'success': True,
            'animalId': animal_id,
            'healthStatus': health_status,
            'newState': 'healthy',
            'vaccinationsNeeded': vaccinations_needed,
            'clearForAdoption': health_status == 'healthy',
            'worker': self.worker_id,
            'timestamp': asyncio.get_event_loop().time()
        }
```

**Opis:** Agent Veterinarian (Weterynarz) obsługuje wszystkie zadania medyczne: szczepienia, kontrole zdrowia, badania wstępne nowych zwierząt. Ma specjalizacje i może być dostępny w trybie awaryjnym. Każdy typ zadania ma różny czas wykonania.

---

*Kontynuacja w następnej części ze względu na limit długości...*

Czy chcesz, żebym kontynuował z pozostałymi plikami (AnimalAssistantAgent, RoomAgent, ReceptionAgent, AdoptionAgent, ApplicantAgent, wszystkie behaviours, models, protocols, utils)?