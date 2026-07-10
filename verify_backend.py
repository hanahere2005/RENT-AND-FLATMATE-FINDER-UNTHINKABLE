import os
import sys
import json
from datetime import datetime, timedelta

# Add backend directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

# Force testing configuration
os.environ['DATABASE_URL'] = 'sqlite:///:memory:' # Use in-memory SQLite for tests
os.environ['SECRET_KEY'] = 'testsecret'
os.environ['JWT_SECRET_KEY'] = 'testjwt'

from backend.app import app
from backend.models import db, User, TenantProfile, OwnerProfile, Listing, InterestRequest, Chat, Message, CompatibilityScore

def run_tests():
    print(">>> Starting Backend Verification Tests...")
    
    # Initialize test client
    client = app.test_client()
    
    with app.app_context():
        # Recreate tables in-memory
        db.drop_all()
        db.create_all()
        
        # Test 1: Register Tenant
        print("\nTest 1: Registering Tenant User...")
        res = client.post('/auth/register', json={
            "email": "tenant@test.com",
            "password": "password123",
            "role": "tenant"
        })
        assert res.status_code == 201, f"Failed: {res.get_json()}"
        print("[PASS] Tenant registered successfully")
        
        # Test 2: Register Owner
        print("\nTest 2: Registering Owner User...")
        res = client.post('/auth/register', json={
            "email": "owner@test.com",
            "password": "password123",
            "role": "owner",
            "contact_phone": "+123456789"
        })
        assert res.status_code == 201, f"Failed: {res.get_json()}"
        print("[PASS] Owner registered successfully")
        
        # Test 3: Authenticate Tenant
        print("\nTest 3: Logging in Tenant...")
        res = client.post('/auth/login', json={
            "email": "tenant@test.com",
            "password": "password123"
        })
        assert res.status_code == 200, f"Failed: {res.get_json()}"
        tenant_data = res.get_json()
        tenant_token = tenant_data['access_token']
        print("[PASS] Tenant login successful")
        
        # Test 4: Authenticate Owner
        print("\nTest 4: Logging in Owner...")
        res = client.post('/auth/login', json={
            "email": "owner@test.com",
            "password": "password123"
        })
        assert res.status_code == 200, f"Failed: {res.get_json()}"
        owner_data = res.get_json()
        owner_token = owner_data['access_token']
        print("[PASS] Owner login successful")
        
        # Test 5: Update Tenant Profile
        print("\nTest 5: Updating Tenant Profile...")
        headers = {"Authorization": f"Bearer {tenant_token}"}
        res = client.post('/tenant/profile', headers=headers, json={
            "preferred_location": "Downtown",
            "budget_min": 500,
            "budget_max": 1200,
            "move_in_date": (datetime.utcnow() + timedelta(days=5)).strftime('%Y-%m-%d'),
            "occupation": "Software Engineer",
            "bio": "Quiet professional looking for a flat."
        })
        assert res.status_code == 200, f"Failed: {res.get_json()}"
        print("[PASS] Tenant profile updated successfully")
        
        # Test 6: Create Property Listing (Owner)
        print("\nTest 6: Creating Property Listing (Owner)...")
        headers_owner = {"Authorization": f"Bearer {owner_token}"}
        res = client.post('/listings', headers=headers_owner, data={
            "title": "Cosy Downtown Studio Room",
            "description": "Lovely room available close to subway.",
            "location": "Downtown",
            "address": "123 Main St, Downtown",
            "rent": "950",
            "available_from": datetime.utcnow().strftime('%Y-%m-%d'),
            "room_type": "single",
            "furnishing_status": "fully-furnished",
            "num_rooms": "1",
            "contact_info": "owner@test.com",
            "amenities": json.dumps(["wifi", "ac", "kitchen"])
        })
        assert res.status_code == 201, f"Failed: {res.get_json()}"
        listing_data = res.get_json()
        listing_id = listing_data['listing']['id']
        print("[PASS] Room listing created successfully")
        
        # Test 7: Verify Rule-Based Compatibility Score Cache
        print("\nTest 7: Verifying Match Score Calculation...")
        compat = CompatibilityScore.query.filter_by(tenant_id=tenant_data['user']['id'], listing_id=listing_id).first()
        assert compat is not None, "Failed: Compatibility score was not cached"
        assert compat.score == 100, f"Failed: Expected score 100, got {compat.score}"
        print("[PASS] Compatibility score calculated and cached successfully (Score: 100%)")
        
        # Test 8: Submit Interest Request (Tenant)
        print("\nTest 8: Submitting Interest Request (Tenant)...")
        res = client.post(f'/listings/{listing_id}/interest', headers=headers)
        assert res.status_code == 201, f"Failed: {res.get_json()}"
        req_data = res.get_json()
        request_id = req_data['request']['id']
        print("[PASS] Interest request submitted successfully")
        
        # Test 9: Accept Request & Verify Chat unlock (Owner)
        print("\nTest 9: Owner accepts request & unlocks Chat...")
        res = client.post(f'/owner/requests/{request_id}/accept', headers=headers_owner)
        assert res.status_code == 200, f"Failed: {res.get_json()}"
        print("[PASS] Interest request accepted")
        
        # Check chat room created
        chat = Chat.query.filter_by(request_id=request_id).first()
        assert chat is not None, "Failed: Chat room was not unlocked/created"
        assert len(chat.messages) == 1, "Failed: Introductory chat message not sent"
        print(f"[PASS] Chat room {chat.id} automatically initialized with intro message")
        
        # Test 10: Fetch Chat List
        print("\nTest 10: Fetching Chat Thread List...")
        res = client.get('/chat/list', headers=headers)
        assert res.status_code == 200, f"Failed: {res.get_json()}"
        chats_list = res.get_json()
        assert len(chats_list) == 1, "Failed: Chat list should have 1 active chat"
        print("[PASS] Chat list fetched successfully")
        
        print("\n>>> All Backend Verification Tests Passed Successfully!")

if __name__ == '__main__':
    run_tests()
