import json
import logging
from flask import current_app

logger = logging.getLogger(__name__)

def calculate_compatibility(listing, tenant_profile):
    """
    Computes compatibility score, breakdown, and explanation between a listing and a tenant profile.
    If the tenant profile has not configured any preferences, returns score 0 and no breakdown.
    """
    # Check if profile is unconfigured (still set to initial system defaults)
    is_configured = False
    if tenant_profile:
        if tenant_profile.preferred_location and tenant_profile.preferred_location != 'Not specified':
            is_configured = True
        if tenant_profile.budget_max and tenant_profile.budget_max != 1000.0:
            is_configured = True
        if tenant_profile.lifestyle_habits:
            is_configured = True
            
    if not is_configured:
        explanation_json = json.dumps({
            "text": "No preferences selected. Configure your profile roommate preferences to calculate matching scores.",
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
    Computes compatibility score, breakdown, and explanation dynamically based on a user's applied search filters.
    If no compatibility-relevant preferences are present, returns score 0.
    """
    # Weights:
    # 1. Budget Match: 35%
    # 2. Location Match: 20%
    # 3. Lifestyle Match: 15%
    # 4. Gender Match: 10%
    # 5. Occupancy Match: 10%
    # 6. Amenities Match: 10%
    
    # 1. Budget Match (Max 35 points)
    budget_score = 35  # neutral/default if filter not set
    rent = listing.rent
    max_budget_filter = prefs.get('max_budget') or prefs.get('budget_max')
    
    if max_budget_filter:
        try:
            b_max = float(max_budget_filter)
            if rent <= b_max:
                budget_score = 35
            else:
                diff = rent - b_max
                reduction = (diff / b_max) * 35
                budget_score = max(0, int(35 - reduction))
        except ValueError:
            pass
            
    # 2. Location Match (Max 20 points)
    location_score = 20  # neutral/default if filter not set
    loc_filter = prefs.get('location')
    if loc_filter:
        loc_listing = listing.location.strip().lower() if listing.location else ""
        pref_loc = loc_filter.strip().lower()
        if loc_listing == pref_loc or pref_loc in loc_listing or loc_listing in pref_loc:
            location_score = 20
        else:
            listing_words = set(loc_listing.replace(",", " ").split())
            tenant_words = set(pref_loc.replace(",", " ").split())
            overlap = listing_words.intersection(tenant_words)
            if overlap:
                location_score = 12
            else:
                location_score = 0
                
    # 3. Lifestyle Match (Max 15 points)
    lifestyle_score = 15  # neutral/default if filter not set
    lifestyle_filter = prefs.get('lifestyle')
    if lifestyle_filter:
        desc_lower = listing.description.lower() if listing.description else ""
        title_lower = listing.title.lower() if listing.title else ""
        combined_text = desc_lower + " " + title_lower
        
        pref_habits = [h.strip().lower() for h in lifestyle_filter.split(',') if h.strip()]
        matched_habits = 0
        for habit in pref_habits:
            if 'non-smoker' in habit or 'no smoking' in habit or 'non smoker' in habit:
                if 'smoking allowed' in combined_text or 'smoker friendly' in combined_text:
                    continue
            if 'vegetarian' in habit or 'veg' in habit:
                if 'non-veg only' in combined_text:
                    continue
            matched_habits += 1
        if pref_habits:
            lifestyle_score = int(15 * (matched_habits / len(pref_habits)))
            
    # 4. Gender Match (Max 10 points)
    gender_score = 10  # neutral/default if filter not set
    gender_filter = prefs.get('gender')
    if gender_filter and gender_filter.lower() != 'any':
        desc_lower = listing.description.lower() if listing.description else ""
        title_lower = listing.title.lower() if listing.title else ""
        combined_text = desc_lower + " " + title_lower
        
        g_filter = gender_filter.lower()
        female_only = any(kw in combined_text for kw in ['female only', 'girls only', 'female flatmate', 'female roommate', 'girl only', 'ladies only'])
        male_only = any(kw in combined_text for kw in ['male only', 'boys only', 'male flatmate', 'male roommate', 'boy only', 'gents only'])
        
        if g_filter == 'male':
            if female_only:
                gender_score = 0
        elif g_filter == 'female':
            if male_only:
                gender_score = 0
                
    # 5. Occupancy Match (Max 10 points)
    occupancy_score = 10  # neutral/default if filter not set
    room_type_filter = prefs.get('room_type')
    if room_type_filter and room_type_filter.lower() != 'any':
        room_type = listing.room_type.lower() if listing.room_type else ""
        rt_filter = room_type_filter.lower()
        if rt_filter in room_type or room_type in rt_filter:
            occupancy_score = 10
        else:
            occupancy_score = 2
            
    # 6. Amenities Match (Max 10 points)
    amenities_score = 10  # neutral/default if filter not set
    furnishing_filter = prefs.get('furnishing')
    if furnishing_filter and furnishing_filter.lower() != 'any':
        furnishing_status = listing.furnishing_status.lower() if listing.furnishing_status else ""
        f_filter = furnishing_filter.lower()
        if f_filter in furnishing_status or furnishing_status in f_filter:
            amenities_score = 10
        else:
            amenities_score = 4
            
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
        f"Budget Match: {budget_score}/35 pts",
        f"Location Match: {location_score}/20 pts",
        f"Lifestyle Match: {lifestyle_score}/15 pts",
        f"Gender Match: {gender_score}/10 pts",
        f"Occupancy Match: {occupancy_score}/10 pts",
        f"Amenities Match: {amenities_score}/10 pts"
    ]
    explanation_text = "Dynamic Compatibility Breakdown:\n\n- " + "\n- ".join(explanations)
    
    return total_score, explanation_text, breakdown


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
            # Check for conflict: e.g. tenant is non-smoker but listing allows smoking
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
