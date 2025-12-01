#!/bin/bash

# Script para probar el módulo de parking
# Este script ejecuta todos los pasos necesarios para configurar y probar el sistema

echo "========================================="
echo "  PMS - Parking Module Setup & Test"
echo "========================================="
echo ""

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Step 1: Create database tables
echo -e "${BLUE}Step 1: Creating database tables...${NC}"
cd /home/guest/Documents/pms_project/pms-backend
alembic upgrade head
echo -e "${GREEN}✓ Database tables created${NC}"
echo ""

# Step 2: Seed Global Admin
echo -e "${BLUE}Step 2: Creating Global Admin...${NC}"
python scripts/seed_global_admin.py
echo -e "${GREEN}✓ Global Admin created${NC}"
echo ""

# Step 3: Seed Operational Admin
echo -e "${BLUE}Step 3: Creating Operational Admin...${NC}"
python scripts/seed_operational_admin.py
echo -e "${GREEN}✓ Operational Admin created${NC}"
echo ""

# Step 4: Seed Rates
echo -e "${BLUE}Step 4: Creating parking rates...${NC}"
python scripts/seed_rates.py
echo -e "${GREEN}✓ Parking rates created${NC}"
echo ""

# Step 5: Seed Shift
echo -e "${BLUE}Step 5: Creating active shift...${NC}"
python scripts/seed_shift.py
echo -e "${GREEN}✓ Active shift created${NC}"
echo ""

echo -e "${GREEN}=========================================${NC}"
echo -e "${GREEN}  Setup completed successfully!${NC}"
echo -e "${GREEN}=========================================${NC}"
echo ""
echo -e "${YELLOW}Next steps:${NC}"
echo "1. Start the server: uvicorn app.main:app --reload"
echo "2. Access API docs: http://localhost:8000/api/docs"
echo ""
echo -e "${YELLOW}Test credentials:${NC}"
echo "Operational Admin:"
echo "  Email: operador@pms.com"
echo "  Password: operador123"
echo ""
echo "Global Admin:"
echo "  Email: admin@pms.com"
echo "  Password: admin123"
