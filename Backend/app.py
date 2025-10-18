# import os
# import json
# import requests
# from flask import Flask, request, jsonify, render_template, session
# from flask_cors import CORS
# from dotenv import load_dotenv
# from datetime import datetime
# import uuid
# import logging
# import boto3 # <-- Import Boto3
# from botocore.exceptions import ClientError, NoCredentialsError, PartialCredentialsError # <-- Added more specific exceptions
# import bcrypt

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
# app.secret_key = os.getenv('SECRET_KEY', 'your-default-secret-key-change-this') # Set a secure key in .env
# CORS(app, resources={r"/*": {"origins": "*"}}) # Enable CORS for all routes and origins

# # Get the API Gateway URL from the .env file
# API_GATEWAY_URL = os.getenv("API_GATEWAY_URL")
# AWS_REGION = os.getenv("AWS_REGION", "us-east-1") # Get AWS region

# # AWS S3 Configuration
# S3_BUCKET = os.getenv("S3_BUCKET", "agentx-blog") # Same bucket as content
# s3_client = boto3.client('s3', region_name=AWS_REGION)

# # Users file in S3
# USERS_S3_KEY = 'users/users.json'

# # --- DynamoDB Configuration ---
# DYNAMODB_TABLE_NAME = os.getenv("DYNAMODB_TABLE_NAME", "blogs") # Read table name from .env
# try:
#     dynamodb = boto3.resource('dynamodb', region_name=AWS_REGION)
#     blogs_table = dynamodb.Table(DYNAMODB_TABLE_NAME)
#     logger.info(f"Successfully connected to DynamoDB table: {DYNAMODB_TABLE_NAME}")
# except (NoCredentialsError, PartialCredentialsError):
#     logger.error("AWS credentials not found. Ensure credentials are configured (e.g., ~/.aws/credentials, environment variables, or IAM role).")
#     dynamodb = None
#     blogs_table = None
# except ClientError as e:
#     logger.error(f"Error connecting to DynamoDB table '{DYNAMODB_TABLE_NAME}': {e.response['Error']['Message']}")
#     dynamodb = None
#     blogs_table = None
# except Exception as e:
#     logger.error(f"An unexpected error occurred during DynamoDB initialization: {str(e)}")
#     dynamodb = None
#     blogs_table = None
# # --- End DynamoDB Configuration ---


# # Load users from S3 (with fallback to empty list)
# def load_users():
#     try:
#         obj = s3_client.get_object(Bucket=S3_BUCKET, Key=USERS_S3_KEY)
#         users_data = obj['Body'].read().decode('utf-8')
#         return json.loads(users_data) if users_data else []
#     except ClientError as e:
#         if e.response['Error']['Code'] == 'NoSuchKey':
#             logger.warning(f"Users file '{USERS_S3_KEY}' not found in bucket '{S3_BUCKET}'. Returning empty list.")
#             return []
#         else:
#             logger.error(f"Error loading users from S3: {e}")
#             return []
#     except Exception as e:
#         logger.error(f"Unexpected error loading users from S3: {str(e)}")
#         return []


# # Save users to S3
# def save_users(users):
#     try:
#         s3_client.put_object(
#             Bucket=S3_BUCKET,
#             Key=USERS_S3_KEY,
#             Body=json.dumps(users, indent=2),
#             ContentType='application/json'
#         )
#         logger.info("Users saved to S3 successfully")
#     except ClientError as e:
#         logger.error(f"ClientError saving users to S3: {e.response['Error']['Message']}")
#     except Exception as e:
#         logger.error(f"Error saving users to S3: {str(e)}")


# # In-memory history store (simulating a database) - now per-user
# history_store = {} # {user_id: list of history items}

# # Log all incoming requests for debugging
# @app.before_request
# def log_request_info():
#     logger.info(f"Incoming request: {request.method} {request.path} from {request.remote_addr}")

# @app.route('/')
# def index():
#     """Renders the main single-page HTML application."""
#     logger.info("Serving index.html")
#     return render_template('index.html')

# @app.route('/signup', methods=['POST'])
# def signup():
#     """Handles user signup and stores in S3."""
#     data = request.get_json()
#     if not data or not all(k in data for k in ['username', 'email', 'password']):
#         return jsonify({"error": "Missing required fields: username, email, password"}), 400

#     users = load_users()
#     if any(u['username'] == data['username'] for u in users):
#         return jsonify({"error": "Username already exists"}), 400
#     if any(u['email'] == data['email'] for u in users):
#         return jsonify({"error": "Email already exists"}), 400

#     # Hash password
#     hashed_password = bcrypt.hashpw(data['password'].encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
#     user_id = str(uuid.uuid4())
#     new_user = {
#         "id": user_id,
#         "username": data['username'],
#         "email": data['email'],
#         "password_hash": hashed_password,
#         "created_at": datetime.utcnow().isoformat() + "Z",
#         "trial_used": False # Track if trial was used before signup
#     }
#     users.append(new_user)
#     save_users(users)

