from flask import Flask, render_template, jsonify, request, make_response
from flask_socketio import SocketIO, emit
from flask_cors import CORS
import threading
import time
import logging
from datetime import datetime

from visualization.message_tracker import tracker

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create Flask app
app = Flask(__name__, 
            template_folder='templates',
            static_folder='static')
app.config['SECRET_KEY'] = 'shelter_mas_visualization_secret'
CORS(app)

# Initialize Socket.IO
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')


# Message callback for real-time updates
def message_callback(message):
    try:
        print("====================Emitting new message", message)
        socketio.emit('new_message', message, namespace='/')
    except Exception as e:
        logger.error(f"Error emitting message: {e}")


# Routes
@app.route('/')
def index():
    response = make_response(render_template('dashboard_v2.html'))
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response


@app.route('/debug')
def debug():
    return render_template('debug.html')


@app.route('/simple')
def simple():
    return render_template('simple.html')


@app.route('/favicon.ico')
def favicon():
    return '', 204  # No content


@app.route('/api/agents')
def get_agents():
    return jsonify(tracker.get_agents())


@app.route('/api/messages')
def get_messages():
    limit = int(request.args.get('limit', 50))
    return jsonify(tracker.get_recent_messages(limit))


@app.route('/api/statistics')
def get_statistics():
    return jsonify(tracker.get_statistics())


@app.route('/api/connections')
def get_connections():
    return jsonify(tracker.get_agent_connections())


@app.route('/api/health')
def health():
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'uptime': (datetime.now() - tracker.start_time).total_seconds()
    })


