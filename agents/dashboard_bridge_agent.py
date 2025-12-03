from typing import Dict
from flask import Flask, request, jsonify
import threading
import logging

from agents.base_agent import BaseAgent
from config.settings import Settings


class DashboardBridgeAgent(BaseAgent):

    def __init__(self, jid: str, password: str, config: Dict):
        super().__init__(jid, password, config)
        self.http_port = config.get('http_port', 5001)
        self.flask_app = None
        self.http_thread = None
        self.agent_loop = None  # Store the agent's event loop

    async def setup(self):
        await super().setup()

        self.logger.info(f"Setting up Dashboard Bridge Agent on HTTP port {self.http_port}")

        # Store the agent's event loop for use in Flask handlers
        import asyncio
        self.agent_loop = asyncio.get_event_loop()

        # Start HTTP server in separate thread
        self._start_http_server()

        self.logger.info("Dashboard Bridge Agent is ready")

    def _start_http_server(self):
        self.flask_app = Flask(__name__)

        # Register new animal endpoint
        @self.flask_app.route('/register_animal', methods=['POST'])
        def register_animal():
            try:
                data = request.get_json()
                self.logger.info(f"Received registration request: {data}")

                # Queue the SPADE message to be sent asynchronously (don't wait)
                import asyncio
                asyncio.run_coroutine_threadsafe(
                    self._send_registration_request(data),
                    self.agent_loop
                )

                # Return immediately without waiting for SPADE message to be sent
                return jsonify({
                    'status': 'success',
                    'message': f"Registration request sent for {data.get('name')}"
                }), 200

            except Exception as e:
                self.logger.error(f"Error processing registration: {e}")
                return jsonify({
                    'status': 'error',
                    'message': str(e)
                }), 500

        # Animal care endpoint
        @self.flask_app.route('/animal_care', methods=['POST'])
        def animal_care():
            try:
                data = request.get_json()
                self.logger.info(f"Received animal care request: {data}")

                # Run the care request and wait for validation
                import asyncio
                import concurrent.futures

                future = asyncio.run_coroutine_threadsafe(
                    self._send_care_request(data),
                    self.agent_loop
                )

                # Wait for completion (with timeout) to catch validation errors
                try:
                    future.result(timeout=5)
                except concurrent.futures.TimeoutError:
                    self.logger.warning(f"Care request timed out for animal {data.get('animal_id')}")
                except Exception as e:
                    # This catches ValueError from adoption status check
                    raise e

                # Return success after validation passes
                return jsonify({
                    'status': 'success',
                    'message': f"{data.get('action').capitalize()} request sent for animal {data.get('animal_id')}"
                }), 200

            except Exception as e:
                self.logger.error(f"Error processing care request: {e}")
                return jsonify({
                    'status': 'error',
                    'message': str(e)
                }), 500

        # Adoption application endpoint
        @self.flask_app.route('/adoption', methods=['POST'])
        def adoption():
            try:
                data = request.get_json()
                self.logger.info(f"Received adoption request: {data}")

                # Queue the SPADE message to be sent asynchronously (don't wait)
                import asyncio
                asyncio.run_coroutine_threadsafe(
                    self._send_adoption_request(data),
                    self.agent_loop
                )

                # Return immediately without waiting for SPADE message to be sent
                return jsonify({
                    'status': 'success',
                    'message': f"Adoption application sent for animal {data.get('animal_id')} by applicant {data.get('applicant_id')}"
                }), 200

            except Exception as e:
                self.logger.error(f"Error processing adoption request: {e}")
                return jsonify({
                    'status': 'error',
                    'message': str(e)
                }), 500

        # Start server in thread
        def run_server():
            self.flask_app.run(host='0.0.0.0', port=self.http_port, debug=False, use_reloader=False)

        self.http_thread = threading.Thread(target=run_server, daemon=True)
        self.http_thread.start()
        self.logger.info(f"HTTP bridge server started on port {self.http_port}")

    async def _send_registration_request(self, animal_data: Dict):
        reception_jid = Settings.get_reception_jid()

        await self.send_request(
            to=reception_jid,
            protocol='RegisterAnimalRequest',
            content=animal_data
        )

        self.logger.info(f"Sent registration request to {reception_jid}")

    async def _send_care_request(self, care_data: Dict):
        import requests as http_requests

        coordinator_jid = Settings.get_coordinator_jid()
        animal_id = care_data.get('animal_id')
        action = care_data.get('action')

        # Check if animal is adopted by querying the dashboard API
        try:
            dashboard_url = 'http://localhost:5000/api/control/animals'
            response = http_requests.get(dashboard_url, timeout=5)
            if response.status_code == 200:
                animals = response.json()
                # Find the animal
                animal = next((a for a in animals if a.get('id') == animal_id), None)
                if animal:
                    adoption_status = animal.get('adoption_status', 'available')
                    if adoption_status == 'adopted':
                        self.logger.warning(f"Rejecting care request for adopted animal {animal_id}")
                        raise ValueError(f"Cannot perform care actions on adopted animal {animal_id}")
        except http_requests.exceptions.RequestException as e:
            self.logger.warning(f"Could not verify animal adoption status: {e}")
            # Continue anyway - let the animal agent handle it

        # Map action to protocol
        protocol_map = {
            'feed': 'FeedRequest',
            'walk': 'WalkRequest',
            'checkup': 'HealthRequest',
            'vaccination': 'VaccinationRequest'
        }

        protocol = protocol_map.get(action)
        if not protocol:
            raise ValueError(f"Unknown action: {action}")

        # Prepare request content
        content = {
            'animalId': animal_id,
            'requestedBy': 'dashboard',
            'priority': 'normal'
        }

        await self.send_request(
            to=coordinator_jid,
            protocol=protocol,
            content=content
        )

        self.logger.info(f"Sent {action} request for animal {animal_id} to {coordinator_jid}")

    async def _send_adoption_request(self, adoption_data: Dict):
        animal_id = adoption_data.get('animal_id')
        applicant_id = adoption_data.get('applicant_id')

        # Build the applicant agent JID
        applicant_jid = f"applicant_{applicant_id}@{Settings.XMPP_SERVER}"

        # Send trigger message to applicant agent to submit adoption application
        # The applicant agent will then communicate with the coordinator
        trigger_data = {
            'animal_id': animal_id,
            'triggered_by': 'dashboard',
            'trigger_source': 'user_action'
        }

        await self.send_request(
            to=applicant_jid,
            protocol='TriggerAdoptionApplication',
            content=trigger_data
        )

        self.logger.info(
            f"Triggered applicant {applicant_id} to submit adoption application for animal {animal_id}"
        )
