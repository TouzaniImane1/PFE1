from flask import Flask, render_template, request, jsonify
from service.transcribe_service import handle_transcribe
import os
import webbrowser
from executors.command_executor import command_map

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/transcribe", methods=["POST"])
def transcribe():
    if "audio" not in request.files:
        return jsonify({"error": "No audio file provided"}), 400
    
    try:
        audio_file = request.files["audio"]

        result = handle_transcribe(audio_file)
        
        text = result.get("text", "").strip().lower()

        command_executor = command_map.get(text)
        if command_executor:
            execution_result = command_executor.execute()
            return jsonify({"text": text, "status": execution_result})
        else:
            return jsonify({"text": text, "status": "Commande non reconnue"})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=9000, debug=True)
