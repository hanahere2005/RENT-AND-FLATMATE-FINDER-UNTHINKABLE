import json
import logging
from flask import current_app

logger = logging.getLogger(__name__)

def calculate_compatibility(listing, tenant_profile):
    """
    Computes compatibility score, breakdown, and explanation between a listing and a tenant profile.
    """
    if not tenant_profile:
        explanation_json = json.dumps({
            "text": "No tenant profile configured.",
            "breakdown": {
                "budget": 0, "location": 0, "lifestyle": 0, "gender": 0, "occupancy": 0, "amenities": 0
            }
        })
        return 0, explanation_json, False
        
    score, explanation_text, breakdown, is_ai = calculate_compatibility_rule_based(listing, tenant_profile)
    
    explanation_json = json.dumps({
        "text": explanation_text,
        "breakdown": breakdown
    })
    
    return score, explanation_json, is_ai


def calculate_compatibility_dynamic(listing, prefs):
    """
    Computes compatibility score, breakdown, and reason strings dynamically based on a user's applied search filters.
    If no compatibility-relevant preferences are present, returns score 0.
    """
    # Weights:
    # 1. Location Match: 30%
    # 2. Budget Match: 25%
    # 3. Room Type Match: 15%
    # 4. Gender Match: 10%
    # 5. Amenities Match: 10%
    # 6. Lifestyle Match: 10%

    reasons = []
    
    # 1. Location (30 points)
    location_score = 0
    loc_filter = prefs.get('location')
    if loc_filter:
        loc_listing = listing.location.strip().lower() if listing.location else ""
        pref_loc = loc_filter.strip().lower()
        if loc_listing == pref_loc:
            location_score = 30
            reasons.append(f"✓ Located in {loc_filter.capitalize()} (+30)")
        elif pref_loc in loc_listing or loc_listing in pref_loc:
            location_score = 21
            reasons.append(f"✓ Close match to preferred city: {loc_filter.capitalize()} (+21)")
        else:
            location_score = 6
            reasons.append("✗ Different location from preferred city. (+6)")
    else:
        location_score = 30

    # 2. Budget (25 points)
    budget_score = 0
    max_budget_filter = prefs.get('max_budget')
    if max_budget_filter:
        try:
            budget = float(max_budget_filter)
            rent = listing.rent
            ratio = rent / budget
            if ratio <= 1.0:
                budget_score = 25
                reasons.append(f"✓ Within your budget (₹{rent:.0f} / ₹{budget:.0f}) (+25)")
            elif ratio <= 1.1:
                budget_score = 18
                reasons.append(f"✓ Slightly above budget limit (₹{rent:.0f} / ₹{budget:.0f}) (+18)")
            elif ratio <= 1.3:
                budget_score = 10
                reasons.append(f"✗ Moderately above budget limit (₹{rent:.0f} / ₹{budget:.0f}) (+10)")
            else:
                budget_score = 2
                reasons.append(f"✗ Far exceeds budget limit (₹{rent:.0f} / ₹{budget:.0f}) (+2)")
        except ValueError:
            budget_score = 25
    else:
        budget_score = 25

    # 3. Room Type / Occupancy (15 points)
    room_type_score = 0
    rt_filter = prefs.get('room_type')
    if rt_filter:
        rt_listing = listing.room_type.lower() if listing.room_type else ""
        if rt_filter.lower() in rt_listing or rt_listing in rt_filter.lower():
            room_type_score = 15
            reasons.append("✓ Matches your preferred room type. (+15)")
        else:
            room_type_score = 0
            reasons.append("✗ Different room type from your preference. (+0)")
    else:
        room_type_score = 15

    # 4. Gender Preference (10 points)
    gender_score = 10
    gender_filter = prefs.get('gender')
    desc_lower = listing.description.lower() if listing.description else ""
    title_lower = listing.title.lower() if listing.title else ""
    combined_text = desc_lower + " " + title_lower
    
    female_only = any(kw in combined_text for kw in ['female only', 'girls only', 'female flatmate', 'female roommate', 'girl only', 'ladies only'])
    male_only = any(kw in combined_text for kw in ['male only', 'boys only', 'male flatmate', 'male roommate', 'boy only', 'gents only'])
    
    if gender_filter:
        pref_gender = gender_filter.lower()
        if pref_gender == 'female' and male_only:
            gender_score = 0
            reasons.append("✗ Female preferred, but listing is male only. (+0)")
        elif pref_gender == 'male' and female_only:
            gender_score = 0
            reasons.append("✗ Male preferred, but listing is female only. (+0)")
        else:
            gender_score = 10
            reasons.append("✓ Matches your gender preference. (+10)")
    else:
        gender_score = 10

    # 5. Amenities (10 points)
    amenities_score = 0
    amenities_filter = prefs.get('amenities')
    if amenities_filter:
        req_amenities = [a.strip().lower() for a in amenities_filter.split(',') if a.strip()]
        listing_amenities = [a.lower() for a in listing.amenities] if isinstance(listing.amenities, list) else []
        if req_amenities:
            matched_count = 0
            found_reqs = []
            missing_reqs = []
            for amenity in req_amenities:
                if any(amenity in la for la in listing_amenities):
                    matched_count += 1
                    found_reqs.append(amenity.upper())
                else:
                    missing_reqs.append(amenity.upper())
            amenity_pct = matched_count / len(req_amenities)
            amenities_score = int(amenity_pct * 10)
            if found_reqs:
                reasons.append(f"✓ Includes requested amenities: {', '.join(found_reqs)}. (+{amenities_score})")
            if missing_reqs:
                reasons.append(f"✗ Missing amenities: {', '.join(missing_reqs)}. (+0)")
        else:
            amenities_score = 10
    else:
        amenities_score = 10

    # 6. Lifestyle Habits (10 points)
    lifestyle_score = 0
    lifestyle_filter = prefs.get('lifestyle')
    if lifestyle_filter:
        req_habits = [h.strip().lower() for h in lifestyle_filter.split(',') if h.strip()]
        if req_habits:
            matched_habits = 0
            for habit in req_habits:
                if 'non-smoker' in habit or 'no smoking' in habit or 'non smoker' in habit:
                    if 'smoking allowed' in combined_text or 'smoker friendly' in combined_text:
                        continue
                if 'vegetarian' in habit or 'veg' in habit:
                    if 'non-veg only' in combined_text:
                        continue
                if habit in combined_text:
                    matched_habits += 1
                else:
                    matched_habits += 0.5
            lifestyle_pct = min(1.0, matched_habits / len(req_habits))
            lifestyle_score = int(lifestyle_pct * 10)
            reasons.append(f"✓ Matches lifestyle and habit preferences. (+{lifestyle_score})")
        else:
            lifestyle_score = 10
    else:
        lifestyle_score = 10

    total_score = location_score + budget_score + room_type_score + gender_score + amenities_score + lifestyle_score
    total_score = max(0, min(100, total_score))

    breakdown = {
        "location": location_score,
        "budget": budget_score,
        "room_type": room_type_score,
        "gender": gender_score,
        "amenities": amenities_score,
        "lifestyle": lifestyle_score
    }

    return total_score, breakdown, reasons


