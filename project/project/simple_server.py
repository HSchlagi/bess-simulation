from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Einfache In-Memory-Datenbank für Kunden
customers = []
next_id = 1

@app.route('/api/customers', methods=['POST'])
def create_customer():
    global next_id
    try:
        data = request.get_json()
        print(f"Received data: {data}")
        
        if not data or not data.get('name'):
            return jsonify({'error': 'Name ist erforderlich'}), 400
        
        customer = {
            'id': next_id,
            'name': data['name'].strip(),
            'company': data.get('company', '').strip() or None,
            'contact': data.get('contact', '').strip() or None
        }
        
        customers.append(customer)
        next_id += 1
        
        print(f"Customer created: {customer}")
        return jsonify({'success': True, 'id': customer['id']}), 201
        
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({'error': str(e)}), 400

@app.route('/api/customers', methods=['GET'])
def get_customers():
    return jsonify(customers)

@app.route('/')
def index():
    return "BESS Simulation Server läuft!"

if __name__ == '__main__':
    print("Starting simple BESS server...")
    app.run(debug=True, host='127.0.0.1', port=5000) 