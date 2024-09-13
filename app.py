from flask import Flask, request, send_file, jsonify
import os
import uuid

app = Flask(__name__)


UPLOAD_FOLDER = './uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'pdf'}


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def find_file_by_id(file_id):
    for filename in os.listdir(UPLOAD_FOLDER):
        if filename.startswith(file_id):
            return os.path.join(UPLOAD_FOLDER, filename)
    return None

@app.route('/')
def index():
    return "Welcome to the Flask-based file management API"


@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        
        return jsonify({"error": "No file part in the request"}), 400

    file = request.files['file']
    
    if file.filename == '':
        return jsonify({"error": "No file selected"}), 400

    if file and allowed_file(file.filename):
        file_id = str(uuid.uuid4())
        file_extension = file.filename.rsplit('.', 1)[1].lower()
        filename = f"{file_id}.{file_extension}"
        file_path = os.path.join(UPLOAD_FOLDER, filename)
        
        file.save(file_path)
        return jsonify({"file_id": file_id}), 201

    return jsonify({"error": "File type not allowed"}), 400



@app.route('/download/<file_id>', methods=['GET'])
def download_file(file_id):
    file_path = find_file_by_id(file_id)
    if file_path is None:
        return jsonify({"error": "File not found"}), 404
    
    return send_file(file_path)


@app.route('/update/<file_id>', methods=['PUT'])
def update_file(file_id):
    if 'file' not in request.files:
        return jsonify({"error": "No file part in the request"}), 400

    new_file = request.files['file']

    if new_file.filename == '':
        return jsonify({"error": "No file selected"}), 400

    if new_file and allowed_file(new_file.filename):
        file_path = find_file_by_id(file_id)
        if file_path is None:
            return jsonify({"error": "File not found"}), 404

        os.remove(file_path)  

        new_file_extension = new_file.filename.rsplit('.', 1)[1].lower()
        new_file_path = os.path.join(UPLOAD_FOLDER, f"{file_id}.{new_file_extension}")
        new_file.save(new_file_path)

        return jsonify({"message": "File updated successfully"}), 200

    return jsonify({"error": "File type not allowed"}), 400


@app.route('/delete/<file_id>', methods=['DELETE'])
def delete_file(file_id):
    file_path = find_file_by_id(file_id)
    if file_path is None:
        return jsonify({"error": "File not found"}), 404
    
    os.remove(file_path)
    return jsonify({"message": "File deleted successfully"}), 200


@app.errorhandler(405)
def method_not_allowed(error):
    return jsonify({"error": "Method not allowed"}), 405


@app.errorhandler(Exception)
def handle_exception(error):
    return jsonify({"error": str(error)}), 500

if __name__ == '__main__':
    app.run(debug=True)
