# import os
# import json
# from datetime import datetime
# from flask import Flask, request, jsonify, render_template
# from flask_cors import CORS
# from flask_sqlalchemy import SQLAlchemy
# from dotenv import load_dotenv

# # Load environment variables
# load_dotenv()

# USE_BEDROCK = os.getenv("USE_BEDROCK", "false").lower() in ("1", "true", "yes")
# AWS_REGION = os.getenv("AWS_REGION", "us-east-1")
# BEDROCK_MODEL_ID = os.getenv("BEDROCK_MODEL_ID", "amazon.titan-text-express-v1")

# # ✅ Fix path issue: templates and static are outside backend/
# BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
# TEMPLATES_DIR = os.path.join(BASE_DIR, "templates")
# STATIC_DIR = os.path.join(BASE_DIR, "static")

# app = Flask(__name__, template_folder=TEMPLATES_DIR, static_folder=STATIC_DIR)
# CORS(app)

# # Database setup
# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///gen_history.db'
# app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# app.config['SECRET_KEY'] = os.getenv("FLASK_SECRET_KEY", "dev-secret")
# db = SQLAlchemy(app)

# # Database Model
# class Generation(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     brief = db.Column(db.Text, nullable=False)
#     language = db.Column(db.String(64), nullable=False)
#     fmt = db.Column(db.String(64), nullable=False)
#     tone = db.Column(db.String(64), nullable=True)
#     result_text = db.Column(db.Text, nullable=False)
#     created_at = db.Column(db.DateTime, default=datetime.utcnow)

# with app.app_context():
#     db.create_all()

# # Optional: Bedrock integration
# if USE_BEDROCK:
#     import boto3
#     from botocore.exceptions import ClientError
#     bedrock_runtime = boto3.client("bedrock-runtime", region_name=AWS_REGION)

# def call_bedrock_generate(prompt_text: str):
#     native_request = {
#         "inputText": prompt_text,
#         "textGenerationConfig": {"maxTokenCount": 1024, "temperature": 0.6, "topP": 0.95}
#     }
#     request_body = json.dumps(native_request)
#     try:
#         resp = bedrock_runtime.invoke_model(modelId=BEDROCK_MODEL_ID, body=request_body)
#         raw = resp["body"].read()
#         model_response = json.loads(raw)
#         return model_response["results"][0].get("outputText", "") if "results" in model_response else json.dumps(model_response)
#     except Exception as e:
#         raise RuntimeError(f"Bedrock error: {e}")

# def mock_generate(prompt_text: str):
#     return f"[MOCK OUTPUT]\n\nGenerated cultural content for:\n{prompt_text}"

# # ===================== FRONTEND ROUTES =====================
# @app.route("/")
# def index():
#     return render_template("index.html")

# @app.route("/features")
# def features():
#     return render_template("features.html")

# @app.route("/create", methods=["GET", "POST"])
# def create():
#     if request.method == "POST":
#         brief = request.form.get("brief", "").strip()
#         language = request.form.get("language", "English")
#         fmt = request.form.get("format", "blog")
#         tone = request.form.get("tone", "neutral")
#         with_image = request.form.get("with_image") == "on"

#         if not brief:
#             return render_template("create.html", error="Brief is required")

#         # Prompt for LLM
#         prompt = f"Create a {fmt} in {language}, tone: {tone}.\nBrief: {brief}\nAdapt for cultural context."

#         try:
#             result_text = call_bedrock_generate(prompt) if USE_BEDROCK else mock_generate(prompt)
#         except Exception as e:
#             return render_template("create.html", error=str(e))

#         # Save to DB
#         g = Generation(brief=brief, language=language, fmt=fmt, tone=tone, result_text=result_text)
#         db.session.add(g)
#         db.session.commit()

#         return render_template("create.html", result=result_text)

#     return render_template("create.html")

