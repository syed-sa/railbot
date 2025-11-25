import requests
import json
from datetime import datetime, timedelta



def extract_query_params(user_query: str):
    """
    Extract (source, destination, date) using Llama 3.1 Instruct model.
    """

    today = datetime.now().date()
    tomorrow = today + timedelta(days=1)

    if "today" in user_query.lower():
        user_query = user_query.replace("today", today.strftime("%Y-%m-%d"))
    if "tomorrow" in user_query.lower():
        user_query = user_query.replace("tomorrow", tomorrow.strftime("%Y-%m-%d"))

    API_URL = "https://router.huggingface.co/v1/chat/completions"
    headers = {"Authorization": f"Bearer {HF_TOKEN}"}

    prompt = f"""
You are an NLU assistant that extracts travel information from text.
Return only a valid JSON object (no markdown, no code, no explanation).
The JSON must have exactly these keys: source, destination, date.

Example output format:
{{
  "source": "Mumbai",
  "destination": "Delhi",
  "date": "2025-11-10"
}}

User query: "{user_query}"
    """

    payload = {
        "model": MODEL_ID,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.2
    }

    response = requests.post(API_URL, headers=headers, json=payload)
    data = response.json()
    try:
        text = data["choices"][0]["message"]["content"]
        start, end = text.find("{"), text.rfind("}") + 1
        json_str = text[start:end]
        return json.loads(json_str)
    except Exception:
        print("⚠️ Could not parse model output:", json.dumps(data, indent=2))
        return {}



def get_trains_from_irctc_api(source_code, dest_code, date):
    """
    Calls IRCTC RapidAPI endpoint for trains between two stations on a date.
    """
    url = "https://irctc1.p.rapidapi.com/api/v3/trainBetweenStations"
    params = {
        "fromStationCode": source_code,
        "toStationCode": dest_code,
        "dateOfJourney": date
    }
    headers = {
        "x-rapidapi-key": RAPID_KEY,
        "x-rapidapi-host": "irctc1.p.rapidapi.com"
    }

    response = requests.get(url, headers=headers, params=params)
    if response.status_code == 200:
        data = response.json()
        if "data" in data and isinstance(data["data"], list):
            return data["data"]
        else:
            print("⚠️ Unexpected API response:", data)
            return []
    else:
        print("❌ API request failed:", response.status_code, response.text)
        return []

def main():
    user_query = input("Enter your query (e.g., 'Show me trains from Mumbai to Delhi tomorrow'): ")

    params = extract_query_params(user_query)
    print("\nExtracted parameters:", params)

    # Simple city-to-station code map for now
    city_to_code = {
        "mumbai": "BVI",   # Borivali
        "delhi": "NDLS",   # New Delhi
        "chennai": "MAS",  # Chennai Central
        "bangalore": "SBC",# KSR Bengaluru
        "hyderabad": "HYB" # Hyderabad Deccan
    }

    src = city_to_code.get(params.get("source", "").lower())
    dest = city_to_code.get(params.get("destination", "").lower())
    date = params.get("date") or datetime.now().strftime("%Y-%m-%d")

    if not src or not dest:
        print("❌ Unknown station. Try Mumbai, Delhi, Chennai, Bangalore, Hyderabad.")
        return

    trains = get_trains_from_irctc_api(src, dest, date)
    print(f"\nFound {len(trains)} trains between {src} and {dest} for {date}:\n")

    for t in trains[:10]:  # Show first 10
        train_num = t.get("train_number", "N/A")
        train_name = t.get("train_name", "N/A")
        departure = t.get("from_std", "N/A")
        arrival = t.get("to_std", "N/A")
        duration = t.get("duration", "N/A")

        # Handle missing or empty "days" field
        days = t.get("days")
        if isinstance(days, list):
            running_days = ", ".join(days)
        elif isinstance(days, str):
            running_days = days
        else:
            running_days = "Not available"

        print(f"{train_num} - {train_name}")
        print(f"   Departure: {departure} | Arrival: {arrival}")
        print(f"   Travel Time: {duration} | Running Days: {running_days}")
        print("-" * 60)


if __name__ == "__main__":
    main()