#     session['user_id'] = user_id
#     logger.info(f"User signed up: {data['username']}")
#     return jsonify({"message": "Signup successful", "user_id": user_id, "username": new_user['username']}), 201

# @app.route('/login', methods=['POST'])
# def login():
#     """Handles user login."""
#     data = request.get_json()
#     if not data or not all(k in data for k in ['username', 'password']):
#         return jsonify({"error": "Missing required fields: username, password"}), 400

#     users = load_users()
#     user = next((u for u in users if u['username'] == data['username']), None)
#     if not user or not bcrypt.checkpw(data['password'].encode('utf-8'), user['password_hash'].encode('utf-8')):
#         return jsonify({"error": "Invalid username or password"}), 401

#     session['user_id'] = user['id']
#     # If trial was used anonymously, mark it as used now
#     if session.get('trial_used'):
#         user['trial_used'] = True
#         save_users(users)

#     logger.info(f"User logged in: {data['username']}")
#     return jsonify({"message": "Login successful", "user_id": user['id'], "username": user['username']}), 200

# @app.route('/logout', methods=['POST'])
# def logout():
#     """Handles user logout."""
#     session.pop('user_id', None)
#     session.pop('trial_used', None)
#     return jsonify({"message": "Logout successful"}), 200

# @app.route('/check-session', methods=['GET'])
# def check_session():
#     """Checks if a user is currently logged in."""
#     user_id = session.get('user_id')
#     if user_id:
#         users = load_users()
#         user = next((u for u in users if u['id'] == user_id), None)
#         if user:
#             return jsonify({"isLoggedIn": True, "username": user['username']}), 200
#         else:
#             # User ID in session but not found in storage - clear session
#             session.pop('user_id', None)
#             logger.warning(f"User ID {user_id} found in session but not in user data. Cleared session.")

#     # Not logged in
#     return jsonify({
#         "isLoggedIn": False,
#         "trial_available": not session.get('trial_used', False)
#     }), 200

# def check_auth():
#     """Check if user is authenticated or has trial available."""
#     user_id = session.get('user_id')
#     if user_id:
#         return True, user_id

#     # Check trial
#     if not session.get('trial_used'):
#         return True, None # Allow trial
#     return False, None

# @app.route('/generate-blog', methods=['POST'])
# def generate_blog():
#     """Handles blog generation, calls API Gateway, stores result in history, and saves to DynamoDB."""
#     is_auth, user_id = check_auth()
#     if not is_auth:
#         return jsonify({"error": "Login required. You've used your free trial."}), 401

#     actual_user_id = user_id # Keep track of the real user ID if logged in

#     data = request.get_json()
#     if not data or not data.get("topic"):
#         logger.error("Missing 'topic' in request body")
#         return jsonify({"error": "Missing 'topic' in request body"}), 400
#     if not data.get("language"):
#         logger.error("A language must be selected")
#         return jsonify({"error": "A language must be selected"}), 400

#     # Validate advanced settings
#     try:
#         tone_intensity = int(data.get("tone_intensity", 5))
#         if not (1 <= tone_intensity <= 10):
#             logger.error("Invalid tone intensity: %s", tone_intensity)
#             return jsonify({"error": "Tone intensity must be between 1 and 10"}), 400

#         word_count = int(data.get("word_count", 500))
#         if not (200 <= word_count <= 2000):
#             logger.error("Invalid word count: %s", word_count)
#             return jsonify({"error": "Word count must be between 200 and 2000"}), 400
#     except ValueError as e:
#         logger.error("Invalid numeric input: %s", str(e))
#         return jsonify({"error": "Tone intensity and word count must be valid numbers"}), 400

#     keywords = data.get("keywords", "").split(",") if data.get("keywords") else []
#     keywords = [k.strip() for k in keywords if k.strip()] # Remove empty or whitespace-only keywords
#     if len(keywords) > 5:
#         logger.error("Too many keywords: %s", len(keywords))
#         return jsonify({"error": "Maximum 5 keywords allowed"}), 400

#     if not API_GATEWAY_URL:
#         logger.error("API Gateway URL not configured")
#         return jsonify({"error": "API Gateway URL not configured"}), 500

#     # Prepare the payload for the Lambda function
#     payload = {
#         "topic": data.get("topic"),
#         "audience": data.get("audience", "general"),
#         "tone": data.get("tone", "professional"),
#         "tone_intensity": tone_intensity,
#         "word_count": word_count,
#         "keywords": keywords,
#         "language": data.get("language", "en")
#     }
#     logger.info("Received request: %s", payload)

#     # Forward the request to AWS API Gateway
#     try:
#         headers = {'Content-Type': 'application/json'}
#         response = requests.post(API_GATEWAY_URL, data=json.dumps(payload), headers=headers, timeout=60) # Increased timeout
#         response.raise_for_status() # Raise an exception for HTTP errors
#         api_response = response.json()
#         logger.info("API Gateway response: %s", api_response)