# @app.route("/history")
# def history():
#     items = Generation.query.order_by(Generation.created_at.desc()).all()
#     return render_template("history.html", items=items)

# # ===================== API ROUTES =====================
# @app.route("/health")
# def health():
#     return jsonify({"status": "ok", "time": datetime.utcnow().isoformat()})

# @app.route("/api/status")
# def api_status():
#     return jsonify({"use_bedrock": USE_BEDROCK, "region": AWS_REGION})

# @app.route("/generate", methods=["POST"])
# def generate():
#     payload = request.get_json() or {}
#     brief = payload.get("brief", "").strip()
#     language = payload.get("language", "English")
#     fmt = payload.get("format", "blog")
#     tone = payload.get("tone", "neutral")

#     if not brief:
#         return jsonify({"error": "Missing 'brief'"}), 400

#     prompt = f"Create a {fmt} in {language}, tone: {tone}.\nBrief: {brief}"

#     try:
#         result_text = call_bedrock_generate(prompt) if USE_BEDROCK else mock_generate(prompt)
#     except Exception as e:
#         return jsonify({"error": str(e)}), 500

#     g = Generation(brief=brief, language=language, fmt=fmt, tone=tone, result_text=result_text)
#     db.session.add(g)
#     db.session.commit()

#     return jsonify({
#         "id": g.id,
#         "brief": brief,
#         "language": language,
#         "format": fmt,
#         "tone": tone,
#         "result_text": result_text,
#         "created_at": g.created_at.isoformat()
#     })

# # ===================== MAIN =====================
# if __name__ == "__main__":
#     app.run(host="0.0.0.0", port=5000, debug=True)





import os
import json
import requests
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from dotenv import load_dotenv
from datetime import datetime
import uuid
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables from .env file
load_dotenv()

# --- Corrected Path Logic ---
backend_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(backend_dir)
template_folder = os.path.join(project_root, 'templates')
static_folder = os.path.join(project_root, 'static')

app = Flask(__name__, template_folder=template_folder, static_folder=static_folder)
CORS(app, resources={r"/*": {"origins": "*"}})  # Enable CORS for all routes and origins

# Get the API Gateway URL from the .env file
API_GATEWAY_URL = os.getenv("API_GATEWAY_URL")

# In-memory history store (simulating a database)
history_store = []

# Log all incoming requests for debugging
@app.before_request
def log_request_info():
    logger.info(f"Incoming request: {request.method} {request.path} from {request.remote_addr}")

@app.route('/')
def index():
    """Renders the main single-page HTML application."""
    logger.info("Serving index.html")
    return render_template('index.html')

