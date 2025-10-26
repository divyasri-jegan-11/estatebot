from flask import Flask, request, jsonify
from flask_cors import CORS
import pandas as pd
import os, re, json, sqlite3, random
from datetime import datetime

try:
    from openai import OpenAI
except ImportError:
    OpenAI = None

app = Flask(__name__)
CORS(app)

DB_FILE = os.path.join(os.path.dirname(__file__), "leads.db")
CSV_FILE = os.path.join(os.path.dirname(__file__), "magicbricks_cleaned.csv")

# Load CSV
if os.path.exists(CSV_FILE):
    df = pd.read_csv(CSV_FILE)
else:
    df = pd.DataFrame(columns=["id","title","city","location","price","bhk","type","amenities","latitude","longitude"])

# SQLite setup
def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("""CREATE TABLE IF NOT EXISTS leads (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT, email TEXT, phone TEXT, query TEXT, created_at TEXT
    )""")
    conn.commit(); conn.close()
init_db()

def save_lead(name,email,phone,query):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("INSERT INTO leads (name,email,phone,query,created_at) VALUES (?,?,?,?,?)",
              (name,email,phone,query,datetime.utcnow().isoformat()))
    conn.commit(); conn.close()

# --- Simple NLP helpers ---
def extract_filters(text):
    text = text.lower()
    filters = {}
    bhk = re.search(r"(\d+)\s*(?:bhk|bed)", text)
    if bhk: filters["bhk"] = int(bhk.group(1))
    price = re.search(r"(?:under|below|less than|within)\s*(\d+\.?\d*)\s*(lakh|lakhs|crore|cr|k|lacs)?", text)
    if price:
        val, unit = float(price.group(1)), price.group(2)
        if unit and unit.startswith("l"): val *= 1e5
        elif unit and unit.startswith("c"): val *= 1e7
        elif unit and unit == "k": val *= 1e3
        filters["max_price"] = val
    loc = re.search(r"(?:in|at|near)\s+([a-zA-Z ]+)", text)
    if loc: filters["location"] = loc.group(1).strip()
    return filters

def search_properties(filters):
    results = df.copy()
    if "bhk" in filters:
        results = results[results["bhk"] == filters["bhk"]]
    if "max_price" in filters:
        results = results[results["price"] <= filters["max_price"] * 1.2]  # 20% buffer
    if "location" in filters:
        loc = filters["location"].lower()
        results = results[results["location"].str.lower().str.contains(loc, na=False)]
    if results.empty:
        results = df.sort_values("price").head(3)
    return results.head(5).to_dict(orient="records")

# --- Local fallback responses ---
def local_chat_reply(query):
    q = query.lower()
    generic_replies = [
        "That’s interesting! Could you tell me which location you’re considering?",
        "Got it! Are you looking to buy or rent?",
        "Sure! What’s your approximate budget range?",
        "I can help with that — do you have a preferred BHK size or area?",
        "Sounds good! Chennai has great options; want me to show a few suggestions?"
    ]
    greet = any(word in q for word in ["hi", "hello", "hey"])
    if greet:
        return random.choice([
            "Hi there! 😊 How can I help you with your property search today?",
            "Hello! 👋 Ready to explore some beautiful homes in Chennai?",
            "Hey! I’m your real estate assistant — tell me what kind of property you want!"
        ])
    elif "thank" in q:
        return "You're most welcome! 😊 Let me know if you want me to shortlist a few properties."
    elif "bye" in q:
        return "Goodbye! Have a great day ahead. 🏡"
    return random.choice(generic_replies)

@app.route("/chat", methods=["POST"])
def chat():
    body = request.json or {}
    query = body.get("query", "").strip()
    if not query:
        return jsonify({"message": "Please enter a question or property request."})

    key = os.getenv("OPENAI_API_KEY")
    llm = OpenAI(api_key=key) if (OpenAI and key) else None

    # Detect property query
    if re.search(r"\b(bhk|flat|villa|property|sale|under|above|in|buy|find)\b", query.lower()):
        filters = extract_filters(query)
        results = search_properties(filters)
        text_summary = "\n".join(
            [f"- {r['title']} (₹{int(r['price']):,}, {r['bhk']} BHK, {r['location']})"
             for r in results]
        )
        try:
            if llm:
                prompt = f"""
                You are an AI real estate assistant for Chennai.
                The user asked: "{query}".
                Here are some matching properties:
                {text_summary}
                Write a friendly, conversational reply summarizing the best options and inviting the user to connect.
                """
                response = llm.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role":"system","content":"You are a helpful property advisor."},
                        {"role":"user","content":prompt}
                    ],
                    temperature=0.8
                )
                reply = response.choices[0].message.content
            else:
                raise Exception("No LLM")
        except Exception:
            reply = f"I found {len(results)} good options around your budget:\n\n{text_summary}\n\nWould you like me to connect you with an agent for more details?"
        return jsonify({"message": reply, "results": results})

    # Generic chat / offline mode
    try:
        if llm:
            completion = llm.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role":"system","content":"You are a helpful, friendly AI property assistant for Chennai real estate."},
                    {"role":"user","content":query}
                ]
            )
            reply = completion.choices[0].message.content
        else:
            raise Exception("No LLM available")
    except Exception:
        reply = local_chat_reply(query)

    return jsonify({"message": reply})

@app.route("/save_lead", methods=["POST"])
def save_lead_route():
    b = request.json or {}
    if not all(k in b for k in ("name","email","phone")):
        return jsonify({"error":"Missing fields"}),400
    save_lead(b["name"], b["email"], b["phone"], b.get("query",""))
    return jsonify({"status":"saved"})

@app.route("/health")
def health():
    return jsonify({"status":"ok", "llm_active": bool(os.getenv("OPENAI_API_KEY"))})

if __name__ == "__main__":
    print("✅ LLM connected:", bool(os.getenv("OPENAI_API_KEY")))
    app.run(port=5000, debug=True)
