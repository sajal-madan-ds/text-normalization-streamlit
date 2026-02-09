# 🚀 Deployment Guide: TTS Text Normalization to Streamlit Cloud

Follow these steps to deploy your app to Streamlit Cloud.

## Step 1: Create GitHub Repository

1. **On the GitHub page you have open:**
   - **Repository name**: Enter `text-normalization-streamlit` (or any name you prefer)
   - **Description**: "TTS Text Normalization - Convert numbers to words for Text-to-Speech"
   - **Visibility**: Keep it **Public** (or Private if you prefer)
   - **DO NOT** check "Add README" (we already have one)
   - **DO NOT** add .gitignore (we already have one)
   - **DO NOT** add license (optional)
   - Click **"Create repository"** button

## Step 2: Initialize Git and Push Code

Open your terminal in the project directory and run these commands:

```bash
# Navigate to your project directory (if not already there)
cd /Users/sajalmadan/text_normalization_streamlit

# Initialize git repository
git init

# Add all files
git add .

# Make your first commit
git commit -m "Initial commit: TTS Text Normalization Streamlit App"

# Add your GitHub repository as remote (replace YOUR_USERNAME and REPO_NAME)
# You'll get this URL after creating the repo on GitHub
git remote add origin https://github.com/YOUR_USERNAME/REPO_NAME.git

# Rename branch to main (if needed)
git branch -M main

# Push to GitHub
git push -u origin main
```

**Note**: When you push, GitHub will ask for your credentials. Use a Personal Access Token (not your password).

## Step 3: Get GitHub Personal Access Token (if needed)

If GitHub asks for authentication:

1. Go to GitHub → Settings → Developer settings → Personal access tokens → Tokens (classic)
2. Click "Generate new token (classic)"
3. Give it a name like "Streamlit Deployment"
4. Select scopes: `repo` (full control of private repositories)
5. Click "Generate token"
6. Copy the token and use it as your password when pushing

## Step 4: Deploy on Streamlit Cloud

1. **Go to Streamlit Cloud:**
   - Visit: https://share.streamlit.io
   - Sign in with your **GitHub account** (same account you used for the repo)

2. **Create New App:**
   - Click the **"New app"** button
   - You'll see a form with these fields:

3. **Fill in the deployment form:**
   - **Repository**: Select `sajal-madan-ds/text-normalization-streamlit` (or your repo name)
   - **Branch**: Select `main` (or `master` if that's your default)
   - **Main file path**: Enter `streamlit_app.py`
   - **App URL**: Leave default (or customize if you have a paid plan)
   - Click **"Deploy"**

4. **Wait for deployment:**
   - Streamlit will install dependencies from `requirements.txt`
   - Build your app
   - Usually takes 1-2 minutes
   - You'll see a live URL when done!

## Step 5: Access Your App

Once deployed, you'll get a URL like:
```
https://text-normalization-streamlit-xxxxx.streamlit.app
```

Share this URL with anyone who needs to use your app!

## Troubleshooting

### If deployment fails:

1. **Check the logs** in Streamlit Cloud dashboard
2. **Verify requirements.txt** has all dependencies:
   ```
   streamlit>=1.28.0
   num2words>=0.5.13
   ```

3. **Check file structure** - Make sure `streamlit_app.py` is in the root directory

4. **Verify Python version** - Streamlit Cloud uses Python 3.9+ by default

### Common Issues:

- **"Module not found"**: Check that all imports are correct in `streamlit_app.py`
- **"App not loading"**: Check Streamlit Cloud logs for errors
- **"Git push failed"**: Make sure you're using a Personal Access Token, not password

## Quick Command Reference

```bash
# Initialize and push (run these in your terminal)
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/YOUR_USERNAME/REPO_NAME.git
git branch -M main
git push -u origin main
```

## Files Ready for Deployment

✅ `streamlit_app.py` - Main app file  
✅ `num2words_tts.py` - Core module  
✅ `requirements.txt` - Dependencies  
✅ `.streamlit/config.toml` - Streamlit config  
✅ `README.md` - Documentation  
✅ `.gitignore` - Git ignore file  

All files are ready! Just follow the steps above. 🎉

