from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from pydantic import ValidationError

import models
from config import settings
from database import users_collection

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")

async def get_current_active_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
        token_data = models.TokenData(email=email)
    except (JWTError, ValidationError):
        raise credentials_exception

    user = await users_collection.find_one({"email": token_data.email})
    if user is None:
        raise credentials_exception
    return user