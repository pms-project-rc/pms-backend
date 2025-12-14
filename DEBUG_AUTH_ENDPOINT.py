"""
Debug endpoint for testing JWT token creation and validation
Add this to app/api/routes/v1/auth/auth_routes.py if you want to test manually
"""

# This is just documentation - add this route if you want to debug JWT tokens

# @router.post("/debug/login", response_model=TokenResponse)
# async def debug_login(
#     data: LoginRequest, 
#     washer_repo: WasherRepositoryImpl = Depends(get_washer_repo)
# ):
#     """Debug endpoint - logs exactly what's being created"""
#     import json
#     
#     washer = await washer_repo.get_by_email(data.email)
#     if not washer:
#         raise HTTPException(status_code=401, detail="Washer not found")
#     
#     if not verify_password(data.password, washer.password_hash):
#         raise HTTPException(status_code=401, detail="Incorrect password")
#     
#     if not washer.is_active or not washer.id:
#         raise HTTPException(status_code=401, detail="Washer not active")
#     
#     # Create token with all claims
#     additional_claims = {
#         "role": "washer",
#         "user_id": washer.id,
#         "username": washer.email
#     }
#     
#     print(f"[DEBUG] Creating token with claims: {json.dumps(additional_claims)}")
#     
#     access_token = create_access_token(
#         subject=washer.id, 
#         additional_claims=additional_claims
#     )
#     
#     # Decode to verify
#     from jose import jwt
#     from app.core.config import settings
#     decoded = jwt.decode(access_token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
#     print(f"[DEBUG] Token decoded verification: {json.dumps(decoded)}")
#     
#     response = TokenResponse(
#         access_token=access_token,
#         token_type="bearer",
#         user_id=washer.id,
#         email=washer.email,
#         role="washer"
#     )
#     
#     print(f"[DEBUG] Response: {response.model_dump()}")
#     
#     return response
