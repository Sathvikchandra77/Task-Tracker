from flask import Flask, jsonify, request

app = Flask(__name__)
DB = {}

@app.get("/health")
def health():
    """Simple health-check endpoint."""
    return jsonify({"status": "ok"}), 200

@app.post("/tasks")
def create_task():
    """Add a new task by sending JSON like {"id": "1", "text": "Buy milk"}."""
    data = request.get_json() or {}
    if "id" not in data or "text" not in data:
        return jsonify({"error": "id and text required"}), 400
    DB[data["id"]] = {"id": data["id"], "text": data["text"]}
    return jsonify(DB[data["id"]]), 201

@app.get("/tasks")
def list_tasks():
    """List all tasks that have been created."""
    return jsonify(list(DB.values())), 200

if __name__ == "__main__":
    # Start the Flask server on http://127.0.0.1:8000
    app.run(host="0.0.0.0", port=8000)
