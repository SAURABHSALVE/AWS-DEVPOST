# import os
# import json
# import requests
# from datetime import datetime
# import uuid
# import logging
# from flask import Flask, request, jsonify, render_template, session
# from flask_cors import CORS
# from dotenv import load_dotenv
# import boto3
# from botocore.exceptions import ClientError, NoCredentialsError, PartialCredentialsError
# import bcrypt
# from dynamodb_json import json_util as dynamodb_json
# from datetime import timezone

# # Configure logging
# logging.basicConfig(level=logging.INFO)
# logger = logging.getLogger(__name__)

# # Load environment variables from .env file
# load_dotenv()

# # --- Corrected Path Logic ---
# backend_dir = os.path.dirname(os.path.abspath(__file__))
# project_root = os.path.dirname(backend_dir)
# template_folder = os.path.join(project_root, 'templates')
# static_folder = os.path.join(project_root, 'static')

# app = Flask(__name__, template_folder=template_folder, static_folder=static_folder)
# app.secret_key = os.getenv('SECRET_KEY', 'your-default-secret-key-change-this')
# CORS(app, resources={r"/*": {"origins": "*"}})

# # Get Config from .env
# API_GATEWAY_URL = os.getenv("API_GATEWAY_URL")
# AWS_REGION = os.getenv("AWS_REGION", "us-east-1")
# DYNAMODB_BLOGS_TABLE_NAME = os.getenv("DYNAMODB_TABLE_NAME", "blogs")
# S3_BUCKET = os.getenv("S3_BUCKET", "agentx-blog")

# # --- AWS Clients Initialization ---
# try:
#     s3_client = boto3.client('s3', region_name=AWS_REGION)
#     logger.info(f"S3 Client initialized for region {AWS_REGION}.")
#     dynamodb = boto3.resource('dynamodb', region_name=AWS_REGION)
#     blogs_table = dynamodb.Table(DYNAMODB_BLOGS_TABLE_NAME)
#     blogs_table.load()
#     logger.info(f"Successfully connected to DynamoDB blogs table: {DYNAMODB_BLOGS_TABLE_NAME}")
# except (NoCredentialsError, PartialCredentialsError):
#     logger.error("AWS credentials not found. Using in-memory fallback.")
#     s3_client = None
#     dynamodb = None
#     blogs_table = None
# except ClientError as e:
#     logger.error(f"Error connecting to AWS services: {e.response['Error']['Message']}")
#     s3_client = None
#     dynamodb = None
#     blogs_table = None
# except Exception as e:
#     logger.error(f"Unexpected error during AWS initialization: {str(e)}")
#     s3_client = None
#     dynamodb = None
#     blogs_table = None

# # --- S3 User Functions ---
# USERS_S3_KEY = 'users/users.json'

# def load_users():
#     """Loads user data from the JSON file in S3."""
#     if not s3_client:
#         logger.warning("S3 client not initialized. Using in-memory users.")
#         return []
#     try:
#         obj = s3_client.get_object(Bucket=S3_BUCKET, Key=USERS_S3_KEY)
#         users_data = obj['Body'].read().decode('utf-8')
#         logger.info(f"Successfully loaded users from s3://{S3_BUCKET}/{USERS_S3_KEY}")
#         return json.loads(users_data) if users_data else []
#     except ClientError as e:
#         if e.response['Error']['Code'] == 'NoSuchKey':
#             logger.warning(f"Users file '{USERS_S3_KEY}' not found in bucket '{S3_BUCKET}'. Returning empty list.")
#             return []
#         logger.error(f"Error loading users from S3: {e.response['Error']['Message']}")
#         return []
#     except Exception as e:
#         logger.error(f"Unexpected error loading users from S3: {str(e)}")
#         return []

# def save_users(users):
#     """Saves the user list as a JSON file to S3."""
#     if not s3_client:
#         logger.warning("S3 client not initialized. Cannot save users.")
#         return False
#     try:
#         s3_client.put_object(
#             Bucket=S3_BUCKET,
#             Key=USERS_S3_KEY,
#             Body=json.dumps(users, indent=2),
#             ContentType='application/json'
#         )
#         logger.info(f"Users saved successfully to s3://{S3_BUCKET}/{USERS_S3_KEY}")
#         return True
#     except ClientError as e:
#         logger.error(f"ClientError saving users to S3: {e.response['Error']['Message']}")
#         return False
#     except Exception as e:
#         logger.error(f"Error saving users to S3: {str(e)}")
#         return False

# # In-memory fallback for users and history
# in_memory_users = []
# in_memory_history = {}

# @app.errorhandler(404)
# def not_found_error(error):
#     logger.error(f"404 error: {request.url}")
#     return jsonify({"error": "Endpoint not found"}), 404

