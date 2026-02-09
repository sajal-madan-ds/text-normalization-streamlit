# TTS Text Normalization - Streamlit App

A web application for converting numbers and numeric patterns in text to words for Text-to-Speech (TTS) systems. Supports both **English** and **Hindi** languages.

## Features

- 🔢 Converts various number patterns to words
- 🌐 Supports English and Hindi languages
- 🔍 Auto-detects language from text
- 📊 Shows detected patterns (optional)
- 🎯 Handles dates, times, currency, phone numbers, IDs, and more

## Supported Patterns

- **Dates**: 12-11-2026, 12/11/2026, January 15th 2024
- **Time**: 2:30pm, 14:30, 5 baj (Hinglish)
- **Phone Numbers**: +91-9876543210, 9999303854
- **Currency**: ₹500, $50, Rs 21000, 150 dollars
- **Percentages**: 25%, 15.5 percent
- **Measurements**: 25.5°C, 125-140 km, 1.5 hours
- **IDs & Codes**: Aadhaar numbers, OTP, PIN codes, Employee IDs
- **Ordinals**: 1st, 2nd, 3rd, 4th
- **Ratios**: 3:1, 16:9
- **Ranges**: 125-140
- **Decimals**: 25.5, 99.99
- **Vehicle Numbers**: DL01CA1234
- **Alphanumeric**: Room 123, Floor 5

## Local Setup

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the app:**
   ```bash
   streamlit run streamlit_app.py
   ```

3. **Open your browser:**
   The app will open at `http://localhost:8501`

## Deploy on Streamlit Cloud

1. **Push your code to GitHub:**
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git remote add origin <your-github-repo-url>
   git push -u origin main
   ```

2. **Deploy on Streamlit Cloud:**
   - Go to [share.streamlit.io](https://share.streamlit.io)
   - Sign in with your GitHub account
   - Click "New app"
   - Select your repository and branch
   - Set the main file path to `streamlit_app.py`
   - Click "Deploy"

3. **Your app will be live!** 🎉

## Project Structure

```
.
├── streamlit_app.py      # Main Streamlit application
├── num2words_tts.py      # TTS preprocessing module
├── requirements.txt      # Python dependencies
├── .streamlit/
│   └── config.toml       # Streamlit configuration
└── README.md             # This file
```

## Dependencies

- `streamlit>=1.28.0` - Web framework
- `num2words>=0.5.13` - Number to words conversion

## License

**⚠️ IMPORTANT: Non-Commercial, Non-Public Use Only**

This software is provided for **personal, private, and educational use only**. 

**Restrictions:**
- ❌ **NOT for commercial use** - Cannot be used in any commercial product or service
- ❌ **NOT for public use** - Cannot be publicly deployed or distributed without permission
- ✅ **Personal/Private use only** - For individual learning and private projects

For commercial or public use licensing, please contact the copyright holder.

See [LICENSE](LICENSE) file for full terms and conditions.