#         # Validate response structure
#         results = api_response.get("results", {})
#         if not results:
#             logger.error("No results returned from API Gateway")
#             return jsonify({"error": "No results returned from API Gateway"}), 500

#         lang = payload["language"]
#         if lang not in results:
#             logger.error("No content generated for language: %s", lang)
#             return jsonify({"error": f"No content generated for language: {lang}"}), 500

#         result = results[lang] # Get the specific language result
#         s3_key = result.get("s3_key")
#         content = result.get("content")

#         # --- Fetch content from S3 if only key is present ---
#         if s3_key and not content:
#             logger.info(f"Content for {lang} is on S3 ({s3_key}), fetching...")
#             try:
#                 s3_obj = s3_client.get_object(Bucket=S3_BUCKET, Key=s3_key)
#                 content = s3_obj['Body'].read().decode('utf-8')
#                 result["content"] = content # Add fetched content back to the result
#                 logger.info(f"Successfully fetched content from S3 key: {s3_key}")
#             except ClientError as e:
#                 error_message = f"Failed to fetch content from S3 ({s3_key}): {e.response['Error']['Message']}"
#                 logger.error(error_message)
#                 # Decide if you want to return an error or continue without content
#                 return jsonify({"error": error_message}), 500
#             except Exception as e:
#                 error_message = f"Unexpected error fetching from S3 ({s3_key}): {str(e)}"
#                 logger.error(error_message)
#                 return jsonify({"error": error_message}), 500
#         # --- End S3 Fetch ---

#         if not content and not s3_key: # Check again after potential S3 fetch
#              logger.error("No content or S3 key provided for language: %s", lang)
#              return jsonify({"error": f"No content or S3 key provided for language: {lang}"}), 500

#         # Store the generated content in history_store (per user)
#         if actual_user_id is None: # Trial user
#             session['trial_used'] = True
#             user_id_for_history = 'trial_' + str(uuid.uuid4()) # Temp ID for trial history (won't persist)
#             logger.info("Trial user generated content. History stored temporarily.")
#         else:
#             user_id_for_history = actual_user_id # Use the real user ID

#         if user_id_for_history not in history_store:
#             history_store[user_id_for_history] = []

#         history_item_id = str(uuid.uuid4()) # Generate a unique ID for this blog entry
#         history_item = {
#             "id": history_item_id, # Use this ID for DynamoDB as well
#             "brief": payload["topic"], # Store full brief now
#             "language": lang,
#             "tone": payload["tone"],
#             "audience": payload["audience"],
#             "version": f"v{len([h for h in history_store.get(user_id_for_history, []) if h['brief'] == payload['topic']]) + 1}.0", # Calculate version based on full brief match
#             "result_text": content or "", # Use fetched content if available
#             "summary_text": result.get("summary", "Summary not provided"),
#             # Removed preview text, can be derived on frontend if needed
#             "quality_score": float(result.get("quality_score", 0.0)), # Default to 0.0 if missing
#             "created_at": datetime.utcnow().isoformat() + "Z",
#             "s3_key": s3_key # Store the S3 key if it exists
#         }
#         history_store[user_id_for_history].append(history_item)
#         logger.info(f"Stored history item '{history_item_id}' for user/session '{user_id_for_history}'")


#         # --- Save to DynamoDB ---
#         if blogs_table and actual_user_id: # Only save if table exists and user is logged in (not trial)
#             try:
#                 dynamo_item = {
#                     'blog_id': history_item_id, # Use history ID as primary key (Partition Key)
#                     'user_id': actual_user_id, # Add user_id (Could be a Sort Key or GSI key if needed for queries)
#                     'brief': history_item['brief'],
#                     'language': history_item['language'],
#                     'tone': history_item['tone'],
#                     'audience': history_item['audience'],
#                     'version': history_item['version'],
#                     'content': history_item['result_text'], # Store full content
#                     'summary': history_item['summary_text'],
#                     'quality_score': str(history_item['quality_score']), # DynamoDB prefers strings for numbers sometimes, or use Decimal
#                     'created_at': history_item['created_at'],
#                     's3_key': history_item.get('s3_key', None) # Include S3 key if present
#                 }
#                 # Remove keys with None values as DynamoDB doesn't like them
#                 dynamo_item = {k: v for k, v in dynamo_item.items() if v is not None}

#                 blogs_table.put_item(Item=dynamo_item)
#                 logger.info(f"Successfully saved blog '{history_item_id}' to DynamoDB for user '{actual_user_id}'.")
#             except ClientError as e:
#                 logger.error(f"Error saving blog '{history_item_id}' to DynamoDB: {e.response['Error']['Message']}")
#                 # Continue execution, but log the error. Don't fail the whole request.
#             except Exception as e:
#                  logger.error(f"Unexpected error saving blog '{history_item_id}' to DynamoDB: {str(e)}")
#                  # Continue execution
#         elif not actual_user_id:
#              logger.info(f"Skipping DynamoDB save for trial user content '{history_item_id}'.")
#         elif not blogs_table:
#              logger.warning(f"DynamoDB table not initialized. Skipping save for blog '{history_item_id}'.")
#         # --- End Save to DynamoDB ---