# @app.errorhandler(500)
# def internal_error(error):
#     logger.error(f"500 error: {str(error)}")
#     return jsonify({"error": "Internal server error"}), 500

# @app.before_request
# def log_request_info():
#     logger.info(f"Incoming request: {request.method} {request.path} from {request.remote_addr}")

# @app.route('/')
# def index():
#     logger.info("Serving index.html")
#     return render_template('index.html')

# @app.route('/signup', methods=['POST'])
# def signup():
#     """Handles user signup and stores in S3 or in-memory."""
#     data = request.get_json()
#     if not data or not all(key in data for key in ['username', 'email', 'password']):
#         logger.error("Missing required fields in signup request")
#         return jsonify({"error": "Missing required fields: username, email, password"}), 400

#     username = data['username'].strip()
#     email = data['email'].strip()
#     password = data['password']

#     users = load_users() if s3_client else in_memory_users
#     if any(u['username'] == username for u in users):
#         logger.error(f"Username {username} already exists")
#         return jsonify({"error": "Username already exists"}), 400
#     if any(u['email'] == email for u in users):
#         logger.error(f"Email {email} already exists")
#         return jsonify({"error": "Email already exists"}), 400

#     hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
#     user_id = str(uuid.uuid4())
#     timestamp = datetime.now(timezone.utc).isoformat()

#     new_user = {
#         "id": user_id,
#         "username": username,
#         "email": email,
#         "password_hash": hashed_password,
#         "created_at": timestamp,
#         "trial_used": False
#     }
#     users.append(new_user)

#     if s3_client:
#         if not save_users(users):
#             logger.error(f"Failed to save updated user list to S3 for signup {username}.")
#             return jsonify({"error": "Failed to create user account. Please try again later."}), 500
#     else:
#         in_memory_users.append(new_user)
#         logger.info("Saved user to in-memory storage")

#     session['user_id'] = user_id
#     logger.info(f"User signed up: {username} (ID: {user_id})")
#     return jsonify({"message": "Signup successful", "user_id": user_id, "username": username}), 201

# @app.route('/login', methods=['POST'])
# def login():
#     """Handles user login using user data from S3 or in-memory."""
#     data = request.get_json()
#     if not data or not all(key in data for key in ['username', 'password']):
#         logger.error("Missing required fields in login request")
#         return jsonify({"error": "Missing required fields: username, password"}), 400

#     username = data['username'].strip()
#     password = data['password']

#     users = load_users() if s3_client else in_memory_users
#     user = next((u for u in users if u['username'] == username), None)

#     if not user:
#         logger.warning(f"Login attempt failed: Username '{username}' not found")
#         return jsonify({"error": "Invalid username or password"}), 401

#     if bcrypt.checkpw(password.encode('utf-8'), user['password_hash'].encode('utf-8')):
#         session['user_id'] = user['id']
#         if session.get('trial_used') and not user.get('trial_used'):
#             user['trial_used'] = True
#             if s3_client:
#                 if not save_users(users):
#                     logger.error(f"Failed to update trial_used status in S3 for user {username}")
#             else:
#                 in_memory_users[:] = users
#         logger.info(f"User logged in: {username} (ID: {user['id']})")
#         return jsonify({"message": "Login successful", "user_id": user['id'], "username": user['username']}), 200
#     else:
#         logger.warning(f"Login attempt failed: Incorrect password for username '{username}'")
#         return jsonify({"error": "Invalid username or password"}), 401

# @app.route('/logout', methods=['POST'])
# def logout():
#     user_id = session.pop('user_id', None)
#     session.pop('trial_used', None)
#     logger.info(f"User logged out: ID {user_id}" if user_id else "User logged out (no session found)")
#     return jsonify({"message": "Logout successful"}), 200

# @app.route('/check-session', methods=['GET'])
# def check_session():
#     """Checks session and verifies user_id against user data from S3 or in-memory."""
#     user_id = session.get('user_id')
#     if user_id:
#         users = load_users() if s3_client else in_memory_users
#         user = next((u for u in users if u.get('id') == user_id), None)
#         if user:
#             logger.info(f"check_session: Valid session found for user {user['username']}")
#             return jsonify({"isLoggedIn": True, "username": user['username'], "trial_available": not user['trial_used']}), 200
#         else:
#             session.pop('user_id', None)
#             logger.warning(f"check_session: User ID {user_id} found in session but not in user data. Cleared session.")

#     logger.info("check_session: No valid session found.")
#     return jsonify({"isLoggedIn": False, "trial_available": not session.get('trial_used', False)}), 200

# def check_auth():
#     user_id = session.get('user_id')
#     if user_id:
#         users = load_users() if s3_client else in_memory_users
#         if any(u.get('id') == user_id for u in users):
#             return True, user_id
#         session.pop('user_id', None)
#         return False, None
#     if not session.get('trial_used'):
#         return True, None
#     return False, None

