from flask import Flask, request, jsonify
import json
import os

app = Flask(__name__)

# Function to load recommendations data from recommendations.json
def load_recommendations():
    try:
        # Ensure correct file path (relative or absolute)
        file_path = os.path.join(os.getcwd(), 'recommendations.json')
        print(f"Loading recommendations from: {file_path}")  # Debugging log
        with open(file_path, 'r') as file:
            data = json.load(file)
            print("Loaded data:", data)  # Debugging log to check structure
            return data
    except FileNotFoundError:
        print("Error: recommendations.json file not found.")
        return None
    except json.JSONDecodeError as e:
        print(f"Error: Failed to decode JSON - {e}")
        return None
    except Exception as e:
        print(f"Unexpected error: {e}")
        return None

# Endpoint to get feed based on username, category, and mood
@app.route('/feed', methods=['GET'])
def get_feed():
    # Get the query parameters
    username = request.args.get('username')
    category_id = request.args.get('category_id')
    mood = request.args.get('mood')
    
    # Load the recommendations data
    recommendations_data = load_recommendations()
    
    if not username:
        return jsonify({"error": "Username is required"}), 400
    
    # Check if the recommendations data is loaded successfully
    if recommendations_data is None:
        return jsonify({"error": "Error loading recommendation data"}), 500

    # Check if the user exists in the recommendations data
    user_data = recommendations_data.get(username, None)
    
    if not user_data:
        return jsonify({"error": f"User {username} not found in recommendations data"}), 404
    
    # Prepare the response with post IDs
    response_data = {
        "user_id": username,
        "recommendations": user_data
    }
    
    # If category_id and mood are provided, add them to the response
    if category_id and mood:
        response_data["category_id"] = category_id
        response_data["mood"] = mood
    
    return jsonify(response_data), 200

if __name__ == '__main__':
    # Run Flask app with debugging enabled
    app.run(debug=True, port=5000)
