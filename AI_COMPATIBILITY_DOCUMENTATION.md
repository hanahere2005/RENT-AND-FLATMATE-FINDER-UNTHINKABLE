# Staylio AI Compatibility Feature Documentation

Staylio incorporates a dual-layer matchmaking engine that analyzes candidate properties against roommate preferences. 

---

## 1. Dynamic Matching Algorithm & Weights

When a search filter is applied, Staylio evaluates a room's compatibility using a deterministic scoring engine that computes six components:

1.  **Location Match (30%)**: Compares the user's preferred search city to the listing's location.
    *   *Perfect match*: 30 points.
    *   *Partial word match*: 21 points.
    *   *Mismatch*: 6 points.
2.  **Budget Match (25%)**: Compares listing rent against user max budget.
    *   *Within budget limit*: 25 points.
    *   *Slightly above (<10%)*: 18 points.
    *   *Moderately above (<30%)*: 10 points.
    *   *Far exceeds (>30%)*: 2 points.
3.  **Room Type Match (15%)**: Evaluates preferred room layout (Single/Shared).
    *   *Match*: 15 points.
    *   *Mismatch*: 0 points.
4.  **Gender Match (10%)**: Evaluates listing gender constraints.
    *   *Match*: 10 points.
    *   *Mismatch*: 0 points.
5.  **Amenities Match (10%)**: Compares listing amenities array against target amenities requested.
    *   *Ratio of present amenities*: mapping up to 10 points.
6.  **Lifestyle Match (10%)**: Evaluates text descriptions for habits (e.g. smoking, pets, vegetarian).
    *   *Ratio of matching traits*: mapping up to 10 points.

---

## 2. OpenAI Matchmaking Engine & Structured Prompts

When OpenAI completions are enabled (`OPENAI_API_KEY` is present), the service delegates complex compatibility logic (e.g., bio parsing and open-text habit analysis) to the model.

### Prompt Template
```text
You are an expert matchmaking assistant for Staylio, a room rent and roommate finder platform.
Your task is to analyze the compatibility between a tenant profile and a property listing, and return a structured JSON response.

Tenant Profile:
- Bio: {tenant_bio}
- Lifestyle habits: {tenant_lifestyle}
- Preferred location: {tenant_location}
- Budget Max: {tenant_budget}

Listing details:
- Title: {listing_title}
- Location: {listing_location}
- Rent: {listing_rent}
- Description: {listing_description}
- Amenities: {listing_amenities}

Analyze the details and return a JSON object with:
1. "score": An integer between 0 and 100.
2. "breakdown": An object showing points for:
   - "budget" (max 35)
   - "location" (max 20)
   - "lifestyle" (max 15)
   - "gender" (max 10)
   - "occupancy" (max 10)
   - "amenities" (max 10)
3. "reasons": A list of short strings (each starting with '✓' for matching or '✗' for mismatching/missing features).

Output format:
{
  "score": 85,
  "breakdown": {
    "budget": 35,
    "location": 20,
    "lifestyle": 12,
    "gender": 10,
    "occupancy": 8,
    "amenities": 0
  },
  "reasons": [
    "✓ Within budget limit (₹5800 / ₹6000)",
    "✗ Missing requested Gym amenity"
  ]
}
```

---

## 3. Structured Rule-Based Fallback Engine

If the `OPENAI_API_KEY` env variable is empty, or the OpenAI service fails due to rate limits or network issues, the backend automatically fails-safe to our local deterministic Python scoring engine. 

This engine implements the exact same math, category scoring, and explanations logic locally (using regex word maps, budget calculations, and listing metadata overlays) to guarantee that user matching scores remain fast, available, and correct under all conditions.