# @app.route('/generate-blog', methods=['POST'])
# def generate_blog():
#     """Handles blog generation, calls API Gateway, stores result in DynamoDB."""
#     is_auth, user_id = check_auth()
#     if not is_auth:
#         logger.error("Unauthorized access to /generate-blog")
#         return jsonify({"error": "Login required. You've used your free trial."}), 401

#     data = request.get_json()
#     if not data or not data.get("topic"):
#         logger.error("Missing 'topic' in request body")
#         return jsonify({"error": "Missing 'topic' in request body"}), 400
#     if not data.get("language"):
#         logger.error("Missing 'language' in request body")
#         return jsonify({"error": "A language must be selected"}), 400
#     try:
#         tone_intensity = int(data.get("tone_intensity", 5))
#         if not (1 <= tone_intensity <= 10):
#             logger.error("Invalid tone intensity")
#             return jsonify({"error": "Tone intensity must be between 1 and 10"}), 400
#         word_count = int(data.get("word_count", 500))
#         if not (200 <= word_count <= 2000):
#             logger.error("Invalid word count")
#             return jsonify({"error": "Word count must be between 200 and 2000"}), 400
#     except ValueError:
#         logger.error("Invalid tone intensity or word count")
#         return jsonify({"error": "Tone intensity and word count must be valid numbers"}), 400
#     keywords = data.get("keywords", "").split(",") if data.get("keywords") else []
#     keywords = [k.strip() for k in keywords if k.strip()]
#     if len(keywords) > 5:
#         logger.error("Too many keywords")
#         return jsonify({"error": "Maximum 5 keywords allowed"}), 400
#     if not API_GATEWAY_URL:
#         logger.error("API Gateway URL not configured")
#         return jsonify({"error": "API Gateway URL not configured"}), 500

#     payload = {
#         "topic": data.get("topic"),
#         "audience": data.get("audience", "general"),
#         "tone": data.get("tone", "professional"),
#         "tone_intensity": tone_intensity,
#         "word_count": word_count,
#         "keywords": keywords,
#         "languages": [data.get("language", "en")]
#     }
#     logger.info(f"Received request: {payload}")

#     try:
#         headers = {'Content-Type': 'application/json'}
#         response = requests.post(API_GATEWAY_URL, data=json.dumps(payload), headers=headers, timeout=90)
#         response.raise_for_status()

#         # Attempt to parse response as JSON regardless of Content-Type
#         try:
#             api_response = response.json()
#             logger.info(f"API Gateway response: {api_response}")
#         except ValueError as e:
#             logger.error(f"Failed to parse API Gateway response as JSON: {str(e)}")
#             logger.error(f"Response text (first 500 chars): {response.text[:500]}")
#             return jsonify({
#                 "error": "The content generation service returned an invalid JSON response. Please check the server logs."
#             }), 502

#         results = api_response.get("results", {})
#         if not results:
#             logger.error("No results returned from API Gateway")
#             return jsonify({"error": "Content generation failed (no results)."}), 500

#         lang = payload["languages"][0]
#         result = results.get(lang)
#         if not result:
#             first_available_lang = next(iter(results)) if results else None
#             if first_available_lang:
#                 logger.warning(f"Requested language '{lang}' not found, using '{first_available_lang}'")
#                 lang = first_available_lang
#                 result = results[lang]
#             else:
#                 logger.error(f"No content generated for language '{lang}' or any other")
#                 return jsonify({"error": f"No content generated for the requested language '{lang}' or any other."}), 500

#         s3_key = result.get("s3_key")
#         content = result.get("content")

#         if s3_key and not content:
#             logger.info(f"Content for {lang} is on S3 ({s3_key}), fetching...")
#             try:
#                 if not s3_client:
#                     raise ConnectionError("S3 client not available.")
#                 s3_obj = s3_client.get_object(Bucket=S3_BUCKET, Key=s3_key)
#                 content = s3_obj['Body'].read().decode('utf-8')
#                 result["content"] = content
#                 logger.info(f"Successfully fetched content from S3 key: {s3_key}")
#             except ClientError as e:
#                 error_code = e.response.get("Error", {}).get("Code")
#                 logger.error(f"Failed to fetch content from S3 ({s3_key}) with ClientError: {error_code} - {str(e)}")
#                 return jsonify({"error": f"Failed to fetch content from S3 due to a permission or configuration error: {error_code}"}), 500
#             except ConnectionError as e:
#                 logger.error(f"Failed to fetch content from S3. Error: {str(e)}")
#                 return jsonify({"error": str(e)}), 500

#         if not content and not s3_key:
#             logger.error(f"No content or S3 key found for language: {lang}")
#             return jsonify({"error": f"Content generation failed (missing content and S3 key for language {lang})."}), 500