#         # Important: Return the potentially updated 'results' dictionary
#         # which now includes the content fetched from S3 if applicable.
#         response_payload = {"results": {lang: result}}

#         response = jsonify(response_payload)
#         response.headers["X-Response-Source"] = "generate-blog"
#         return response, 200

#     except requests.exceptions.Timeout:
#         error_message = "Error calling API Gateway: Request timed out."
#         logger.error(error_message)
#         return jsonify({"error": error_message}), 504 # Gateway Timeout
#     except requests.exceptions.RequestException as e:
#         error_message = f"Error calling API Gateway: {str(e)}"
#         logger.error(error_message)
#         # Attempt to get status code from underlying response if possible
#         status_code = e.response.status_code if hasattr(e, 'response') and e.response is not None else 500
#         return jsonify({"error": error_message}), status_code
#     except Exception as e:
#         error_message = f"Unexpected error in generate-blog: {str(e)}"
#         logger.error(error_message, exc_info=True) # Log traceback for unexpected errors
#         return jsonify({"error": "An internal server error occurred."}), 500


# @app.route('/history', methods=['GET'])
# def get_history():
#     """Returns the list of stored history items for the logged-in user."""
#     user_id = session.get('user_id')
#     if not user_id:
#         # Check if it was a trial user asking (though we don't persist trial history)
#         if session.get('trial_used'):
#              return jsonify({"error": "Login required to view persistent history"}), 401
#         else:
#              return jsonify({"error": "Not logged in"}), 401


#     # --- Optionally fetch history from DynamoDB instead of in-memory ---
#     # This part depends on how you want to manage history.
#     # If you want DynamoDB to be the source of truth for logged-in users:
#     # try:
#     #     if blogs_table:
#     #         # Note: Querying requires user_id to be part of the key or an index.
#     #         # Assuming user_id is NOT the partition key, you might need a GSI or Scan.
#     #         # Scan is less efficient for large tables. Let's assume a GSI on user_id exists.
#     #         # Replace 'user_id-index' with your actual Global Secondary Index name.
#     #         response = blogs_table.query(
#     #             IndexName='user_id-index', # Example GSI name
#     #             KeyConditionExpression=boto3.dynamodb.conditions.Key('user_id').eq(user_id)
#     #         )
#     #         user_history_from_db = response.get('Items', [])
#     #         # Convert DynamoDB items back to your history_item format if needed
#     #         user_history = sorted(user_history_from_db, key=lambda x: x['created_at'], reverse=True) # Sort by date
#     #         logger.info(f"Fetched {len(user_history)} history items from DynamoDB for user {user_id}")
#     #     else:
#     #         logger.warning("DynamoDB table not available, falling back to in-memory history.")
#     #         user_history = history_store.get(user_id, [])
#     # except ClientError as e:
#     #     logger.error(f"Error fetching history from DynamoDB for user {user_id}: {e.response['Error']['Message']}")
#     #     user_history = history_store.get(user_id, []) # Fallback to in-memory
#     # except Exception as e:
#     #     logger.error(f"Unexpected error fetching history from DynamoDB: {str(e)}")
#     #     user_history = history_store.get(user_id, []) # Fallback to in-memory
#     # --- End Optional DynamoDB Fetch ---

#     # --- Using In-Memory History (as originally implemented) ---
#     user_history = history_store.get(user_id, [])
#     # --- End In-Memory History ---


#     try:
#         # Ensure quality_score is a float for JSON serialization if needed
#         # (It was already converted before storing in history_store)
#         for item in user_history:
#              # Add any necessary type conversions if fetching from DynamoDB directly
#              if 'quality_score' in item and not isinstance(item['quality_score'], (int, float)):
#                  try:
#                     item['quality_score'] = float(item['quality_score'])
#                  except (ValueError, TypeError):
#                     item['quality_score'] = 0.0 # Default if conversion fails


#         logger.info("Returning %d history items for user %s", len(user_history), user_id)
#         response = jsonify(user_history)
#         response.headers["X-History-Count"] = len(user_history)
#         response.headers["X-Server-Time"] = datetime.utcnow().isoformat() + "Z"
#         response.headers["X-Response-Source"] = "history"
#         return response, 200
#     except Exception as e:
#         error_message = f"Error preparing history response: {str(e)}"
#         logger.error(error_message, exc_info=True)
#         response = jsonify({"error": "Failed to retrieve history."})
#         response.headers["X-Error-Details"] = str(e)
#         response.headers["X-Response-Source"] = "history-error"
#         return response, 500


