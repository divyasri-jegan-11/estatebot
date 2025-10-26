
EstateBot Fullscreen LLM - Windows instructions

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

Notes:
- If you don't set OPENAI_API_KEY, the backend will fallback to a rule-based parser.
- Leads are stored in backend/leads.db when saved via /save_lead (the UI currently prompts contact collection after results).