#         if user_id:
#             in_memory_history.setdefault(user_id, [])
#             history_item_id = str(uuid.uuid4())
#             history_item = {
#                 "id": history_item_id,
#                 "brief": payload["topic"],
#                 "language": lang,
#                 "tone": payload["tone"],
#                 "audience": payload["audience"],
#                 "version": f"v{len([h for h in in_memory_history.get(user_id, []) if h['brief'] == payload['topic']]) + 1}.0",
#                 "result_text": content or "",
#                 "summary_text": result.get("summary", "Summary not provided"),
#                 "quality_score": float(result.get("quality_score", 0.0)),
#                 "created_at": datetime.now(timezone.utc).isoformat(),
#                 "s3_key": s3_key
#             }
#             in_memory_history[user_id].append(history_item)

#             if blogs_table:
#                 try:
#                     dynamo_item = {
#                         'blogId': history_item_id,
#                         'user_id': user_id,
#                         'brief': history_item['brief'],
#                         'language': history_item['language'],
#                         'tone': history_item['tone'],
#                         'audience': history_item['audience'],
#                         'version': history_item['version'],
#                         'content': history_item['result_text'],
#                         'summary': history_item['summary_text'],
#                         'quality_score': str(history_item['quality_score']),
#                         'created_at': history_item['created_at'],
#                         's3_key': history_item.get('s3_key')
#                     }
#                     dynamo_item = {k: v for k, v in dynamo_item.items() if v is not None}
#                     blogs_table.put_item(Item=dynamo_item)
#                     logger.info(f"Successfully saved blog '{history_item_id}' to DynamoDB for user '{user_id}'.")
#                 except ClientError as e:
#                     logger.error(f"Error saving blog '{history_item_id}' to DynamoDB: {e.response['Error']['Message']}")
#             else:
#                 logger.warning(f"DynamoDB blogs table not initialized. Using in-memory history for user '{user_id}'.")
#         else:
#             session['trial_used'] = True
#             logger.info("Trial user generated content. History not saved persistently.")

#         response_payload = {"results": {lang: result}}
#         response = jsonify(response_payload)
#         response.headers["X-Response-Source"] = "generate-blog"
#         return response, 200

#     except requests.exceptions.Timeout:
#         logger.error("Error calling API Gateway: Request timed out.")
#         return jsonify({"error": "Error calling API Gateway: Request timed out."}), 504
#     except requests.exceptions.RequestException as e:
#         error_message = f"Error calling API Gateway: {str(e)}"
#         logger.error(error_message)
#         status_code = e.response.status_code if hasattr(e, 'response') and e.response else 500
#         return jsonify({"error": error_message}), status_code
#     except Exception as e:
#         logger.error(f"Unexpected error in generate-blog: {str(e)}", exc_info=True)
#         return jsonify({"error": "An internal server error occurred."}), 500

# @app.route('/history', methods=['GET'])
# def get_history():
#     """Returns the list of stored history items for the logged-in user from DynamoDB or in-memory."""
#     user_id = session.get('user_id')
#     if not user_id:
#         logger.error("Unauthorized access to /history")
#         return jsonify({"error": "Login required to view history"}), 401

#     user_history = []
#     if blogs_table:
#         try:
#             response = blogs_table.query(
#                 IndexName='user_id-index',
#                 KeyConditionExpression='user_id = :uid',
#                 ExpressionAttributeValues={':uid': user_id}
#             )
#             items_from_db = response.get('Items', [])
#             for item in items_from_db:
#                 history_item = {
#                     "id": item.get('blog_id'),
#                     "brief": item.get('brief'),
#                     "language": item.get('language'),
#                     "tone": item.get('tone'),
#                     "audience": item.get('audience'),
#                     "version": item.get('version'),
#                     "result_text": item.get('content', ''),
#                     "summary_text": item.get('summary', "Summary not provided"),
#                     "quality_score": float(item.get('quality_score', 0.0)) if item.get('quality_score') else 0.0,
#                     "created_at": item.get('created_at'),
#                     "s3_key": item.get('s3_key')
#                 }
#                 user_history.append(history_item)
#             logger.info(f"Fetched {len(user_history)} history items from DynamoDB for user {user_id}")
#         except Exception as e:
#             logger.error(f"Failed to fetch history from DynamoDB for user {user_id}: {str(e)}", exc_info=True)
#             logger.warning(f"Falling back to in-memory history for user {user_id}")
#             user_history = in_memory_history.get(user_id, [])
#     else:
#         logger.warning(f"DynamoDB blogs table not initialized. Using in-memory history for user {user_id}")
#         user_history = in_memory_history.get(user_id, [])

#     user_history.sort(key=lambda x: x.get('created_at', ''), reverse=True)
#     response = jsonify(user_history)
#     response.headers["X-History-Count"] = len(user_history)
#     response.headers["X-Server-Time"] = datetime.now(timezone.utc).isoformat()
#     response.headers["X-Response-Source"] = "history"
#     return response, 200

