
from datetime import datetime
from flask import Flask, render_template, request, jsonify
import hashlib
import json
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)

# File in which original hashes are stored
HASH_FILE = "file_hashes.json"

HISTORY_FILE = "history.json"

# Maximum upload size: 50 MB
app.config["MAX_CONTENT_LENGTH"] = 50 * 1024 * 1024


# Generate SHA-256 hash of uploaded file
def generate_hash(file):

    sha256 = hashlib.sha256()

    while True:
        chunk = file.read(4096)

        if not chunk:
            break

        sha256.update(chunk)

    return sha256.hexdigest()


# Load saved hashes
def load_hashes():

    if os.path.exists(HASH_FILE):
        try:
            with open(HASH_FILE, "r") as f:
                return json.load(f)
        except (json.JSONDecodeError, OSError):
            return {}

    return {}


# Save hashes
def save_hashes(hashes):

    with open(HASH_FILE, "w") as f:
        json.dump(hashes, f, indent=4)


# Load verification history
def load_history():

    if os.path.exists(HISTORY_FILE):

        try:
            with open(HISTORY_FILE, "r") as f:
                return json.load(f)

        except (json.JSONDecodeError, OSError):
            return []

    return []


# Save an activity in history
def record_history(filename, action, result):

    history = load_history()

    record = {
        "filename": filename,
        "action": action,
        "result": result,
        "date_time": datetime.now().strftime("%d-%m-%Y %I:%M:%S %p")
    }

    history.append(record)

    with open(HISTORY_FILE, "w") as f:
        json.dump(history, f, indent=4)

# Home page
@app.route("/")
def home():
    return render_template("index.html")


# Register a file
@app.route("/register", methods=["POST"])
def register_file():

    file = request.files.get("file")

    if not file or not file.filename:
        return jsonify({
            "status": "error",
            "message": "Please select a file first."
        }), 400

    filename = secure_filename(file.filename)

    if not filename:
        return jsonify({
            "status": "error",
            "message": "Invalid file name."
        }), 400

    file_hash = generate_hash(file)

    hashes = load_hashes()
    hashes[filename] = file_hash
    save_hashes(hashes)
    record_history(filename, "Register", "Registered")

    return jsonify({
        "status": "success",
        "message": "File registered successfully!",
        "filename": filename,
        "hash": file_hash
    })


# Verify a file
@app.route("/verify", methods=["POST"])
def verify_file():

    file = request.files.get("file")

    if not file or not file.filename:
        return jsonify({
            "status": "error",
            "message": "Please select a file first."
        }), 400

    filename = secure_filename(file.filename)

    if not filename:
        return jsonify({
            "status": "error",
            "message": "Invalid file name."
        }), 400

    hashes = load_hashes()

    if filename not in hashes:
        record_history(filename, "Verify", "Not Registered")
        return jsonify({
            "status": "error",
            "message": "This file is not registered. Register it first."
        }), 404

    current_hash = generate_hash(file)
    original_hash = hashes[filename]

    if current_hash == original_hash:
        record_history(filename, "Verify", "Unchanged")

        return jsonify({
            "status": "success",
            "message": "File is safe. No changes detected!",
            "filename": filename,
            "result": "Unchanged"
        })

    else:
        record_history(filename, "Verify", "Modified")

        return jsonify({

            "status": "modified",
            "message": "Warning! File has been modified.",
            "filename": filename,
            "result": "Modified"
        })


# Handle files larger than the upload limit
@app.errorhandler(413)
def file_too_large(error):
    return jsonify({
        "status": "error",
        "message": "File is too large. Maximum size is 50 MB."
    }), 413


# Display all registered files on dashboard
@app.route("/files", methods=["GET"])
def get_files():

    hashes = load_hashes()

    file_list = []

    for filename, file_hash in hashes.items():
        file_list.append({
            "filename": filename,
            "hash": file_hash
        })

    return jsonify({
        "total": len(file_list),
        "files": file_list
    })
# Display verification history
@app.route("/history", methods=["GET"])
def get_history():

    history = load_history()

    return jsonify({
        "total": len(history),
        "history": list(reversed(history))
    })
if __name__ == "__main__":
    app.run(debug=True)



   
   
        
       

    

   