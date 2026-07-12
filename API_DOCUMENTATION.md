# Staylio API Documentation

All API endpoints are hosted by default on `http://localhost:5050` and return standard JSON formats.

---

## 1. Authentication Blueprint

### Register Account
*   **Method**: `POST`
*   **URL**: `/auth/register`
*   **Auth Required**: None
*   **Request Body**:
    ```json
    {
      "email": "user@test.com",
      "password": "password123",
      "role": "tenant" 
    }
    ```
*   **Response (201 Created)**:
    ```json
    {
      "message": "User registered successfully",
      "user": {
        "id": 1,
        "email": "user@test.com",
        "role": "tenant"
      }
    }
    ```
*   **Error Responses**:
    *   `400 Bad Request` (Email already exists or invalid parameters)

### Login Account
*   **Method**: `POST`
*   **URL**: `/auth/login`
*   **Auth Required**: None
*   **Request Body**:
    ```json
    {
      "email": "user@test.com",
      "password": "password123"
    }
    ```
*   **Response (200 OK)**:
    ```json
    {
      "access_token": "jwt_access_token_string",
      "refresh_token": "jwt_refresh_token_string",
      "user": {
        "id": 1,
        "email": "user@test.com",
        "role": "tenant"
      }
    }
    ```
*   **Error Responses**:
    *   `401 Unauthorized` (Invalid email or password)

### Refresh Token
*   **Method**: `POST`
*   **URL**: `/auth/refresh`
*   **Auth Required**: Yes (Refresh Token inside Bearer Header)
*   **Response (200 OK)**:
    ```json
    {
      "access_token": "new_jwt_access_token_string"
    }
    ```

---

## 2. Listings Blueprint

### Get Listings Index
*   **Method**: `GET`
*   **URL**: `/listings`
*   **Auth Required**: Optional (Tenant JWT unlocks dynamic match scores)
*   **Query Parameters**:
    *   `location`: city name
    *   `max_budget`: maximum rent limit
    *   `room_type`: single/shared
    *   `furnishing`: fully-furnished/unfurnished
    *   `gender`: male/female
    *   `lifestyle`: habits tags
    *   `amenities`: comma-separated string (e.g. `wifi,ac`)
    *   `availability`: `available`, `booked`, or `all`
*   **Response (200 OK)**:
    ```json
    {
      "listings": [
        {
          "id": 3,
          "title": "Spacious Cozy Room",
          "rent": 6000.0,
          "location": "Pune",
          "room_type": "single",
          "furnishing_status": "semi-furnished",
          "is_filled": false,
          "compatibility_score": 79,
          "compatibility_breakdown": {
            "location": 21,
            "budget": 25,
            "room_type": 15,
            "gender": 10,
            "amenities": 3,
            "lifestyle": 5
          }
        }
      ],
      "total": 1,
      "page": 1,
      "pages": 1
    }
    ```

### Create Listing
*   **Method**: `POST`
*   **URL**: `/listings`
*   **Auth Required**: Yes (Owner role)
*   **Request Multipart Form-Data**:
    *   `title`: string
    *   `description`: string
    *   `location`: string
    *   `address`: string
    *   `rent`: float
    *   `contact_info`: string
    *   `room_type`: single/shared
    *   `furnishing_status`: fully-furnished/semi-furnished/unfurnished
    *   `num_rooms`: integer
    *   `available_from`: date string (`YYYY-MM-DD`)
    *   `amenities`: list of strings (e.g., `['wifi', 'ac']`)
    *   `images`: file objects (optional)
*   **Response (201 Created)**:
    ```json
    {
      "message": "Listing created successfully",
      "listing": {
        "id": 1,
        "title": "Modern Room"
      }
    }
    ```

### Get Listing Details
*   **Method**: `GET`
*   **URL**: `/listings/<id>`
*   **Auth Required**: Optional (Tenant JWT unlocks dynamic match scores)
*   **Response (200 OK)**:
    ```json
    {
      "id": 3,
      "title": "Spacious Cozy Room",
      "rent": 6000.0,
      "location": "Pune",
      "compatibility": {
        "compatibility_score": 79,
        "compatibility_breakdown": {
          "location": 21,
          "budget": 25,
          "room_type": 15,
          "gender": 10,
          "amenities": 3,
          "lifestyle": 5
        },
        "reason": [
          "Located in Pune (+21)",
          "Within your budget limit (+25)"
        ],
        "status": "Calculated dynamically"
      }
    }
    ```

### Delete Listing
*   **Method**: `DELETE`
*   **URL**: `/listings/<id>`
*   **Auth Required**: Yes (Listing Owner only)
*   **Response (200 OK)**:
    ```json
    {
      "success": true,
      "message": "Listing deleted successfully"
    }
    ```
*   **Error Responses**:
    *   `403 Forbidden` (User does not own listing)

### Toggle Booking Status
*   **Method**: `POST`
*   **URL**: `/listings/<id>/fill`
*   **Auth Required**: Yes (Listing Owner only)
*   **Request Body**:
    ```json
    {
      "is_filled": true
    }
    ```
*   **Response (200 OK)**:
    ```json
    {
      "message": "Listing status updated successfully",
      "listing": {
        "id": 3,
        "is_filled": true
      }
    }
    ```

---

## 3. Profiles & Actions

### Get Tenant Compatibility Score
*   **Method**: `GET`
*   **URL**: `/tenant/compatibility/<listing_id>`
*   **Auth Required**: Yes (Tenant role)
*   **Response (200 OK)**:
    ```json
    {
      "success": true,
      "data": {
        "compatibility": {
          "score": 79,
          "compatibility_breakdown": {
            "location": 21,
            "budget": 25,
            "room_type": 15,
            "gender": 10,
            "amenities": 3,
            "lifestyle": 5
          },
          "reason": [
            "Located in Pune (+21)",
            "Within your budget limit (+25)"
          ]
        },
        "interest_status": "none"
      }
    }
    ```

### Express Interest Request
*   **Method**: `POST`
*   **URL**: `/tenant/interest/<listing_id>`
*   **Auth Required**: Yes (Tenant role)
*   **Response (201 Created)**:
    ```json
    {
      "message": "Interest request submitted successfully"
    }
    ```

### Accept Interest Request
*   **Method**: `POST`
*   **URL**: `/owner/requests/<request_id>/accept`
*   **Auth Required**: Yes (Owner role)
*   **Response (200 OK)**:
    ```json
    {
      "message": "Interest request accepted, chat channel unlocked successfully"
    }
    ```