# if __name__ == '__main__':
#     # Use environment variable for port, default to 5000
#     port = int(os.environ.get('PORT', 5000))
#     # Debug mode controlled by FLASK_DEBUG env var (or default to True if FLASK_ENV=development)
#     debug_mode = os.environ.get('FLASK_DEBUG', '1' if os.environ.get('FLASK_ENV') == 'development' else '0') == '1'
#     app.run(host="0.0.0.0", port=port, debug=debug_mode)







import os
import json
import requests
from flask import Flask, request, jsonify, render_template, session
from flask_cors import CORS
from dotenv import load_dotenv
from datetime import datetime
import uuid
import logging
import boto3
from botocore.exceptions import ClientError, NoCredentialsError, PartialCredentialsError
import bcrypt

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
# DYNAMODB_USERS_TABLE_NAME removed
S3_BUCKET = os.getenv("S3_BUCKET", "agentx-blog") # Bucket for users.json and potentially blog content

# --- AWS Clients Initialization ---
try:
    # S3 Client (for users.json and blog content)
    s3_client = boto3.client('s3', region_name=AWS_REGION)
    logger.info(f"S3 Client initialized for region {AWS_REGION}.")

    # DynamoDB (only for blogs table)
    dynamodb = boto3.resource('dynamodb', region_name=AWS_REGION)
    blogs_table = dynamodb.Table(DYNAMODB_BLOGS_TABLE_NAME)
    blogs_table.load() # Check if table exists on load
    logger.info(f"Successfully connected to DynamoDB blogs table: {DYNAMODB_BLOGS_TABLE_NAME}")

except (NoCredentialsError, PartialCredentialsError):
    logger.error("AWS credentials not found. Ensure credentials are configured.")
    s3_client = None
    dynamodb = None
    blogs_table = None
except ClientError as e:
    logger.error(f"Error connecting to AWS services: {e.response['Error']['Message']}")
    s3_client = None
    dynamodb = None
    blogs_table = None
except Exception as e:
    logger.error(f"An unexpected error occurred during AWS initialization: {str(e)}")
    s3_client = None
    dynamodb = None
    blogs_table = None
# --- End AWS Clients Initialization ---

# --- S3 User Functions (Reinstated) ---
USERS_S3_KEY = 'users/users.json' # Define the path within the bucket

def load_users():
    """Loads user data from the JSON file in S3."""
    if not s3_client:
        logger.error("S3 client not initialized. Cannot load users.")
        return []
    try:
        obj = s3_client.get_object(Bucket=S3_BUCKET, Key=USERS_S3_KEY)
        users_data = obj['Body'].read().decode('utf-8')
        logger.info(f"Successfully loaded users from s3://{S3_BUCKET}/{USERS_S3_KEY}")
        return json.loads(users_data) if users_data else []
    except ClientError as e:
        if e.response['Error']['Code'] == 'NoSuchKey':
            logger.warning(f"Users file '{USERS_S3_KEY}' not found in bucket '{S3_BUCKET}'. Returning empty list.")
            return [] # Return empty list if file doesn't exist
        else:
            logger.error(f"Error loading users from S3: {e.response['Error']['Message']}")
            return [] # Return empty list on other errors
    except Exception as e:
        logger.error(f"Unexpected error loading users from S3: {str(e)}")
        return []

def save_users(users):
    """Saves the user list as a JSON file to S3."""
    if not s3_client:
        logger.error("S3 client not initialized. Cannot save users.")
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
# --- End S3 User Functions ---

# In-memory history store
history_store = {}

@app.before_request
def log_request_info():
    logger.info(f"Incoming request: {request.method} {request.path} from {request.remote_addr}")

@app.route('/')
def index():
    logger.info("Serving index.html")
    return render_template('index.html')

@app.route('/signup', methods=['POST'])
def signup():
    """Handles user signup and stores in S3."""
    if not s3_client:
         return jsonify({"error": "User storage service unavailable."}), 503

    data = request.get_json()
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')

    if not all([username, email, password]):
        return jsonify({"error": "Missing required fields: username, email, password"}), 400

    users = load_users() # Load current users from S3

    # Check for duplicates
    if any(u['username'] == username for u in users):
        return jsonify({"error": "Username already exists"}), 400
    if any(u['email'] == email for u in users):
        return jsonify({"error": "Email already exists"}), 400

    # Hash password
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    user_id = str(uuid.uuid4())
    timestamp = datetime.utcnow().isoformat() + "Z"

    new_user = {
        "id": user_id, # Keep a unique ID
        "username": username,
        "email": email,
        "password_hash": hashed_password,
        "created_at": timestamp,
        "trial_used": False
    }
    users.append(new_user)

    if save_users(users): # Save updated list back to S3
        session['user_id'] = user_id
        logger.info(f"User signed up and saved to S3: {username} (ID: {user_id})")
        return jsonify({"message": "Signup successful", "user_id": user_id, "username": username}), 201
    else:
        logger.error(f"Failed to save updated user list to S3 for signup {username}.")
        return jsonify({"error": "Failed to create user account. Please try again later."}), 500