@app.route('/api/track_agent', methods=['POST'])
def track_agent():
    try:
        data = request.get_json()
        tracker.register_agent(
            jid=data.get('jid'),
            role=data.get('role'),
            metadata=data.get('metadata', {})
        )
        return jsonify({'status': 'success'}), 200
    except Exception as e:
        logger.error(f"Error tracking agent: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500


@app.route('/api/track_message', methods=['POST'])
def track_message():
    try:
        data = request.get_json()
        message = tracker.track_message(
            from_jid=data.get('from_jid'),
            to_jid=data.get('to_jid'),
            content=data.get('content', {}),
            metadata=data.get('metadata', {})
        )
        return jsonify({'status': 'success', 'message_id': message['id']}), 200
    except Exception as e:
        logger.error(f"Error tracking message: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500


# ========== INTERACTIVE CONTROL API ENDPOINTS ==========

@app.route('/api/control/animals')
def get_control_animals():
    try:
        animals_list = []

        # Get all agents from tracker
        agents = tracker.get_agents()

        # Filter animal agents and extract their metadata
        for agent_name, agent_data in agents.items():
            jid = agent_data.get('jid', '')

            # Check if this is an animal agent (JID starts with "animal_")
            if jid.startswith('animal_'):
                metadata = agent_data.get('metadata', {})

                # Extract animal ID from JID (e.g., "animal_001@serverhello" -> "001")
                animal_id = jid.split('@')[0].replace('animal_', '')

                # Get adoption status
                adoption_status = metadata.get('adoption_status', 'available')

                # Only include available animals (filter out adopted ones)
                if adoption_status != 'adopted':
                    animal_entry = {
                        'id': animal_id,
                        'name': metadata.get('name', f'Animal {animal_id}'),
                        'species': metadata.get('species', 'unknown'),
                        'adoption_status': adoption_status
                    }
                    animals_list.append(animal_entry)

        # If no animals found in tracker, fall back to config file
        if not animals_list:
            import json
            import os
            config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config', 'animals.json')
            try:
                with open(config_path, 'r') as f:
                    data = json.load(f)
                    all_animals = data.get('animals', [])
                    # Filter out adopted animals from config too
                    animals_list = [a for a in all_animals if a.get('adoption_status') != 'adopted']
            except:
                pass

        return jsonify(animals_list)
    except Exception as e:
        logger.error(f"Error loading animals: {e}")
        return jsonify([])


@app.route('/api/control/rooms')
def get_control_rooms():
    try:
        import json
        import os
        config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config', 'rooms.json')
        with open(config_path, 'r') as f:
            data = json.load(f)
        return jsonify(data.get('rooms', []))
    except Exception as e:
        logger.error(f"Error loading rooms: {e}")
        return jsonify([])


@app.route('/api/control/applicants')
def get_control_applicants():
    try:
        import json
        import os
        config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config', 'applicants.json')
        with open(config_path, 'r') as f:
            data = json.load(f)
        return jsonify(data.get('applicants', []))
    except Exception as e:
        logger.error(f"Error loading applicants: {e}")
        return jsonify([])


@app.route('/api/trigger/register_animal', methods=['POST'])
def trigger_register_animal():
    try:
        data = request.get_json()
        name = data.get('name')
        species = data.get('species')

        if not name or not species:
            return jsonify({
                'status': 'error',
                'message': 'Name and species are required'
            }), 400

        # Prepare registration data
        registration_data = {
            'name': name,
            'species': species,
            'breed': data.get('breed', 'Unknown'),
            'age': data.get('age', 0),
            'sex': data.get('sex', 'unknown'),
            'dietary_requirements': data.get('dietary_requirements', 'standard'),
            'behavioral_notes': data.get('behavioral_notes', 'Registered via dashboard'),
        }

        # Forward to bridge agent
        import requests as http_requests
        import os
        # Try localhost first for local development, then container name
        bridge_host = os.getenv('BRIDGE_HOST', 'localhost')
        bridge_url = f'http://{bridge_host}:5001/register_animal'
        try:
            response = http_requests.post(bridge_url, json=registration_data, timeout=10)

            if response.status_code == 200:
                logger.info(f"Successfully sent registration request for {name} ({species})")
                return jsonify({
                    'status': 'success',
                    'message': f'Registration request sent for {name} the {species}. The animal will be processed and appear on the graph after initial checkup.'
                }), 200
            else:
                logger.error(f"Bridge agent returned error: {response.text}")
                return jsonify({
                    'status': 'error',
                    'message': f'Bridge agent error: {response.text}'
                }), 500

        except http_requests.exceptions.RequestException as e:
            logger.error(f"Failed to connect to bridge agent: {e}")
            return jsonify({
                'status': 'error',
                'message': 'Bridge agent is not running. Please ensure the dashboard_bridge agent is started.'
            }), 503

    except Exception as e:
        logger.error(f"Error triggering animal registration: {e}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


@app.route('/api/trigger/animal_care', methods=['POST'])
def trigger_animal_care():
    try:
        data = request.get_json()
        animal_id = data.get('animal_id')
        action = data.get('action')

        if not animal_id or not action:
            return jsonify({
                'status': 'error',
                'message': 'Animal ID and action are required'
            }), 400

        # Validate action
        valid_actions = ['feed', 'walk', 'checkup', 'vaccination']
        if action not in valid_actions:
            return jsonify({
                'status': 'error',
                'message': f'Invalid action. Must be one of: {", ".join(valid_actions)}'
            }), 400

        # Prepare care request data
        care_data = {
            'animal_id': animal_id,
            'action': action
        }

        # Forward to bridge agent
        import requests as http_requests
        import os
        # Try localhost first for local development, then container name
        bridge_host = os.getenv('BRIDGE_HOST', 'localhost')
        bridge_url = f'http://{bridge_host}:5001/animal_care'
        try:
            response = http_requests.post(bridge_url, json=care_data, timeout=10)

            if response.status_code == 200:
                action_names = {
                    'feed': 'feeding',
                    'walk': 'walking',
                    'checkup': 'health checkup',
                    'vaccination': 'vaccination'
                }
                logger.info(f"Successfully sent {action} request for animal {animal_id}")
                return jsonify({
                    'status': 'success',
                    'message': f'{action_names[action].capitalize()} request sent for animal {animal_id}. The coordinator will assign this task to an available worker.'
                }), 200
            else:
                logger.error(f"Bridge agent returned error: {response.text}")
                return jsonify({
                    'status': 'error',
                    'message': f'Bridge agent error: {response.text}'
                }), 500

        except http_requests.exceptions.RequestException as e:
            logger.error(f"Failed to connect to bridge agent: {e}")
            return jsonify({
                'status': 'error',
                'message': 'Bridge agent is not running. Please ensure the dashboard_bridge agent is started.'
            }), 503

    except Exception as e:
        logger.error(f"Error triggering animal care: {e}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


@app.route('/api/trigger/adoption', methods=['POST'])
def trigger_adoption():
    try:
        data = request.get_json()
        animal_id = data.get('animal_id')
        applicant_id = data.get('applicant_id')

        if not animal_id or not applicant_id:
            return jsonify({
                'status': 'error',
                'message': 'Animal ID and applicant ID are required'
            }), 400

        # Prepare adoption request data
        adoption_data = {
            'animal_id': animal_id,
            'applicant_id': applicant_id
        }

        # Forward to bridge agent
        import requests as http_requests
        import os
        # Try localhost first for local development, then container name
        bridge_host = os.getenv('BRIDGE_HOST', 'localhost')
        bridge_url = f'http://{bridge_host}:5001/adoption'
        try:
            response = http_requests.post(bridge_url, json=adoption_data, timeout=10)

            if response.status_code == 200:
                logger.info(f"Successfully sent adoption request for animal {animal_id} by applicant {applicant_id}")
                return jsonify({
                    'status': 'success',
                    'message': f'Adoption application submitted for animal {animal_id} by applicant {applicant_id}. The application will be processed by the adoption agent.'
                }), 200
            else:
                logger.error(f"Bridge agent returned error: {response.text}")
                return jsonify({
                    'status': 'error',
                    'message': f'Bridge agent error: {response.text}'
                }), 500

        except http_requests.exceptions.RequestException as e:
            logger.error(f"Failed to connect to bridge agent: {e}")
            return jsonify({
                'status': 'error',
                'message': 'Bridge agent is not running. Please ensure the dashboard_bridge agent is started.'
            }), 503

    except Exception as e:
        logger.error(f"Error triggering adoption: {e}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


# Socket.IO events
@socketio.on('connect')
def handle_connect():
    logger.info(f"Client connected")
    
    # Send initial data
    emit('init_data', {
        'agents': tracker.get_agents(),
        'messages': tracker.get_recent_messages(100),
        'statistics': tracker.get_statistics(),
        'connections': tracker.get_agent_connections()
    })


@socketio.on('disconnect')
def handle_disconnect():
    logger.info(f"Client disconnected")


@socketio.on('request_update')
def handle_request_update():
    emit('statistics_update', tracker.get_statistics())
    emit('connections_update', tracker.get_agent_connections())


# Background task to send periodic updates
def background_updates():
    while True:
        time.sleep(2)  # Update every 2 seconds
        try:
            socketio.emit('statistics_update', tracker.get_statistics())
            socketio.emit('agents_update', tracker.get_agents())
        except Exception as e:
            logger.error(f"Error in background updates: {e}")


def initialize_default_agents():
    logger.info("Registering default agents...")
    
    default_agents = [
        ('coordinator@localhost', 'coordinator', {'description': 'Main coordinator agent'}),
        ('reception@localhost', 'reception', {'description': 'Reception desk agent'}),
        ('adoption@localhost', 'adoption', {'description': 'Adoption processing agent'}),
        ('dashboard@localhost', 'dashboard', {'description': 'Dashboard control interface'})
    ]
    
    for jid, role, metadata in default_agents:
        tracker.register_agent(jid, role, metadata)
        logger.info(f"  ✓ Registered {role} agent")


def start_dashboard(host='0.0.0.0', port=5000, debug=False):
    logger.info(f"Starting dashboard server on {host}:{port}")
    
    # Register default agents
    initialize_default_agents()
    
    # Subscribe to message updates
    tracker.subscribe(message_callback)
    
    # Start background updates thread
    update_thread = threading.Thread(target=background_updates, daemon=True)
    update_thread.start()
    
    # Run the server
    socketio.run(app, host=host, port=port, debug=debug, allow_unsafe_werkzeug=True)


if __name__ == '__main__':
    start_dashboard(debug=True)
