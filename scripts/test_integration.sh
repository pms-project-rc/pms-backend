#!/bin/bash
BASE_URL="http://localhost:8000/api/v1"

# 1. Login Global Admin
echo "Logging in Global Admin..."
GLOBAL_TOKEN=$(curl -s -X POST $BASE_URL/auth/login/global-admin \
  -H "Content-Type: application/json" \
  -d '{"email": "admin@pms.com", "password": "admin123"}' | python3 -c "import sys, json; print(json.load(sys.stdin)['access_token'])")

if [ -z "$GLOBAL_TOKEN" ]; then
    echo "Failed to login global admin"
    exit 1
fi

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

if [ -z "$TOKEN" ]; then
    echo "Failed to login operational admin"
    exit 1
fi

# 4. Entry
echo -e "\nRegistering Entry for TEST001..."
curl -s -X POST "$BASE_URL/parking/entry" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "plate": "TEST001",
    "vehicle_type": "carro",
    "notes": "Test vehicle"
  }'

# 5. Create Washing Service
echo -e "\nCreating Washing Service (Lavado general)..."
# Assuming washer 1 and shift 1 exist. If not, this might fail.
# We'll try to get a washer first or just assume ID 1.
curl -s -X POST "$BASE_URL/washing/" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "plate": "TEST001",
    "vehicle_type": "carro",
    "service_type": "Lavado general",
    "price": 20000,
    "washer_id": 1,
    "shift_id": 1,
    "owner_name": "Test Owner"
  }'

# 6. Exit
echo -e "\nRegistering Exit for TEST001..."
curl -s -X POST "$BASE_URL/parking/exit" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "plate": "TEST001",
    "notes": "Exit test"
  }'