@app.route('/login', methods=['POST'])
def login():
    """Handles user login using user data from S3."""
    if not s3_client:
         return jsonify({"error": "User storage service unavailable."}), 503

    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if not all([username, password]):
        return jsonify({"error": "Missing required fields: username, password"}), 400

    users = load_users() # Load users from S3
    user = next((u for u in users if u['username'] == username), None)

    if not user:
        logger.warning(f"Login attempt failed: Username '{username}' not found in S3 data.")
        return jsonify({"error": "Invalid username or password"}), 401

    # Check password
    if bcrypt.checkpw(password.encode('utf-8'), user['password_hash'].encode('utf-8')):
        session['user_id'] = user['id']
        logger.info(f"User logged in: {username} (ID: {user['id']})")

        # If trial was used anonymously before login, update the user record in the list and save back to S3
        if session.get('trial_used') and not user.get('trial_used'):
            user['trial_used'] = True # Modify the user dict in the list
            if not save_users(users): # Save the whole list back
                 logger.error(f"Failed to update trial_used status in S3 for user {username} after login.")
                 # Non-critical error for login itself, but log it.
            else:
                 logger.info(f"Marked trial_used=true in S3 for user {username} after login.")

        return jsonify({"message": "Login successful", "user_id": user['id'], "username": user['username']}), 200
    else:
        logger.warning(f"Login attempt failed: Incorrect password for username '{username}'.")
        return jsonify({"error": "Invalid username or password"}), 401

@app.route('/logout', methods=['POST'])
def logout():
    user_id = session.pop('user_id', None)
    session.pop('trial_used', None)
    logger.info(f"User logged out: ID {user_id}" if user_id else "User logged out (no session found)")
    return jsonify({"message": "Logout successful"}), 200

@app.route('/check-session', methods=['GET'])
def check_session():
    """Checks session and verifies user_id against user data from S3."""
    user_id = session.get('user_id')
    if user_id:
        if not s3_client:
             logger.error("check_session: S3 client unavailable.")
             session.pop('user_id', None) # Clear potentially invalid session
             return jsonify({"isLoggedIn": False, "trial_available": not session.get('trial_used', False)}), 200

        users = load_users() # Load users from S3
        user = next((u for u in users if u.get('id') == user_id), None)

        if user:
            logger.info(f"check_session: Valid session found for user {user['username']}")
            return jsonify({"isLoggedIn": True, "username": user['username']}), 200
        else:
            # User ID in session but not found in S3 data - clear session
            session.pop('user_id', None)
            logger.warning(f"check_session: User ID {user_id} found in session but not in S3 data. Cleared session.")

    # If we reached here, user is not logged in
    logger.info("check_session: No valid session found.")
    return jsonify({
        "isLoggedIn": False,
        "trial_available": not session.get('trial_used', False)
    }), 200

def check_auth():
    """Check if user is authenticated (session valid against S3 data) or has trial available."""
    user_id = session.get('user_id')
    if user_id:
        # Optional: Add an S3 check here for extra validation if desired, but check_session should handle it.
        # users = load_users()
        # if any(u.get('id') == user_id for u in users):
        #      return True, user_id
        # else: # Invalid session
        #      session.pop('user_id', None)
        #      return False, None
        return True, user_id # Relying on check_session having validated it recently

    # Check trial
    if not session.get('trial_used'):
        return True, None # Allow trial
    return False, None


