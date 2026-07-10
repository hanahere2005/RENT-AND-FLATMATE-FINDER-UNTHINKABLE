import json
import logging
from openai import OpenAI
from flask import current_app
from backend.prompts.ai_prompts import COMPATIBILITY_PROMPT_TEMPLATE

logger = logging.getLogger(__name__)

def calculate_compatibility(listing, tenant_profile):
    """
    Computes compatibility score and explanation between a listing and a tenant profile.
    Tries OpenAI first, falls back to rule-based matching if OpenAI fails or key is missing.
    Returns (score, explanation, is_ai)
    """
    api_key = current_app.config.get('OPENAI_API_KEY')
    
    if api_key:
        try:
            client = OpenAI(api_key=api_key)
            prompt = COMPATIBILITY_PROMPT_TEMPLATE.format(
                listing_title=listing.title,
                listing_room_type=listing.room_type,
                listing_furnishing_status=listing.furnishing_status,
                listing_rent=listing.rent,
                listing_location=listing.location,
                listing_address=listing.address,
                listing_available_from=str(listing.available_from),
                listing_amenities=", ".join(listing.amenities) if isinstance(listing.amenities, list) else str(listing.amenities),
                tenant_preferred_location=tenant_profile.preferred_location,
                tenant_budget_min=tenant_profile.budget_min,
                tenant_budget_max=tenant_profile.budget_max,
                tenant_move_in_date=str(tenant_profile.move_in_date),
                tenant_occupation=tenant_profile.occupation,
                tenant_bio=tenant_profile.bio or "N/A"
            )
            
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that returns only raw JSON."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.2,
                response_format={"type": "json_object"}
            )
            
            result_text = response.choices[0].message.content.strip()
            result_json = json.loads(result_text)
            
            score = int(result_json.get('score', 0))
            explanation = result_json.get('explanation', '')
            
            # Bound check score
            score = max(0, min(100, score))
            
            return score, explanation, True
            
        except Exception as e:
            logger.error(f"AI compatibility scoring failed, falling back to rule-based. Error: {str(e)}")
            
    # Fallback to rule-based
    return calculate_compatibility_rule_based(listing, tenant_profile)


def calculate_compatibility_rule_based(listing, tenant_profile):
    """
    Deterministically computes a compatibility score based on structured rules.
    Max Score: 100 points
    - Budget Match: 40 points
    - Location Match: 40 points
    - Move-in Date Match: 20 points
    """
    budget_score = 0
    location_score = 0
    date_score = 0
    
    explanations = []
    
    # 1. Budget Match (Max 40 points)
    rent = listing.rent
    b_min = tenant_profile.budget_min
    b_max = tenant_profile.budget_max
    
    if b_min <= rent <= b_max:
        budget_score = 40
        explanations.append(f"Rent of ${rent:.2f} falls perfectly within your budget range of ${b_min:.2f} - ${b_max:.2f} (+40 pts).")
    elif rent < b_min:
        # Rent is cheaper than preferred min budget, which is generally fine/positive
        budget_score = 40
        explanations.append(f"Rent of ${rent:.2f} is below your minimum budget of ${b_min:.2f}, representing a great saving (+40 pts).")
    elif rent <= b_max * 1.15:
        budget_score = 20
        explanations.append(f"Rent of ${rent:.2f} is slightly above your budget cap of ${b_max:.2f} but within a 15% margin (+20 pts).")
    else:
        budget_score = 0
        explanations.append(f"Rent of ${rent:.2f} exceeds your budget cap of ${b_max:.2f} (0 pts).")
        
    # 2. Location Match (Max 40 points)
    loc_listing = listing.location.strip().lower()
    loc_tenant = tenant_profile.preferred_location.strip().lower()
    
    if loc_listing == loc_tenant or loc_tenant in loc_listing or loc_listing in loc_tenant:
        location_score = 40
        explanations.append(f"Property location ({listing.location}) matches your preferred location ({tenant_profile.preferred_location}) (+40 pts).")
    else:
        # Check partial word matches
        listing_words = set(loc_listing.replace(",", " ").split())
        tenant_words = set(loc_tenant.replace(",", " ").split())
        overlap = listing_words.intersection(tenant_words)
        
        if overlap:
            location_score = 20
            explanations.append(f"Property location ({listing.location}) shares regional terms with your preferred location ({tenant_profile.preferred_location}) (+20 pts).")
        else:
            location_score = 0
            explanations.append(f"Property location ({listing.location}) does not match your preferred location ({tenant_profile.preferred_location}) (0 pts).")
            
    # 3. Move-in Date Match (Max 20 points)
    avail_date = listing.available_from
    move_date = tenant_profile.move_in_date
    
    if avail_date <= move_date:
        date_score = 20
        explanations.append(f"Property is available from {avail_date.strftime('%Y-%m-%d')}, which is on or before your move-in date of {move_date.strftime('%Y-%m-%d')} (+20 pts).")
    else:
        days_diff = (avail_date - move_date).days
        if days_diff <= 30:
            date_score = 10
            explanations.append(f"Property is available from {avail_date.strftime('%Y-%m-%d')}, which is {days_diff} days after your preferred move-in date of {move_date.strftime('%Y-%m-%d')} (+10 pts).")
        else:
            date_score = 0
            explanations.append(f"Property availability ({avail_date.strftime('%Y-%m-%d')}) is more than 30 days after your move-in date ({move_date.strftime('%Y-%m-%d')}) (0 pts).")
            
    total_score = budget_score + location_score + date_score
    
    # Generate final response summary
    explanation_text = " (Rule-based Fallback Scorer)\n\n" + "\n- ".join(explanations)
    explanation_text += f"\n\nRoom Type: {listing.room_type.replace('_', ' ').capitalize()} room. Furnishing status: {listing.furnishing_status.capitalize()}."
    
    return total_score, explanation_text, False
