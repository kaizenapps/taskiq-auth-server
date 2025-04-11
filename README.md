# TaskIQ Auth Server

A FastAPI server that handles OAuth 2.0 authentication with Google APIs for TaskIQ. This server can be deployed to Vercel or any other serverless platform.

## Features

- Google OAuth 2.0 authentication flow
- Token storage and management
- API endpoints for authentication and token status
- Easy deployment to Vercel

## Setup

1. Ensure you have the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Make sure you have a `.gauth.json` file with your Google OAuth credentials in the project directory.

3. Update the `.env` file with your configuration:
   ```
   CLIENT_SECRETS_FILE=".gauth.json"
   REDIRECT_URI="https://taskiq.io/auth/google"
   TOKEN_STORAGE_DIR="./tokens"
   ```

## Local Development

To run the server locally:

```bash
uvicorn app:app --reload --host 0.0.0.0 --port 8000
```

or simply:

```bash
python app.py
```

The server will be available at http://localhost:8000.

## API Endpoints

- `GET /`: Check if the server is running
- `GET /generate-auth-url?email={email}`: Generate an OAuth URL for a user
- `GET /auth/google`: OAuth callback endpoint (redirect URI)
- `GET /token/{user_id}`: Check if a user has a valid token

## Deploying to Vercel

1. Install the Vercel CLI:
   ```bash
   npm install -g vercel
   ```

2. Log in to Vercel:
   ```bash
   vercel login
   ```

3. Deploy the project:
   ```bash
   vercel
   ```

4. For production deployment:
   ```bash
   vercel --prod
   ```

## Important Notes

1. Update Google Cloud Console settings:
   - Add your production domain (e.g., `https://taskiq.io/auth/google`) to the authorized redirect URIs in the Google Cloud Console.

2. For production, consider:
   - Using a more secure token storage solution
   - Adding authentication to protect the API endpoints
   - Implementing proper error handling and logging

## Integration with TaskIQ Bot

To use this auth server with the TaskIQ Telegram bot:

1. Update the bot to use the auth server URL for generating authentication links
2. Update the relevant handlers to check token status via the `/token/{user_id}` endpoint
3. Use the saved tokens to authenticate API requests to Google services
