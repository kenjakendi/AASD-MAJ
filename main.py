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
from agents.dashboard_bridge_agent import DashboardBridgeAgent

from config.settings import Settings
from utils.logger import setup_logger

# Global list to track active agents
active_agents: List = []
logger = None


def load_config(config_path: str) -> dict:
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
    jid = config.get('jid', f"coordinator@{Settings.XMPP_SERVER}")
    password = config.get('password', Settings.AGENT_PASSWORD)
    
    logger.info(f"Creating Coordinator Agent: {jid}")
    agent = CoordinatorAgent(jid, password, config)
    await agent.start_with_retry(max_retries=Settings.MAX_RETRIES)
    return agent


async def create_caretaker(config: dict) -> CaretakerAgent:
    jid = config['jid']
    password = config.get('password', Settings.AGENT_PASSWORD)
    
    logger.info(f"Creating Caretaker Agent: {jid}")
    agent = CaretakerAgent(jid, password, config)
    await agent.start_with_retry(max_retries=Settings.MAX_RETRIES)
    return agent


async def create_cleaner(config: dict) -> CleanerAgent:
    jid = config['jid']
    password = config.get('password', Settings.AGENT_PASSWORD)
    
    logger.info(f"Creating Cleaner Agent: {jid}")
    agent = CleanerAgent(jid, password, config)
    await agent.start_with_retry(max_retries=Settings.MAX_RETRIES)
    return agent


async def create_veterinarian(config: dict) -> VeterinarianAgent:
    jid = config['jid']
    password = config.get('password', Settings.AGENT_PASSWORD)
    
    logger.info(f"Creating Veterinarian Agent: {jid}")
    agent = VeterinarianAgent(jid, password, config)
    await agent.start_with_retry(max_retries=Settings.MAX_RETRIES)
    return agent


async def create_animal_assistants(config: dict) -> List[AnimalAssistantAgent]:
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
    jid = config.get('jid', f"reception@{Settings.XMPP_SERVER}")
    password = config.get('password', Settings.AGENT_PASSWORD)
    
    logger.info(f"Creating Reception Agent: {jid}")
    agent = ReceptionAgent(jid, password, config)
    await agent.start_with_retry(max_retries=Settings.MAX_RETRIES)
    return agent


async def create_adoption(config: dict) -> AdoptionAgent:
    jid = config.get('jid', f"adoption@{Settings.XMPP_SERVER}")
    password = config.get('password', Settings.AGENT_PASSWORD)
    
    logger.info(f"Creating Adoption Agent: {jid}")
    agent = AdoptionAgent(jid, password, config)
    await agent.start_with_retry(max_retries=Settings.MAX_RETRIES)
    return agent


async def create_applicants(config: dict) -> List[ApplicantAgent]:
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


async def create_dashboard_bridge(config: dict) -> DashboardBridgeAgent:
    jid = config.get('jid', f"dashboard_bridge@{Settings.XMPP_SERVER}")
    password = config.get('password', Settings.AGENT_PASSWORD)

    logger.info(f"Creating Dashboard Bridge Agent: {jid}")
    agent = DashboardBridgeAgent(jid, password, config)
    await agent.start_with_retry(max_retries=Settings.MAX_RETRIES)
    return agent


async def shutdown_agents():
    logger.info("Shutting down all agents...")
    for agent in active_agents:
        try:
            await agent.stop()
            logger.info(f"Agent {agent.jid} stopped successfully")
        except Exception as e:
            logger.error(f"Error stopping agent {agent.jid}: {e}")


def signal_handler(signum, frame):
    logger.info(f"Received signal {signum}, initiating shutdown...")
    asyncio.create_task(shutdown_agents())
    sys.exit(0)


async def main():
    global logger
    
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Animal Shelter Management System')
    parser.add_argument('--role', required=True,
                       choices=['coordinator', 'caretaker', 'cleaner', 'veterinarian',
                               'animal_assistant', 'room', 'reception', 'adoption', 'applicant', 'dashboard_bridge'],
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

        elif args.role == 'dashboard_bridge':
            agent = await create_dashboard_bridge(config)
            active_agents.append(agent)

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
