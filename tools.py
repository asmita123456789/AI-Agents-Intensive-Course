
# tools.py
import os
import pandas as pd
from datetime import datetime, timedelta

# Optional: Gemini (google-generativeai)
try:
    import google.generativeai as genai
    GENAI_AVAILABLE = True
except Exception:
    GENAI_AVAILABLE = False

# ----------------- existing tools -----------------
def generate_timeline(event_type, event_date):
    event_date = datetime.strptime(event_date, "%Y-%m-%d")
    tasks = [
        ("Book Venue", -30),
        ("Vendor Hunt", -25),
        ("Decoration Planning", -10),
        ("Guest Invitations", -20),
        ("Final Follow-ups", -3),
        ("Event Day", 0)
    ]
    timeline = []
    for task, days_before in tasks:
        date = event_date + timedelta(days=days_before)
        timeline.append({"task": task, "date": date.strftime("%Y-%m-%d")})
    return timeline

def search_vendors(event_type, budget):
    df = pd.read_csv("sample_vendors.csv")
    # simple matching: event_type match and price <= budget
    df = df[df["event_type"].str.lower() == event_type.lower()]
    df = df[df["price"] <= budget]
    return df.to_dict(orient="records")

def create_invite_card(event_type, event_date, guests):
    return f"🎉 Invitation 🎉\nEvent: {event_type}\nDate: {event_date}\nExpected Guests: {guests}\nHosted by: Asmita Wander Events\n"

# ----------------- Gemini helper (safe) -----------------
def gemini_event_advice(event_type: str, budget: int, guests: int) -> str:
    """
    Returns LLM-based event suggestions. If Gemini is not available or API key missing,
    returns a placeholder text.
    """
    if not GENAI_AVAILABLE:
        return ("[Gemini not installed] Install 'google-generativeai' and set GOOGLE_API_KEY "
                "to get AI suggestions. (Fallback advice not shown.)")

    api_key = os.environ.get("GOOGLE_API_KEY")
    if not api_key:
        return ("[No API key] Set environment variable GOOGLE_API_KEY to enable Gemini suggestions.")

    try:
        genai.configure(api_key=api_key)
        # choose a supported model name; update if model names change
        model = "gemini-1.5"  # change per availability if needed
        prompt = (
            f"Provide 5 practical planning tips and 3 creative ideas for an event:\n\n"
            f"Event Type: {event_type}\nBudget: {budget}\nGuest Count: {guests}\n\n"
            "Keep it short, numbered, and actionable."
        )
        response = genai.generate(model=model, prompt=prompt, max_output_tokens=500)
        # response structure may vary by SDK version — try to extract text safely
        text = ""
        if hasattr(response, "candidates") and len(response.candidates) > 0:
            text = response.candidates[0].content[0].text if hasattr(response.candidates[0], "content") else str(response)
        else:
            # fallback to string conversion
            text = str(response)
        return text
    except Exception as e:
        return f"[Gemini error] {e}"
