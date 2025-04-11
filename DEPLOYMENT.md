# Deploying TaskIQ Auth Server to Vercel

This guide provides step-by-step instructions for deploying the TaskIQ Auth Server to Vercel.

## Prerequisites

1. A Vercel account (sign up at [vercel.com](https://vercel.com) if you don't have one)
2. Vercel CLI installed (optional, but recommended for easier deployment)
3. Google Cloud Console project with OAuth 2.0 credentials
4. A domain (e.g., taskiq.io) that you want to use for the auth server

## Steps for Deployment

### 1. Prepare Your Project

Make sure your project structure is as follows:
```
auth_server/
├── app.py
├── requirements.txt
├── vercel.json
├── .gauth.json
├── .env
└── tokens/ (directory)
```

### 2. Update Google Cloud Console Configuration

1. Go to the [Google Cloud Console](https://console.cloud.google.com/)
2. Select your project
3. Navigate to "APIs & Services" > "Credentials"
4. Edit your OAuth 2.0 Client ID
5. Add your production redirect URI to the list of authorized redirect URIs:
   ```
   https://taskiq.io/auth/google
   ```
   or if using a Vercel subdomain:
   ```
   https://your-project-name.vercel.app/auth/google
   ```

### 3. Update Environment Configuration

1. In your `.env` file, make sure the `REDIRECT_URI` is set to your production URL:
   ```
   REDIRECT_URI="https://taskiq.io/auth/google"
   ```

2. Update the `vercel.json` file if needed:
   ```json
   {
     "version": 2,
     "builds": [
       {
         "src": "app.py",
         "use": "@vercel/python"
       }
     ],
     "routes": [
       {
         "src": "/(.*)",
         "dest": "app.py"
       }
     ],
     "env": {
       "CLIENT_SECRETS_FILE": ".gauth.json",
       "REDIRECT_URI": "https://taskiq.io/auth/google",
       "TOKEN_STORAGE_DIR": "./tokens"
     }
   }
   ```

### 4. Deploy with Vercel CLI (Recommended)

1. Install Vercel CLI if you haven't already:
   ```bash
   npm install -g vercel
   ```

2. Log in to Vercel:
   ```bash
   vercel login
   ```

3. Navigate to your project directory:
   ```bash
   cd taskiq_backend/auth_server
   ```

4. Deploy to Vercel:
   ```bash
   vercel
   ```

5. Follow the CLI prompts:
   - Set up and deploy project? Yes
   - Link to existing project? No
   - Project name? taskiq-auth
   - Directory? ./
   - Want to override settings? No

6. For production deployment:
   ```bash
   vercel --prod
   ```

### 5. Deploy with Vercel Dashboard (Alternative)

1. Create a new Git repository and push your code to it.

2. Log in to the [Vercel Dashboard](https://vercel.com/dashboard).

3. Click "New Project" and import your Git repository.

4. Configure the project:
   - Framework Preset: Other
   - Root Directory: auth_server (if your repo has multiple projects)
   - Build Command: (leave empty)
   - Output Directory: (leave empty)

5. Add environment variables (same as in vercel.json):
   - `CLIENT_SECRETS_FILE`: `.gauth.json`
   - `REDIRECT_URI`: `https://taskiq.io/auth/google`
   - `TOKEN_STORAGE_DIR`: `./tokens`

6. Deploy the project.

### 6. Set Up Custom Domain (Optional)

1. In the Vercel Dashboard, go to your project.

2. Navigate to "Settings" > "Domains".

3. Add your custom domain (e.g., `auth.taskiq.io`).

4. Follow the instructions to configure your DNS settings.

### 7. Testing

1. Visit your deployed site's root URL to check if it's running:
   ```
   https://taskiq.io/
   ```
   or
   ```
   https://your-project-name.vercel.app/
   ```

2. Test the auth flow by generating an auth URL:
   ```
   https://taskiq.io/generate-auth-url?email=test@example.com
   ```

### 8. Update TaskIQ Bot Configuration

1. In your bot's configuration, update the `AUTH_SERVER_URL` environment variable to your new server URL:
   ```
   AUTH_SERVER_URL=https://taskiq.io
   ```

## Notes and Limitations

### Token Storage

Vercel functions are serverless and don't maintain persistent storage between requests. The current implementation saves tokens to a directory (`./tokens`), which will work for immediate use but may not persist between deployments.

For a production setup, consider using:
- Vercel KV (key-value storage)
- A cloud database (e.g., MongoDB Atlas)
- A cloud storage solution (e.g., AWS S3)

### Security Considerations

1. The current implementation doesn't include authentication for the token endpoints. For production, consider adding:
   - API keys for token endpoints
   - JWT authentication
   - IP restrictions

2. Keep your `.gauth.json` file secure. For production, you might want to:
   - Use environment variables for client ID and secret instead of a file
   - Set up proper secrets management in Vercel

## Troubleshooting

### Error: Function Not Found

If you get a "Function Not Found" error, check that your `vercel.json` file is correctly configured.

### OAuth Redirect URI Mismatch

If you get a "redirect_uri_mismatch" error:
1. Double-check that the redirect URI in your Google Cloud Console matches exactly with the one in your `.env` and `vercel.json` files.
2. Make sure to include the protocol (https://) and the exact path (/auth/google).

### Missing Dependencies

If your deployment fails due to missing dependencies, verify that all required packages are listed in `requirements.txt`.
