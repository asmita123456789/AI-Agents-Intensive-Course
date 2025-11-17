# agents.py
from tools import generate_timeline, search_vendors, create_invite_card, gemini_event_advice
from memory import MemoryStore

class EventAgent:
    def __init__(self):
        self.memory = MemoryStore()

    def plan_event(self, event_type, date, budget, guests):
        plan = generate_timeline(event_type, date)
        vendors = search_vendors(event_type, budget)
        invite = create_invite_card(event_type, date, guests)

        # call Gemini helper (this will return fallback string if key missing)
        gemini_tips = gemini_event_advice(event_type, budget, guests)

        result = {
            "event_type": event_type,
            "date": date,
            "budget": budget,
            "guests": guests,
            "timeline": plan,
            "vendors": vendors,
            "invite_sample": invite,
            "gemini_tips": gemini_tips
        }

        # store result in memory
        self.memory.add("last_event_plan", result)
        return result

    def refine_plan(self, feedback):
        previous = self.memory.get("last_event_plan")

        if not previous:
            return {"error": "No previous plan found to refine."}

        if "budget" in feedback:
            previous["budget"] = feedback["budget"]
            previous["vendors"] = search_vendors(previous["event_type"], feedback["budget"])

        # update memory
        self.memory.add("last_event_plan", previous)
        return previous

    def show_memory(self):
        return self.memory.store