# --- generate_blog function remains the same, saving blog details to DynamoDB 'blogs' table ---
@app.route('/generate-blog', methods=['POST'])
def generate_blog():
    """Handles blog generation, calls API Gateway, stores result in history, and saves to DynamoDB blogs table."""
    is_auth, user_id = check_auth() # Uses the S3-based check_auth
    if not is_auth:
        return jsonify({"error": "Login required. You've used your free trial."}), 401

    actual_user_id = user_id # Keep track of the real user ID if logged in

    data = request.get_json()
    # ...(Input validation remains the same)...
    if not data or not data.get("topic"):
        # ... (rest of validation) ...
        return jsonify({"error": "Missing 'topic' in request body"}), 400
    if not data.get("language"):
        # ... (rest of validation) ...
        return jsonify({"error": "A language must be selected"}), 400
    try:
        tone_intensity = int(data.get("tone_intensity", 5))
        if not (1 <= tone_intensity <= 10):
             return jsonify({"error": "Tone intensity must be between 1 and 10"}), 400
        word_count = int(data.get("word_count", 500))
        if not (200 <= word_count <= 2000):
            return jsonify({"error": "Word count must be between 200 and 2000"}), 400
    except ValueError as e:
        return jsonify({"error": "Tone intensity and word count must be valid numbers"}), 400
    keywords = data.get("keywords", "").split(",") if data.get("keywords") else []
    keywords = [k.strip() for k in keywords if k.strip()]
    if len(keywords) > 5:
        return jsonify({"error": "Maximum 5 keywords allowed"}), 400
    if not API_GATEWAY_URL:
        return jsonify({"error": "API Gateway URL not configured"}), 500


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

    try:
        headers = {'Content-Type': 'application/json'}
        response = requests.post(API_GATEWAY_URL, data=json.dumps(payload), headers=headers, timeout=90)
        response.raise_for_status()
        api_response = response.json()
        logger.info("API Gateway response: %s", api_response)

        results = api_response.get("results", {})
        if not results:
             return jsonify({"error": "Content generation failed (no results)."}), 500

        lang = payload["language"]
        result = results.get(lang) # Use .get for safety

        # Handle missing language, try to find another
        if not result:
            logger.error("No content generated for language: %s", lang)
            first_available_lang = next(iter(results)) if results else None
            if first_available_lang:
                logger.warning(f"Requested language '{lang}' not found, returning '{first_available_lang}' instead.")
                lang = first_available_lang
                result = results[lang]
            else:
                 return jsonify({"error": f"No content generated for the requested language '{lang}' or any other."}), 500


        s3_key = result.get("s3_key")
        content = result.get("content")

        # --- Fetch content from S3 if only key is present ---
        if s3_key and not content:
            # ...(S3 fetch logic remains the same)...
            logger.info(f"Content for {lang} is on S3 ({s3_key}), fetching...")
            try:
                if not s3_client: raise ConnectionError("S3 client not available.")
                s3_obj = s3_client.get_object(Bucket=S3_BUCKET, Key=s3_key)
                content = s3_obj['Body'].read().decode('utf-8')
                result["content"] = content
                logger.info(f"Successfully fetched content from S3 key: {s3_key}")
            except (ClientError, ConnectionError) as e:
                error_message = f"Failed to fetch content from S3 ({s3_key}): {str(e)}"
                logger.error(error_message)
                return jsonify({"error": error_message}), 500
            except Exception as e:
                error_message = f"Unexpected error fetching from S3 ({s3_key}): {str(e)}"
                logger.error(error_message)
                return jsonify({"error": error_message}), 500
        # --- End S3 Fetch ---

        if not content and not s3_key: # Check again after potential S3 fetch
             logger.error("No content or S3 key found for language: %s", lang)
             return jsonify({"error": f"Content generation failed (missing content and S3 key for language {lang})."}), 500


        # Store in in-memory history
        if actual_user_id is None: # Trial user
            session['trial_used'] = True
            user_id_for_history = 'trial_'
            logger.info("Trial user generated content. History not saved persistently.")
            history_item_id = str(uuid.uuid4()) # Still need an ID for DynamoDB if we were saving trial blogs
        else:
            user_id_for_history = actual_user_id

            if user_id_for_history not in history_store:
                history_store[user_id_for_history] = []

            history_item_id = str(uuid.uuid4())
            history_item = {
                "id": history_item_id,
                "brief": payload["topic"],
                "language": lang,
                "tone": payload["tone"],
                "audience": payload["audience"],
                "version": f"v{len([h for h in history_store.get(user_id_for_history, []) if h['brief'] == payload['topic']]) + 1}.0",
                "result_text": content or "",
                "summary_text": result.get("summary", "Summary not provided"),
                "quality_score": float(result.get("quality_score", 0.0)),
                "created_at": datetime.utcnow().isoformat() + "Z",
                "s3_key": s3_key
            }
            history_store[user_id_for_history].append(history_item)
            logger.info(f"Stored in-memory history item '{history_item_id}' for user '{user_id_for_history}'")


            # --- Save Blog to DynamoDB (only for logged-in users) ---
            if blogs_table:
                # ...(DynamoDB saving logic for blogs table remains the same)...
                try:
                    dynamo_item = {
                        'blog_id': history_item_id,
                        'user_id': actual_user_id,
                        'brief': history_item['brief'],
                        'language': history_item['language'],
                        'tone': history_item['tone'],
                        'audience': history_item['audience'],
                        'version': history_item['version'],
                        'content': history_item['result_text'],
                        'summary': history_item['summary_text'],
                        'quality_score': str(history_item['quality_score']),
                        'created_at': history_item['created_at'],
                        's3_key': history_item.get('s3_key', None)
                    }
                    dynamo_item = {k: v for k, v in dynamo_item.items() if v is not None}
                    blogs_table.put_item(Item=dynamo_item)
                    logger.info(f"Successfully saved blog '{history_item_id}' to DynamoDB for user '{actual_user_id}'.")
                except ClientError as e:
                    logger.error(f"Error saving blog '{history_item_id}' to DynamoDB: {e.response['Error']['Message']}")
                except Exception as e:
                     logger.error(f"Unexpected error saving blog '{history_item_id}' to DynamoDB: {str(e)}")
            else:
                 logger.warning(f"DynamoDB blogs table not initialized. Skipping save for blog '{history_item_id}'.")
            # --- End Save Blog to DynamoDB ---

        # Important: Return the potentially updated 'results' dictionary
        response_payload = {"results": {lang: result}}
        response = jsonify(response_payload)
        response.headers["X-Response-Source"] = "generate-blog"
        return response, 200

    except requests.exceptions.Timeout:
        error_message = "Error calling API Gateway: Request timed out."
        logger.error(error_message)
        return jsonify({"error": error_message}), 504
    except requests.exceptions.RequestException as e:
        error_message = f"Error calling API Gateway: {str(e)}"
        logger.error(error_message)
        status_code = e.response.status_code if hasattr(e, 'response') and e.response is not None else 500
        return jsonify({"error": error_message}), status_code
    except Exception as e:
        error_message = f"Unexpected error in generate-blog: {str(e)}"
        logger.error(error_message, exc_info=True)
        return jsonify({"error": "An internal server error occurred."}), 500