# @app.route('/loginMsg.js', methods=['GET'])
# def login_msg_js():
#     """Handles requests for missing loginMsg.js file."""
#     logger.error(f"Static file 'loginMsg.js' not found in {static_folder}")
#     return jsonify({"error": "Static file 'loginMsg.js' not found. Please check if the file exists in the static folder or update the frontend to remove this reference."}), 404

# if __name__ == '__main__':
#     port = int(os.environ.get('PORT', 5000))
#     debug_mode = os.environ.get('FLASK_DEBUG', '1' if os.environ.get('FLASK_ENV') == 'development' else '0') == '1'
#     app.run(host="0.0.0.0", port=port, debug=debug_mode)




import os
import json
import requests
from datetime import datetime
import uuid
import logging
from flask import Flask, request, jsonify, render_template, session
from flask_cors import CORS
from dotenv import load_dotenv
import boto3
from botocore.exceptions import ClientError, NoCredentialsError, PartialCredentialsError
import bcrypt
from dynamodb_json import json_util as dynamodb_json
from datetime import timezone

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
app.secret_key = os.getenv('SECRET_KEY', 'your-default-secret-key-change-this')
CORS(app, resources={r"/*": {"origins": "*"}})

# Get Config from .env
API_GATEWAY_URL = os.getenv("API_GATEWAY_URL")
AWS_REGION = os.getenv("AWS_REGION", "us-east-1")
DYNAMODB_BLOGS_TABLE_NAME = os.getenv("DYNAMODB_TABLE_NAME", "blogs")
S3_BUCKET = os.getenv("S3_BUCKET", "agentx-blog")

# --- AWS Clients Initialization ---
try:
    s3_client = boto3.client('s3', region_name=AWS_REGION)
    logger.info(f"S3 Client initialized for region {AWS_REGION}.")
    dynamodb = boto3.resource('dynamodb', region_name=AWS_REGION)
    blogs_table = dynamodb.Table(DYNAMODB_BLOGS_TABLE_NAME)
    blogs_table.load()
    logger.info(f"Successfully connected to DynamoDB blogs table: {DYNAMODB_BLOGS_TABLE_NAME}")
except (NoCredentialsError, PartialCredentialsError):
    logger.error("AWS credentials not found. Using in-memory fallback.")
    s3_client = None
    dynamodb = None
    blogs_table = None
except ClientError as e:
    logger.error(f"Error connecting to AWS services: {e.response['Error']['Message']}")
    s3_client = None
    dynamodb = None
    blogs_table = None
except Exception as e:
    logger.error(f"Unexpected error during AWS initialization: {str(e)}")
    s3_client = None
    dynamodb = None
    blogs_table = None

# --- S3 User Functions ---
USERS_S3_KEY = 'users/users.json'

def load_users():
    """Loads user data from the JSON file in S3."""
    if not s3_client:
        logger.warning("S3 client not initialized. Using in-memory users.")
        return []
    try:
        obj = s3_client.get_object(Bucket=S3_BUCKET, Key=USERS_S3_KEY)
        users_data = obj['Body'].read().decode('utf-8')
        logger.info(f"Successfully loaded users from s3://{S3_BUCKET}/{USERS_S3_KEY}")
        return json.loads(users_data) if users_data else []
    except ClientError as e:
        if e.response['Error']['Code'] == 'NoSuchKey':
            logger.warning(f"Users file '{USERS_S3_KEY}' not found in bucket '{S3_BUCKET}'. Returning empty list.")
            return []
        logger.error(f"Error loading users from S3: {e.response['Error']['Message']}")
        return []
    except Exception as e:
        logger.error(f"Unexpected error loading users from S3: {str(e)}")
        return []

def save_users(users):
    """Saves the user list as a JSON file to S3."""
    if not s3_client:
        logger.warning("S3 client not initialized. Cannot save users.")
        return False
    try:
        s3_client.put_object(
            Bucket=S3_BUCKET,
            Key=USERS_S3_KEY,
            Body=json.dumps(users, indent=2),
            ContentType='application/json'
        )
        logger.info(f"Users saved successfully to s3://{S3_BUCKET}/{USERS_S3_KEY}")
        return True
    except ClientError as e:
        logger.error(f"ClientError saving users to S3: {e.response['Error']['Message']}")
        return False
    except Exception as e:
        logger.error(f"Error saving users to S3: {str(e)}")
        return False

# In-memory fallback for users and history
in_memory_users = []
in_memory_history = {}

@app.errorhandler(404)
def not_found_error(error):
    logger.error(f"404 error: {request.url}")
    return jsonify({"error": "Endpoint not found"}), 404

