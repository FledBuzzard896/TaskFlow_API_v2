import httpx
from fastapi import HTTPException, Depends, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import jwt, JWTError, jwk
from keycloak import KeycloakOpenID
from app.core.config import settings


security = HTTPBearer()


# Инициализация клиента Keycloak
keycloak_openid = KeycloakOpenID(
    server_url=settings.KEYCLOAK_URL,
    client_id=settings.KEYCLOAK_CLIENT_ID,
    realm_name=settings.KEYCLOAK_REALM,
    client_secret_key=settings.KEYCLOAK_CLIENT_SECRET,
)


def decode_token(token: str) -> dict:
    try:
        # Получаем JWKS (публичные ключи) от Keycloak
        jwks_url = f"{settings.KEYCLOAK_URL}/realms/{settings.KEYCLOAK_REALM}/protocol/openid-connect/certs"
        with httpx.Client() as client:
            response = client.get(jwks_url)
            jwks_data = response.json()

        # Берём первый ключ
        key_data = jwks_data['keys'][0]
        public_key = jwk.construct(key_data)

        # Декодируем без проверки аудитории и издателя (для упрощения)
        payload = jwt.decode(
            token,
            public_key,
            algorithms=["RS256"],
            options={
                "verify_aud": False,  # отключаем проверку аудитории
                "verify_iss": False,  # отключаем проверку издателя
            }
        )
        return payload
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid token, {e}",
            headers={"WWW-Authenticate": "Bearer"},
        ) from e


def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> dict:
    token = credentials.credentials
    payload = decode_token(token)

    return {
        "user_id": payload.get("sub"),
        "preferred_username": payload.get("preferred_username"),
        "email": payload.get("email"),
        "name": payload.get("name"),
        "roles": payload.get("realm_access", {}).get("roles", []),
    }