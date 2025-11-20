from flask import Flask, request, jsonify
from pymongo import MongoClient
from flask_cors import CORS
from dotenv import load_dotenv

from handlers.email_handler import EmailManager
from handlers.weather_handler import WeatherHandler

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
weather_info = WeatherHandler()

CORS(app)  # Enable CORS for browser requests

client = MongoClient(os.getenv("MONGODB_URI"))
geo_db = client[os.getenv("MONGODB_DATABASE")]
user_trail = geo_db[os.getenv("MONGODB_COLLECTION")]
event_log = geo_db[os.getenv("EVENT_LOG")]
drawn_shapes = geo_db.shapes

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


def check_weather_advisory(lat, lng):
    coordinates_info = weather_info.get_coordinates_info(lat=lat, long=lng)
    coordinates_info = coordinates_info.get("name", None)

    panahon_data = weather_info.get_panahon_advisory(coordinates_info)

    data = [advisory for key, advisory in panahon_data.items() if advisory]
    if len(data) > 0:
        return data
    return None

# Hourly threshold:
# Yellow warning: 7.5 mm to 15 mm in one hour.
# Orange warning: 15 mm to 30 mm in one hour.
# Red warning: More than 30 mm in one hour.
# https://water.usgs.gov/edu/activity-howmuchrain-metric.html#:~:text=Slight%20rain:%20Less%20than%200.5,than%2050%20mm%20per%20hour.
def check_precipitation():
    pass

def fence_activation():
    # Iterate through all documents in the shapes collection
    for document in drawn_shapes.find():
        try:
            # Extract the first coordinate point from the geometry
            coordinates = document.get('geometry', {}).get('coordinates', [])

            if coordinates and len(coordinates) > 0:
                # Get the first polygon (index 0)
                polygon = coordinates[0]
                if polygon and len(polygon) > 0:
                    # Get the first coordinate point (longitude, latitude)
                    first_coordinate = polygon[0]
                    if first_coordinate and len(first_coordinate) >= 2:
                        lng = first_coordinate[0]  # longitude
                        lat = first_coordinate[1]  # latitude

                        print(f"Checking shape {document.get('_id')} at coordinates: {lat}, {lng}")

                        # Check for weather advisory
                        advisory = check_weather_advisory(lat, lng)

                        # Update is_active inside properties based on advisory
                        if advisory:
                            # Activate fence if advisory exists
                            drawn_shapes.update_one(
                                {'_id': document['_id']},
                                {'$set': {'properties.is_active': True}}
                            )
                            print(f"✓ Activated fence {document.get('_id')} - Advisory found")
                        else:
                            # Deactivate fence if no advisory
                            drawn_shapes.update_one(
                                {'_id': document['_id']},
                                {'$set': {'properties.is_active': False}}
                            )
                            print(f"✗ Deactivated fence {document.get('_id')} - No advisory")

        except Exception as e:
            print(f"Error processing document {document.get('_id')}: {str(e)}")
            continue

    client.close()
    print("Fence activation process completed!")
fence_activation()
if __name__ == '__main__':
    app.run(port=int(os.getenv("API_PORT", 5000)))