@app.errorhandler(500)
def internal_error(error):
    logger.error(f"500 error: {str(error)}")
    return jsonify({"error": "Internal server error"}), 500

@app.before_request
def log_request_info():
    logger.info(f"Incoming request: {request.method} {request.path} from {request.remote_addr}")

@app.route('/')
def index():
    logger.info("Serving index.html")
    return render_template('index.html')

@app.route('/signup', methods=['POST'])
def signup():
    """Handles user signup and stores in S3 or in-memory."""
    data = request.get_json()
    if not data or not all(key in data for key in ['username', 'email', 'password']):
        logger.error("Missing required fields in signup request")
        return jsonify({"error": "Missing required fields: username, email, password"}), 400

    username = data['username'].strip()
    email = data['email'].strip()
    password = data['password']

    users = load_users() if s3_client else in_memory_users
    if any(u['username'] == username for u in users):
        logger.error(f"Username {username} already exists")
        return jsonify({"error": "Username already exists"}), 400
    if any(u['email'] == email for u in users):
        logger.error(f"Email {email} already exists")
        return jsonify({"error": "Email already exists"}), 400

    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    user_id = str(uuid.uuid4())
    timestamp = datetime.now(timezone.utc).isoformat()

    new_user = {
        "id": user_id,
        "username": username,
        "email": email,
        "password_hash": hashed_password,
        "created_at": timestamp,
        "trial_used": False
    }
    users.append(new_user)

    if s3_client:
        if not save_users(users):
            logger.error(f"Failed to save updated user list to S3 for signup {username}.")
            return jsonify({"error": "Failed to create user account. Please try again later."}), 500
    else:
        in_memory_users.append(new_user)
        logger.info("Saved user to in-memory storage")

    session['user_id'] = user_id
    logger.info(f"User signed up: {username} (ID: {user_id})")
    return jsonify({"message": "Signup successful", "user_id": user_id, "username": username}), 201

@app.route('/login', methods=['POST'])
def login():
    """Handles user login using user data from S3 or in-memory."""
    data = request.get_json()
    if not data or not all(key in data for key in ['username', 'password']):
        logger.error("Missing required fields in login request")
        return jsonify({"error": "Missing required fields: username, password"}), 400

    username = data['username'].strip()
    password = data['password']

    users = load_users() if s3_client else in_memory_users
    user = next((u for u in users if u['username'] == username), None)

    if not user:
        logger.warning(f"Login attempt failed: Username '{username}' not found")
        return jsonify({"error": "Invalid username or password"}), 401

    if bcrypt.checkpw(password.encode('utf-8'), user['password_hash'].encode('utf-8')):
        session['user_id'] = user['id']
        if session.get('trial_used') and not user.get('trial_used'):
            user['trial_used'] = True
            if s3_client:
                if not save_users(users):
                    logger.error(f"Failed to update trial_used status in S3 for user {username}")
            else:
                in_memory_users[:] = users
        logger.info(f"User logged in: {username} (ID: {user['id']})")
        return jsonify({"message": "Login successful", "user_id": user['id'], "username": user['username']}), 200
    else:
        logger.warning(f"Login attempt failed: Incorrect password for username '{username}'")
        return jsonify({"error": "Invalid username or password"}), 401

@app.route('/logout', methods=['POST'])
def logout():
    user_id = session.pop('user_id', None)
    session.pop('trial_used', None)
    logger.info(f"User logged out: ID {user_id}" if user_id else "User logged out (no session found)")
    return jsonify({"message": "Logout successful"}), 200

@app.route('/check-session', methods=['GET'])
def check_session():
    """Checks session and verifies user_id against user data from S3 or in-memory."""
    user_id = session.get('user_id')
    if user_id:
        users = load_users() if s3_client else in_memory_users
        user = next((u for u in users if u.get('id') == user_id), None)
        if user:
            logger.info(f"check_session: Valid session found for user {user['username']}")
            return jsonify({
                "isLoggedIn": True,
                "username": user['username'],
                "trial_available": not user['trial_used'],
                "canGenerate": not session.get('trial_used', False) or user_id is not None
            }), 200
        else:
            session.pop('user_id', None)
            logger.warning(f"check_session: User ID {user_id} found in session but not in user data. Cleared session.")

    logger.info("check_session: No valid session found.")
    return jsonify({
        "isLoggedIn": False,
        "trial_available": not session.get('trial_used', False),
        "canGenerate": not session.get('trial_used', False)
    }), 200

def check_auth():
    user_id = session.get('user_id')
    if user_id:
        users = load_users() if s3_client else in_memory_users
        if any(u.get('id') == user_id for u in users):
            return True, user_id
        session.pop('user_id', None)
        return False, None
    if not session.get('trial_used'):
        return True, None
    return False, None

