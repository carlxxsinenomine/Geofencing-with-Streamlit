from flask import Flask, request, jsonify
from pymongo import MongoClient
from flask_cors import CORS
from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__)
CORS(app)  # Enable CORS for browser requests

client = MongoClient(os.getenv("MONGODB_URI"))
geo_db = client[os.getenv("MONGODB_DATABASE")]
user_trail = geo_db[os.getenv("MONGODB_COLLECTION")]

@app.route('/save-tracking', methods=['POST'])
def save_tracking():
    data = request.json
    document = {
        "path_coordinates": data['path_coordinates'],
        "timestamp": data['timestamp'],
        "user_id": data.get('user_id', 'anonymous')
    }
    result = user_trail.insert_one(document)
    return jsonify({"success": True, "id": str(result.inserted_id)})

if __name__ == '__main__':
    app.run(port=int(os.getenv("API_PORT", 5000)))