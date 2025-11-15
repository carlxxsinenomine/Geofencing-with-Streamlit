from flask import Flask, request, jsonify
from pymongo import MongoClient
from flask_cors import CORS
from dotenv import load_dotenv

from email_manager import EmailManager

import os

# RESTful API example
# @app.route('/articles', methods=['GET'])          # Get all articles
# @app.route('/articles', methods=['POST'])         # Create new article
# @app.route('/articles/<id>', methods=['GET'])     # Get specific article
# @app.route('/articles/<id>', methods=['PUT'])     # Update entire article
# @app.route('/articles/<id>', methods=['PATCH'])   # Update part of article
# @app.route('/articles/<id>', methods=['DELETE'])  # Delete article
load_dotenv()

app = Flask(__name__)
CORS(app)  # Enable CORS for browser requests

client = MongoClient(os.getenv("MONGODB_URI"))
geo_db = client[os.getenv("MONGODB_DATABASE")]
user_trail = geo_db[os.getenv("MONGODB_COLLECTION")]
event_log = geo_db[os.getenv("EVENT_LOG")]

@app.route('/save-tracking', methods=['POST'])
def save_tracking():
    data = request.json
    document = {
        "type": data['type'],
        "properties": data['properties'],
        "geometry": data['geometry']
    }
    result = user_trail.insert_one(document)
    return jsonify({"success": True, "id": str(result.inserted_id)})

@app.route('/log-alert-event', methods=['POST'])
def log_alert_event():
    email_manager = EmailManager()
    email_manager.create_message("Putanginamo Labas")
    email_manager.send_alert_email()

    data = request.json

    document = {
        "user_id": data['userId'],
        "time_stamp": data['timestamp']
    }
    result = event_log.insert_one(document)
    return jsonify({"success": True, "id": str(result)})


if __name__ == '__main__':
    app.run(port=int(os.getenv("API_PORT", 5000)))