@app.route('/generate-blog', methods=['POST'])
def generate_blog():
    """Handles blog generation, calls API Gateway, stores result in DynamoDB."""
    is_auth, user_id = check_auth()
    if not is_auth:
        logger.error("Unauthorized access to /generate-blog")
        return jsonify({"error": "Login required. You've used your free trial."}), 401

    data = request.get_json()
    if not data or not data.get("topic"):
        logger.error("Missing 'topic' in request body")
        return jsonify({"error": "Missing 'topic' in request body"}), 400
    if not data.get("language"):
        logger.error("Missing 'language' in request body")
        return jsonify({"error": "A language must be selected"}), 400
    try:
        tone_intensity = int(data.get("tone_intensity", 5))
        if not (1 <= tone_intensity <= 10):
            logger.error("Invalid tone intensity")
            return jsonify({"error": "Tone intensity must be between 1 and 10"}), 400
        word_count = int(data.get("word_count", 500))
        if not (200 <= word_count <= 2000):
            logger.error("Invalid word count")
            return jsonify({"error": "Word count must be between 200 and 2000"}), 400
    except ValueError:
        logger.error("Invalid tone intensity or word count")
        return jsonify({"error": "Tone intensity and word count must be valid numbers"}), 400
    keywords = data.get("keywords", "").split(",") if data.get("keywords") else []
    keywords = [k.strip() for k in keywords if k.strip()]
    if len(keywords) > 5:
        logger.error("Too many keywords")
        return jsonify({"error": "Maximum 5 keywords allowed"}), 400
    if not API_GATEWAY_URL:
        logger.error("API Gateway URL not configured")
        return jsonify({"error": "API Gateway URL not configured"}), 500

    payload = {
        "topic": data.get("topic"),
        "audience": data.get("audience", "general"),
        "tone": data.get("tone", "professional"),
        "tone_intensity": tone_intensity,
        "word_count": word_count,
        "keywords": keywords,
        "languages": [data.get("language", "en")]
    }
    logger.info(f"Received request: {payload}")

    try:
        headers = {'Content-Type': 'application/json'}
        response = requests.post(API_GATEWAY_URL, data=json.dumps(payload), headers=headers, timeout=90)
        response.raise_for_status()

        # Attempt to parse response as JSON regardless of Content-Type
        try:
            api_response = response.json()
            logger.info(f"API Gateway response: {api_response}")
        except ValueError as e:
            logger.error(f"Failed to parse API Gateway response as JSON: {str(e)}")
            logger.error(f"Response text (first 500 chars): {response.text[:500]}")
            return jsonify({
                "error": "The content generation service returned an invalid JSON response. Please check the server logs."
            }), 502

        results = api_response.get("results", {})
        if not results:
            logger.error("No results returned from API Gateway")
            return jsonify({"error": "Content generation failed (no results)."}), 500

        lang = payload["languages"][0]
        result = results.get(lang)
        if not result:
            first_available_lang = next(iter(results)) if results else None
            if first_available_lang:
                logger.warning(f"Requested language '{lang}' not found, using '{first_available_lang}'")
                lang = first_available_lang
                result = results[lang]
            else:
                logger.error(f"No content generated for language '{lang}' or any other")
                return jsonify({"error": f"No content generated for the requested language '{lang}' or any other."}), 500

        s3_key = result.get("s3_key")
        content = result.get("content")

        if s3_key and not content:
            logger.info(f"Content for {lang} is on S3 ({s3_key}), fetching...")
            try:
                if not s3_client:
                    raise ConnectionError("S3 client not available.")
                s3_obj = s3_client.get_object(Bucket=S3_BUCKET, Key=s3_key)
                content = s3_obj['Body'].read().decode('utf-8')
                result["content"] = content
                logger.info(f"Successfully fetched content from S3 key: {s3_key}")
            except ClientError as e:
                error_code = e.response.get("Error", {}).get("Code")
                logger.error(f"Failed to fetch content from S3 ({s3_key}) with ClientError: {error_code} - {str(e)}")
                return jsonify({"error": f"Failed to fetch content from S3 due to a permission or configuration error: {error_code}"}), 500
            except ConnectionError as e:
                logger.error(f"Failed to fetch content from S3. Error: {str(e)}")
                return jsonify({"error": str(e)}), 500

        if not content and not s3_key:
            logger.error(f"No content or S3 key found for language: {lang}")
            return jsonify({"error": f"Content generation failed (missing content and S3 key for language {lang})."}), 500

        if user_id:
            in_memory_history.setdefault(user_id, [])
            history_item_id = str(uuid.uuid4())
            history_item = {
                "id": history_item_id,
                "brief": payload["topic"],
                "language": lang,
                "tone": payload["tone"],
                "audience": payload["audience"],
                "version": f"v{len([h for h in in_memory_history.get(user_id, []) if h['brief'] == payload['topic']]) + 1}.0",
                "result_text": content or "",
                "summary_text": result.get("summary", "Summary not provided"),
                "quality_score": float(result.get("quality_score", 0.0)),
                "created_at": datetime.now(timezone.utc).isoformat(),
                "s3_key": s3_key
            }
            in_memory_history[user_id].append(history_item)

            if blogs_table:
                try:
                    dynamo_item = {
                        'blogId': history_item_id,
                        'user_id': user_id,
                        'brief': history_item['brief'],
                        'language': history_item['language'],
                        'tone': history_item['tone'],
                        'audience': history_item['audience'],
                        'version': history_item['version'],
                        'content': history_item['result_text'],
                        'summary': history_item['summary_text'],
                        'quality_score': str(history_item['quality_score']),
                        'created_at': history_item['created_at'],
                        's3_key': history_item.get('s3_key')
                    }
                    dynamo_item = {k: v for k, v in dynamo_item.items() if v is not None}
                    blogs_table.put_item(Item=dynamo_item)
                    logger.info(f"Successfully saved blog '{history_item_id}' to DynamoDB for user '{user_id}'.")
                except ClientError as e:
                    logger.error(f"Error saving blog '{history_item_id}' to DynamoDB: {e.response['Error']['Message']}")
            else:
                logger.warning(f"DynamoDB blogs table not initialized. Using in-memory history for user '{user_id}'.")
        else:
            session['trial_used'] = True
            logger.info("Trial user generated content. History not saved persistently.")

        response_payload = {"results": {lang: result}}
        response = jsonify(response_payload)
        response.headers["X-Response-Source"] = "generate-blog"
        return response, 200

    except requests.exceptions.Timeout:
        logger.error("Error calling API Gateway: Request timed out.")
        return jsonify({"error": "Error calling API Gateway: Request timed out."}), 504
    except requests.exceptions.RequestException as e:
        error_message = f"Error calling API Gateway: {str(e)}"
        logger.error(error_message)
        status_code = e.response.status_code if hasattr(e, 'response') and e.response else 500
        return jsonify({"error": error_message}), status_code
    except Exception as e:
        logger.error(f"Unexpected error in generate-blog: {str(e)}", exc_info=True)
        return jsonify({"error": "An internal server error occurred."}), 500

