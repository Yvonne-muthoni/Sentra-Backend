import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from extensions import db
from models import ContactMessage

app = Flask(__name__)
CORS(app)

# Absolute path to the database
basedir = os.path.abspath(os.path.dirname(__file__))
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + os.path.join(basedir, "instance", "sentra.db")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Initialize the database with the app
db.init_app(app)

with app.app_context():
    db.create_all()

# Basic test route
@app.route('/api/health', methods=['GET'])
def health():
    return jsonify({'status': 'Backend is running!'}), 200

# Contact form endpoint
@app.route('/contact', methods=['POST', 'OPTIONS'])
def contact():
    if request.method == 'OPTIONS':
        return '', 200
    
    try:
        data = request.get_json()
        
        # Validate required fields
        if not data or not all(key in data for key in ['name', 'email', 'message']):
            return jsonify({'error': 'Missing required fields: name, email, message'}), 400
        
        # Create new contact message
        contact_msg = ContactMessage(
            name=data['name'],
            email=data['email'],
            message=data['message']
        )
        
        # Save to database
        db.session.add(contact_msg)
        db.session.commit()
        
        return jsonify({'success': 'Message sent successfully!'}), 200
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Server error: {str(e)}'}), 500

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5000)