def calculate_compatibility_rule_based(listing, tenant_profile):
    # Weights:
    # 1. Budget Match: 35%
    # 2. Location Match: 20%
    # 3. Lifestyle Match: 15%
    # 4. Gender Match: 10%
    # 5. Occupancy Match: 10%
    # 6. Amenities Match: 10%
    
    # 1. Budget Match (Max 35 points)
    budget_score = 0
    rent = listing.rent
    b_max = tenant_profile.budget_max or 1000.0
    
    if rent <= b_max:
        budget_score = 35
    else:
        # Gradual reduction: if rent is double the budget cap, score is 0
        diff = rent - b_max
        reduction = (diff / b_max) * 35
        budget_score = max(0, int(35 - reduction))
        
    # 2. Location Match (Max 20 points)
    location_score = 0
    loc_listing = listing.location.strip().lower() if listing.location else ""
    pref_loc = tenant_profile.preferred_location.strip().lower() if tenant_profile.preferred_location else ""
    
    if not pref_loc or pref_loc == "not specified":
        location_score = 10  # neutral default
    elif loc_listing == pref_loc or pref_loc in loc_listing or loc_listing in pref_loc:
        location_score = 20
    else:
        # Partial word matching
        listing_words = set(loc_listing.replace(",", " ").split())
        tenant_words = set(pref_loc.replace(",", " ").split())
        overlap = listing_words.intersection(tenant_words)
        if overlap:
            location_score = 12
        else:
            location_score = 0
            
    # 3. Lifestyle Match (Max 15 points)
    lifestyle_score = 0
    habits = []
    if tenant_profile.lifestyle_habits:
        habits = [h.strip().lower() for h in tenant_profile.lifestyle_habits.split(',') if h.strip()]
        
    desc_lower = listing.description.lower() if listing.description else ""
    title_lower = listing.title.lower() if listing.title else ""
    combined_text = desc_lower + " " + title_lower
    
    if not habits:
        # Neutral default if no preferences are specified
        lifestyle_score = 10
    else:
        matched_habits = 0
        for habit in habits:
            if 'non-smoker' in habit or 'no smoking' in habit or 'non smoker' in habit:
                if 'smoking allowed' in combined_text or 'smoker friendly' in combined_text:
                    continue
            if 'vegetarian' in habit or 'veg' in habit:
                if 'non-veg only' in combined_text:
                    continue
            matched_habits += 1
            
        lifestyle_score = int(15 * (matched_habits / len(habits)))
        
    # 4. Gender Match (Max 10 points)
    gender_score = 10
    female_only = any(kw in combined_text for kw in ['female only', 'girls only', 'female flatmate', 'female roommate', 'girl only', 'ladies only'])
    male_only = any(kw in combined_text for kw in ['male only', 'boys only', 'male flatmate', 'male roommate', 'boy only', 'gents only'])
    
    tenant_bio = tenant_profile.bio.lower() if tenant_profile.bio else ""
    tenant_email = tenant_profile.user.email.lower() if (tenant_profile.user and tenant_profile.user.email) else ""
    tenant_text = tenant_bio + " " + tenant_email
    
    is_female = any(kw in tenant_text for kw in ['female', 'girl', 'woman', 'lady', 'she', 'her'])
    is_male = any(kw in tenant_text for kw in ['male', 'boy', 'man', 'guy', 'he', 'him'])
    
    if female_only and is_male and not is_female:
        gender_score = 0
    elif male_only and is_female and not is_male:
        gender_score = 0
        
    # 5. Occupancy Match (Max 10 points)
    occupancy_score = 8  # default neutral
    room_type = listing.room_type.lower() if listing.room_type else ""
    if 'single' in room_type:
        if 'private' in tenant_bio or 'single' in tenant_bio:
            occupancy_score = 10
        elif 'shared' in tenant_bio or 'sharing' in tenant_bio:
            occupancy_score = 5
    elif 'shared' in room_type:
        if 'shared' in tenant_bio or 'sharing' in tenant_bio or 'roommate' in tenant_bio:
            occupancy_score = 10
        elif 'private' in tenant_bio or 'single' in tenant_bio:
            occupancy_score = 4
            
    # 6. Amenities Match (Max 10 points)
    amenities_score = 0
    key_amenities = ['wifi', 'parking', 'washing machine', 'ac', 'kitchen', 'furnished', 'attached bathroom', 'gym']
    listing_amenities = [a.lower() for a in listing.amenities] if isinstance(listing.amenities, list) else []
    
    matched_count = 0
    for amenity in key_amenities:
        if any(amenity in a for a in listing_amenities):
            matched_count += 1
            
    amenities_score = int(10 * (matched_count / len(key_amenities)))
    if matched_count > 0 and amenities_score == 0:
        amenities_score = 1
        
    total_score = budget_score + location_score + lifestyle_score + gender_score + occupancy_score + amenities_score
    total_score = max(0, min(100, total_score))
    
    breakdown = {
        "budget": budget_score,
        "location": location_score,
        "lifestyle": lifestyle_score,
        "gender": gender_score,
        "occupancy": occupancy_score,
        "amenities": amenities_score
    }
    
    explanations = [
        f"Budget Match: {budget_score}/35 pts (Rent: ${rent:.0f}, Max Budget: ${b_max:.0f})",
        f"Location Match: {location_score}/20 pts (Listing: {listing.location}, Preferred: {tenant_profile.preferred_location})",
        f"Lifestyle Match: {lifestyle_score}/15 pts (Habits: {tenant_profile.lifestyle_habits or 'None specified'})",
        f"Gender Match: {gender_score}/10 pts",
        f"Occupancy Match: {occupancy_score}/10 pts (Listing Room Type: {listing.room_type.capitalize()})",
        f"Amenities Match: {amenities_score}/10 pts (Matches {matched_count} key amenities)"
    ]
    explanation_text = "Detailed Compatibility Breakdown:\n\n- " + "\n- ".join(explanations)
    
    return total_score, explanation_text, breakdown, False