@app.route('/history', methods=['GET'])
def get_history():
    """Returns the list of stored history items for the logged-in user from DynamoDB or in-memory."""
    user_id = session.get('user_id')
    if not user_id:
        logger.error("Unauthorized access to /history")
        return jsonify({"error": "Login required to view history"}), 401

    user_history = []
    if blogs_table:
        try:
            response = blogs_table.query(
                IndexName='user_id-index',
                KeyConditionExpression='user_id = :uid',
                ExpressionAttributeValues={':uid': user_id}
            )
            items_from_db = response.get('Items', [])
            for item in items_from_db:
                history_item = {
                    "id": item.get('blog_id'),
                    "brief": item.get('brief'),
                    "language": item.get('language'),
                    "tone": item.get('tone'),
                    "audience": item.get('audience'),
                    "version": item.get('version'),
                    "result_text": item.get('content', ''),
                    "summary_text": item.get('summary', "Summary not provided"),
                    "quality_score": float(item.get('quality_score', 0.0)) if item.get('quality_score') else 0.0,
                    "created_at": item.get('created_at'),
                    "s3_key": item.get('s3_key')
                }
                user_history.append(history_item)
            logger.info(f"Fetched {len(user_history)} history items from DynamoDB for user {user_id}")
        except Exception as e:
            logger.error(f"Failed to fetch history from DynamoDB for user {user_id}: {str(e)}", exc_info=True)
            logger.warning(f"Falling back to in-memory history for user {user_id}")
            user_history = in_memory_history.get(user_id, [])
    else:
        logger.warning(f"DynamoDB blogs table not initialized. Using in-memory history for user {user_id}")
        user_history = in_memory_history.get(user_id, [])

    user_history.sort(key=lambda x: x.get('created_at', ''), reverse=True)
    response = jsonify(user_history)
    response.headers["X-History-Count"] = len(user_history)
    response.headers["X-Server-Time"] = datetime.now(timezone.utc).isoformat()
    response.headers["X-Response-Source"] = "history"
    return response, 200

@app.route('/loginMsg.js', methods=['GET'])
def login_msg_js():
    """Handles requests for missing loginMsg.js file."""
    logger.error(f"Static file 'loginMsg.js' not found in {static_folder}")
    return jsonify({"error": "Static file 'loginMsg.js' not found. Please check if the file exists in the static folder or update the frontend to remove this reference."}), 404

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug_mode = os.environ.get('FLASK_DEBUG', '1' if os.environ.get('FLASK_ENV') == 'development' else '0') == '1'
    app.run(host="0.0.0.0", port=port, debug=debug_mode)
