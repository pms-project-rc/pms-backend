#!/bin/bash
BASE_URL="http://localhost:8000/api/v1"

# 1. Login Global Admin
echo "Logging in Global Admin..."
GLOBAL_TOKEN=$(curl -s -X POST $BASE_URL/auth/login/global-admin \
  -H "Content-Type: application/json" \
  -d '{"email": "admin@pms.com", "password": "admin123"}' | python3 -c "import sys, json; print(json.load(sys.stdin)['access_token'])")

# 2. Create Rate
echo "Creating Rate for Carro..."
curl -s -X POST "$BASE_URL/parking/rates/" \
  -H "Authorization: Bearer $GLOBAL_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "vehicle_type": "carro",
    "rate_type": "hour",
    "price": 5000,
    "description": "Tarifa hora carro",
    "is_active": true
  }'

# 3. Login Operational Admin
echo -e "\nLogging in Operational Admin..."
TOKEN=$(curl -s -X POST $BASE_URL/auth/login/operational-admin \
  -H "Content-Type: application/json" \
  -d '{"email": "op@pms.com", "password": "op123"}' | python3 -c "import sys, json; print(json.load(sys.stdin)['access_token'])")

# 4. Create Shift (if needed)
echo -e "\nCreating Shift..."
SHIFT_ID=$(curl -s -X POST "$BASE_URL/shifts/" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"start_time": "'$(date -u +"%Y-%m-%dT%H:%M:%SZ")'"}' | python3 -c "import sys, json; data=json.load(sys.stdin); print(data.get('id', 1))")
echo "Shift ID: $SHIFT_ID"

# 5. Create Washer (Global Admin)
echo -e "\nCreating Washer..."
WASHER_ID=$(curl -s -X POST "$BASE_URL/washers/" \
  -H "Authorization: Bearer $GLOBAL_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Lavador Test",
    "phone": "1234567890",
    "email": "washer@test.com",
    "is_active": true
  }' | python3 -c "import sys, json; data=json.load(sys.stdin); print(data.get('id', 1))")
echo "Washer ID: $WASHER_ID"

# 6. Entry
echo -e "\nRegistering Entry for TEST002..."
curl -s -X POST "$BASE_URL/parking/entry" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "plate": "TEST002",
    "vehicle_type": "carro",
    "owner_name": "Test Owner 2",
    "notes": "Test vehicle"
  }'

# 7. Create Washing Service
echo -e "\nCreating Washing Service (Lavado general)..."
curl -s -X POST "$BASE_URL/washing/services/" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "plate": "TEST002",
    "vehicle_type": "carro",
    "service_type": "Lavado general",
    "price": 20000,
    "washer_id": '$WASHER_ID',
    "shift_id": '$SHIFT_ID',
    "owner_name": "Test Owner 2"
  }'

# 8. Exit
echo -e "\nRegistering Exit for TEST002..."
curl -s -X POST "$BASE_URL/parking/exit" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "plate": "TEST002",
    "notes": "Exit test"
  }'
