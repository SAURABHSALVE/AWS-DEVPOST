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

# Load environment variables from .env file
load_dotenv()

# --- Corrected Path Logic ---
backend_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(backend_dir)
template_folder = os.path.join(project_root, 'templates')
static_folder = os.path.join(project_root, 'static')

app = Flask(__name__, template_folder=template_folder, static_folder=static_folder)
CORS(app)  # Enable CORS for all routes

# Get the API Gateway URL from the .env file
API_GATEWAY_URL = os.getenv("API_GATEWAY_URL")

@app.route('/')
def index():
    """Renders the main single-page HTML application."""
    return render_template('index.html')

@app.route('/generate-blog', methods=['POST'])
def generate_blog():
    """Handles blog generation, either by calling API Gateway or returning a mock response."""
    data = request.get_json()
    if not data or not data.get("topic"):
        return jsonify({"error": "Missing 'topic' in request body"}), 400

    # Prepare the payload for the Lambda function or mock response
    payload = {
        "topic": data.get("topic"),
        "audience": data.get("audience", "general"),
        "tone": data.get("tone", "professional"),
        "languages": [data.get("language", "en")]
    }
    print(f"Received request: {payload}")  # Debug log

    # If API_GATEWAY_URL is set, forward the request to AWS API Gateway
    if API_GATEWAY_URL:
        try:
            headers = {'Content-Type': 'application/json'}
            response = requests.post(API_GATEWAY_URL, data=json.dumps(payload), headers=headers, timeout=60)
            response.raise_for_status()  # Raise an exception for HTTP errors
            api_response = response.json()
            print(f"API Gateway response: {api_response}")  # Debug log
            # Ensure the response has the expected structure
            results = api_response.get("results", {})
            if not results:
                return jsonify({"error": "No results returned from API Gateway"}), 500
            return jsonify({"results": results}), 200
        except requests.exceptions.RequestException as e:
            error_message = f"Error calling API Gateway: {str(e)}"
            print(error_message)
            return jsonify({"error": error_message}), 500
    else:
        # Return a mock response for local testing, matching AWS structure
        lang = data.get("language", "en")
        topic = data.get("topic", "test")
        blog_id = f"{topic.replace(' ', '-')}-{lang}"
        mock_content = (
            f"Discover our revolutionary AI writing tool, designed to craft compelling content effortlessly. "
            f"With advanced natural language processing, it adapts to your desired tone—{data.get('tone', 'professional')}—"
            f"and creates engaging text for any audience, from {data.get('audience', 'general')} readers to niche markets. "
            f"Perfect for blogs, marketing, and more, this tool streamlines your workflow and elevates your content game."
        )
        mock_response = {
            "results": {
                lang: {
                    "blogId": f"{blog_id}-{lang}",
                    "s3_key": f"{lang}/{blog_id}.html",
                    "content": mock_content
                }
            }
        }
        print(f"Mock response: {mock_response}")  # Debug log
        return jsonify(mock_response), 200

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)