@app.route('/generate-blog', methods=['POST'])
def generate_blog():
    """Handles blog generation by calling the API Gateway and stores the result in history."""
    data = request.get_json()
    if not data or not data.get("topic"):
        logger.error("Missing 'topic' in request body")
        return jsonify({"error": "Missing 'topic' in request body"}), 400
    if not data.get("language"):
        logger.error("A language must be selected")
        return jsonify({"error": "A language must be selected"}), 400

    # Validate advanced settings
    try:
        tone_intensity = int(data.get("tone_intensity", 5))
        if not (1 <= tone_intensity <= 10):
            logger.error("Invalid tone intensity: %s", tone_intensity)
            return jsonify({"error": "Tone intensity must be between 1 and 10"}), 400

        word_count = int(data.get("word_count", 500))
        if not (200 <= word_count <= 2000):
            logger.error("Invalid word count: %s", word_count)
            return jsonify({"error": "Word count must be between 200 and 2000"}), 400
    except ValueError as e:
        logger.error("Invalid numeric input: %s", str(e))
        return jsonify({"error": "Tone intensity and word count must be valid numbers"}), 400

    keywords = data.get("keywords", "").split(",") if data.get("keywords") else []
    keywords = [k.strip() for k in keywords if k.strip()]  # Remove empty or whitespace-only keywords
    if len(keywords) > 5:
        logger.error("Too many keywords: %s", len(keywords))
        return jsonify({"error": "Maximum 5 keywords allowed"}), 400

    if not API_GATEWAY_URL:
        logger.error("API Gateway URL not configured")
        return jsonify({"error": "API Gateway URL not configured"}), 500

    # Prepare the payload for the Lambda function
    payload = {
        "topic": data.get("topic"),
        "audience": data.get("audience", "general"),
        "tone": data.get("tone", "professional"),
        "tone_intensity": tone_intensity,
        "word_count": word_count,
        "keywords": keywords,
        "language": data.get("language", "en")
    }
    logger.info("Received request: %s", payload)

    # Forward the request to AWS API Gateway
    try:
        headers = {'Content-Type': 'application/json'}
        response = requests.post(API_GATEWAY_URL, data=json.dumps(payload), headers=headers, timeout=60)
        response.raise_for_status()  # Raise an exception for HTTP errors
        api_response = response.json()
        logger.info("API Gateway response: %s", api_response)

        # Validate response structure
        results = api_response.get("results", {})
        if not results:
            logger.error("No results returned from API Gateway")
            return jsonify({"error": "No results returned from API Gateway"}), 500

        lang = payload["language"]
        if lang not in results:
            logger.error("No content generated for language: %s", lang)
            return jsonify({"error": f"No content generated for language: {lang}"}), 500
        if not results[lang].get("content") and not results[lang].get("s3_key"):
            logger.error("No content or S3 key provided for language: %s", lang)
            return jsonify({"error": f"No content or S3 key provided for language: {lang}"}), 500

        # Store the generated content in history_store
        result = results[lang]
        history_item = {
            "id": str(uuid.uuid4()),  # Unique ID for the history item
            "brief": payload["topic"][:50],  # Truncated to match frontend display
            "language": lang,
            "tone": payload["tone"],
            "audience": payload["audience"],
            "version": f"v{len([h for h in history_store if h['brief'] == payload['topic'][:50]]) + 1}.0",
            "result_text": result.get("content", ""),
            "summary_text": result.get("summary", "Summary not provided"),
            "preview_text": result.get("content", "")[:100] + "..." if result.get("content") else "No preview available",
            "quality_score": float(result.get("quality_score", 80.0)),  # Ensure float for JSON serialization
            "created_at": datetime.utcnow().isoformat() + "Z"
        }
        history_store.append(history_item)
        logger.info("Stored history item: %s", history_item)

        response = jsonify({"results": results})
        response.headers["X-Response-Source"] = "generate-blog"
        return response, 200
    except requests.exceptions.RequestException as e:
        error_message = f"Error calling API Gateway: {str(e)}"
        logger.error(error_message)
        return jsonify({"error": error_message}), 500
    except Exception as e:
        error_message = f"Unexpected error in generate-blog: {str(e)}"
        logger.error(error_message)
        return jsonify({"error": error_message}), 500

@app.route('/history', methods=['GET'])
def get_history():
    """Returns the list of stored history items."""
    try:
        # Ensure history_store is JSON-serializable
        for item in history_store:
            if not isinstance(item["quality_score"], (int, float)):
                item["quality_score"] = float(item["quality_score"])
            if not isinstance(item["created_at"], str):
                item["created_at"] = item["created_at"].isoformat() + "Z"

        logger.info("Returning %d history items", len(history_store))
        response = jsonify(history_store)
        response.headers["X-History-Count"] = len(history_store)
        response.headers["X-Server-Time"] = datetime.utcnow().isoformat() + "Z"
        response.headers["X-Response-Source"] = "history"
        return response, 200
    except Exception as e:
        error_message = f"Error retrieving history: {str(e)}"
        logger.error(error_message)
        response = jsonify({"error": error_message})
        response.headers["X-Error-Details"] = str(e)
        response.headers["X-Response-Source"] = "history-error"
        return response, 500

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)
