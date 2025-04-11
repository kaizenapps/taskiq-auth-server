import os
import json
from datetime import datetime
from typing import Dict, Optional, Any

from fastapi import FastAPI, HTTPException, Request, Response
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from pydantic import BaseModel
import httpx

from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = FastAPI(title="TaskIQ Auth Server")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuration
CLIENT_SECRETS_FILE = os.getenv("CLIENT_SECRETS_FILE", "../.gauth.json")
SCOPES = [
    "openid",
    "https://www.googleapis.com/auth/userinfo.email",
    "https://mail.google.com/",
    "https://www.googleapis.com/auth/calendar"
]
REDIRECT_URI = os.getenv("REDIRECT_URI", "https://taskiq.io/auth/google")
TOKEN_STORAGE_DIR = os.getenv("TOKEN_STORAGE_DIR", "./tokens")

# Ensure token directory exists
os.makedirs(TOKEN_STORAGE_DIR, exist_ok=True)

# Pydantic models
class TokenRequest(BaseModel):
    user_id: str
    code: str

class TokenResponse(BaseModel):
    token: Dict[str, Any]
    expires_at: str
    success: bool
    message: str

# Helper functions
def get_flow() -> Flow:
    """Create and configure an OAuth flow object."""
    try:
        flow = Flow.from_client_secrets_file(
            CLIENT_SECRETS_FILE,
            scopes=SCOPES,
            redirect_uri=REDIRECT_URI
        )
        return flow
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create OAuth flow: {str(e)}")

def save_token(user_id: str, credentials: Credentials) -> str:
    """Save user credentials to file storage."""
    try:
        token_path = os.path.join(TOKEN_STORAGE_DIR, f"{user_id.replace('@', '_at_')}.json")
        token_data = {
            "token": credentials.to_json(),
            "created_at": datetime.now().isoformat(),
        }
        with open(token_path, "w") as f:
            json.dump(token_data, f)
        return token_path
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save token: {str(e)}")

def get_user_info(credentials: Credentials) -> Dict[str, Any]:
    """Get user information from Google's UserInfo API."""
    try:
        userinfo_url = "https://www.googleapis.com/oauth2/v2/userinfo"
        headers = {"Authorization": f"Bearer {credentials.token}"}
        response = httpx.get(userinfo_url, headers=headers)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get user info: {str(e)}")

# Routes
@app.get("/")
def read_root():
    """Root endpoint."""
    return {"message": "TaskIQ Auth Server is running"}

@app.get("/auth/google")
async def auth_callback(request: Request, code: Optional[str] = None, state: Optional[str] = None, error: Optional[str] = None):
    """Handle OAuth 2.0 callback from Google."""
    if error:
        error_html = f"""
        <html>
            <head><title>Authentication Error</title></head>
            <body>
                <h1>Authentication Error</h1>
                <p>Error: {error}</p>
                <p>Please close this window and try again.</p>
            </body>
        </html>
        """
        return HTMLResponse(content=error_html, status_code=400)
    
    if not code:
        return HTMLResponse(content="No authorization code received", status_code=400)
    
    try:
        # Get the OAuth flow
        flow = get_flow()
        
        # Exchange the authorization code for credentials
        flow.fetch_token(code=code)
        credentials = flow.credentials
        
        # Get user info to retrieve the email
        user_info = get_user_info(credentials)
        user_email = user_info.get("email")
        
        if not user_email:
            return HTMLResponse(content="Could not retrieve user email", status_code=400)
        
        # Save the token
        token_path = save_token(user_email, credentials)
        
        # Return a success page
        success_html = f"""
        <html>
            <head><title>Authentication Successful</title></head>
            <body>
                <h1>Authentication Successful</h1>
                <p>You have successfully authenticated with Google.</p>
                <p>Email: {user_email}</p>
                <p>You may now close this window and return to TaskIQ.</p>
                <script>
                    // Send message to telegram bot (if opened through Telegram)
                    if (window.TelegramWebviewProxy) {{
                        window.TelegramWebviewProxy.postEvent('auth_complete', {{
                            email: '{user_email}',
                            success: true
                        }});
                    }}
                </script>
            </body>
        </html>
        """
        return HTMLResponse(content=success_html)
        
    except Exception as e:
        error_message = str(e)
        error_html = f"""
        <html>
            <head><title>Authentication Error</title></head>
            <body>
                <h1>Authentication Error</h1>
                <p>Error: {error_message}</p>
                <p>Please close this window and try again.</p>
            </body>
        </html>
        """
        return HTMLResponse(content=error_html, status_code=500)

@app.get("/generate-auth-url")
def generate_auth_url(email: str):
    """Generate an OAuth 2.0 authorization URL for a user."""
    try:
        flow = get_flow()
        auth_url, _ = flow.authorization_url(
            access_type='offline',
            include_granted_scopes='true',
            prompt='consent'
        )
        
        # Store the email along with the state parameter for later use
        # (In a production app, this would be stored in a database)
        
        return {"auth_url": auth_url, "email": email}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate auth URL: {str(e)}")

@app.get("/token/{user_id}")
def get_token(user_id: str):
    """Check if a user has a valid token."""
    token_path = os.path.join(TOKEN_STORAGE_DIR, f"{user_id.replace('@', '_at_')}.json")
    
    if not os.path.exists(token_path):
        return {"has_token": False, "message": "No token found for user"}
    
    try:
        with open(token_path, "r") as f:
            token_data = json.load(f)
        
        # Check if token exists and is potentially valid
        return {
            "has_token": True,
            "created_at": token_data.get("created_at"),
            "message": "Token found for user"
        }
    except Exception as e:
        return {"has_token": False, "message": f"Error reading token: {str(e)}"}

# For local development
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)
