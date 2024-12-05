from google.cloud import firestore
from flask import Flask, request, jsonify
import firebase_admin
from firebase_admin import credentials

cred = credentials.Certificate(r'auth_key.json')
firebase_admin.initialize_app(cred)

app = Flask(__name__)
db = firestore.Client.from_service_account_json(
    r'auth_key.json') \

@app.route('/add_pin', methods=['POST'])
def add_pin():
    data = request.json
    lat = data.get("latitude")
    lng = data.get("longitude")
    name = data.get("name")
    rating = data.get("rating")
    comments = data.get("comments")

    pin_data = {
        "latitude": lat,
        "longitude": lng,
        "name": name,
        "rating": rating,
        "comments": comments
    }
    db.collection("locations").add(pin_data)

    return jsonify({"message": "Pin added successfully"}), 201


@app.route('/get_pins', methods=['GET'])
def get_pins():
    pins_ref = db.collection("locations")
    docs = pins_ref.stream()

    pins = []
    for doc in docs:
        pin = doc.to_dict()
        pin["id"] = doc.id
        pins.append(pin)

    return jsonify(pins), 200

@app.route('/edit_pin/<pin_id>', methods=['PUT'])
def edit_pin(pin_id):
    data = request.json
    lat = data.get("latitude")
    lng = data.get("longitude")
    name = data.get("name")
    rating = data.get("rating")
    comments = data.get("comments")

    pin_data = {
        "latitude": lat,
        "longitude": lng,
        "name": name,
        "rating": rating,
        "comments": comments
    }

    pin_ref = db.collection("locations").document(pin_id)
    pin_ref.update(pin_data)

    return jsonify({"message": f"Pin {pin_id} updated successfully"}), 200

@app.route('/remove_pin/<pin_id>', methods=['DELETE'])
def remove_pin(pin_id):
    pin_ref = db.collection("locations").document(pin_id)
    pin_ref.delete()

    return jsonify({"message": f"Pin {pin_id} deleted successfully"}), 200

if __name__ == '__main__':
    app.run(debug=True)