# --- /history endpoint still uses DynamoDB 'blogs' table ---
@app.route('/history', methods=['GET'])
def get_history():
    """Returns the list of stored history items for the logged-in user FROM DYNAMODB BLOGS TABLE."""
    user_id = session.get('user_id')
    if not user_id:
         return jsonify({"error": "Login required to view history"}), 401

    if not blogs_table:
        logger.error("History endpoint called but DynamoDB blogs table is not initialized.")
        return jsonify({"error": "History service is temporarily unavailable."}), 503

    try:
        # Querying requires user_id to be part of the key or an index.
        # Assuming user_id is NOT the partition key, you need a GSI or Scan.
        # Scan is less efficient. Let's assume a GSI on user_id exists.
        # Replace 'user_id-index' with your actual GSI name on the 'blogs' table.
        response = blogs_table.query(
             IndexName='user_id-index', # Example GSI name on the 'blogs' table
             KeyConditionExpression=Key('user_id').eq(user_id)
        )
        items_from_db = response.get('Items', [])

        # Convert DynamoDB items back to the format expected by the frontend history
        user_history = []
        for item in items_from_db:
             history_item = {
                "id": item.get('blog_id'), # Use blog_id from DB as history item ID
                "brief": item.get('brief'),
                "language": item.get('language'),
                "tone": item.get('tone'),
                "audience": item.get('audience'),
                "version": item.get('version'),
                "result_text": item.get('content', ''), # Ensure content is present
                "summary_text": item.get('summary', "Summary not provided"),
                "quality_score": 0.0, # Default
                "created_at": item.get('created_at'),
                "s3_key": item.get('s3_key')
             }
             # Safely convert quality_score
             try:
                 qs = item.get('quality_score')
                 if qs is not None:
                     history_item['quality_score'] = float(qs)
             except (ValueError, TypeError):
                 logger.warning(f"Could not convert quality_score '{qs}' to float for blog {item.get('blog_id')}")

             user_history.append(history_item)


        # Sort by creation date descending
        user_history.sort(key=lambda x: x.get('created_at', ''), reverse=True)

        logger.info(f"Fetched {len(user_history)} history items from DynamoDB for user {user_id}")

    except ClientError as e:
        if 'ResourceNotFoundException' in str(e) and 'user_id-index' in str(e):
             logger.error(f"DynamoDB GSI 'user_id-index' not found on table '{DYNAMODB_BLOGS_TABLE_NAME}'. Cannot fetch history efficiently.")
             return jsonify({"error": "History service configuration error. Index missing."}), 500
        logger.error(f"Error fetching history from DynamoDB for user {user_id}: {e.response['Error']['Message']}")
        return jsonify({"error": "Failed to retrieve history due to a database error."}), 500
    except Exception as e:
        logger.error(f"Unexpected error fetching history from DynamoDB: {str(e)}", exc_info=True)
        return jsonify({"error": "An internal error occurred while retrieving history."}), 500
    # --- End DynamoDB History Fetch ---


    # --- Prepare and Return Response ---
    try:
        response = jsonify(user_history)
        response.headers["X-History-Count"] = len(user_history)
        response.headers["X-Server-Time"] = datetime.utcnow().isoformat() + "Z"
        response.headers["X-Response-Source"] = "history-dynamodb"
        return response, 200
    except Exception as e:
        error_message = f"Error preparing history response: {str(e)}"
        logger.error(error_message, exc_info=True)
        response = jsonify({"error": "Failed to format history response."})
        response.headers["X-Error-Details"] = str(e)
        response.headers["X-Response-Source"] = "history-error"
        return response, 500
    # --- End Prepare and Return Response ---

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug_mode = os.environ.get('FLASK_DEBUG', '1' if os.environ.get('FLASK_ENV') == 'development' else '0') == '1'
    app.run(host="0.0.0.0", port=port, debug=debug_mode)