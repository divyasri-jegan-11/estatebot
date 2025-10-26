# AI Real Estate Chatbot 


This project is an AI-powered real estate assistant that helps users find properties based on their preferences. It combines a Flask backend for handling property data and OpenAI API queries, with a modern frontend for user interaction.

---

## Features

- Interactive chatbot UI to ask about properties
- Filters and searches properties from a real CSV dataset (`magicbricks_cleaned.csv`)
- Conversational AI powered by OpenAI LLM for answering queries naturally
- Collects user information (name, email, phone) for personalized assistance
- Fullscreen chatbot interface with responsive design
- Easy deployment using Render (backend) + Netlify (frontend)

---

## Project Structure
```
estatebot/
├── backend/
│ ├── app.py
│ ├── requirements.txt
│ ├── Procfile
│ ├── magicbricks_cleaned.csv
│ └── leads.db
└── frontend/
├── index.html
├── style.css
└── script.js

```


---

## Prerequisites

- Python 3.11+
- Node.js (optional if building frontend separately)
- OpenAI API key

---

### EstateBot Fullscreen LLM - Windows instructions

1. Unzip the folder 'estatebot_fullscreen_llm' created by this package.
2. Backend (Flask + OpenAI):
   - Open PowerShell in the 'backend' folder.
   - python -m venv venv
   - .\venv\Scripts\activate
   - pip install -r requirements.txt
   - setx OPENAI_API_KEY "your_openai_api_key_here"
   - python app.py
   Backend will run on http://127.0.0.1:5000

3. Frontend:
   - The frontend is static. Open frontend/index.html in your browser.
   - Type queries like: "Show me 2BHK in Kelambakkam under 30 lakh"

## Notes:
- If you don't set OPENAI_API_KEY, the backend will fallback to a rule-based parser.
- Leads are stored in backend/leads.db when saved via /save_lead (the UI currently prompts contact collection after results).
     
## Backend Setup (Render)

1. Set environment variable for OpenAI API key:

```bash
export OPENAI_API_KEY="sk-your_api_key_here"   # Linux/Mac
setx OPENAI_API_KEY "sk-your_api_key_here"     # Windows
```
2. Install dependencies:
```
cd backend
pip install -r requirements.txt
```

3. Run locally (for testing):
```
python app.py

```

Access API at: `http://localhost:5000/chat`

For deployment on Render:

Root Directory:` backend`

Build Command: `pip install -r requirements.txt`

Start Command: `gunicorn backend.app:app`

Frontend Setup (Netlify)

1. Open `frontend/script.js` and set the API endpoint to your Render backend URL:

```
const API = "https://your-backend.onrender.com";
```

2. Deploy the frontend folder on Netlify (drag & drop or connect GitHub repo).

3. Visit your frontend link to interact with the chatbot.

### Usage

1. Open the chatbot frontend in a browser.

2. Start the conversation:
```
Hi! I'm your real estate assistant. Tell me what kind of property you're looking for!

```
3. Example queries:
   - Show me 2BHK flat under 70 lakh
   - Find villas with swimming pool in Chennai
   - List 3BHK flats in Sholinganallur

4. Provide name, email, and phone for personalized recommendations.

### Notes
   - Make sure your OpenAI API key has available quota.
   - The chatbot first filters the CSV dataset for matching properties, then uses LLM for conversational replies.
   - The app is designed for easy expansion: you can add more cities, property types, or integrate with real-time property APIs.


### License

MIT License



