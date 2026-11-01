from flask import Flask, request, jsonify
import os
from extractor import document_classifier
from logger import get_logger

logger = get_logger(__name__)
logger.info("Flask app initializing")

app = Flask(__name__)

@app.route('/summarize', methods = ['POST'])
def summarize():
    """
    Accepts a file upload, extracts and summarizes its content, returns JSON with topic, summary, and key_topics.
    """
    
    logger.info("POST/ summarize")

    if 'file' not in request.files:
        logger.warning("Request failed. No Files Received")
        return jsonify({"error":"No file upload"}), 400
    
    file = request.files['file']
    file_type = os.path.splitext(file.filename)[1].lower()
    logger.info(f"File Received | name='{file.filename}'")

    result = document_classifier(file_type,file)

    if isinstance(result, str):  # unsupported file type
        logger.warning("Unsupported File Request")
        return jsonify({"error": result}), 415
    
    logger.info(f"Summarization successful | topic='{result.topic}'")
    
    return jsonify({
        "topic": result.topic,
        "summary": result.summary,
        "key_topics": result.key_topics
    })



if __name__ == "__main__":
    logger.info("Starting Flask server on port 5000")
    app.run(port=5000, debug=True)