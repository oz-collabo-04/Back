from asgiref.sync import sync_to_async
from channels.sessions import CookieMiddleware
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from rest_framework_simplejwt.tokens import AccessToken

User = get_user_model()


class JWTAuthMiddleware:
    """
    Custom middleware for JWT authentication in Django Channels.
    """

    def __init__(self, inner):
        self.inner = inner

    async def __call__(self, scope, receive, send):
        # Check for headers in the scope
        if "headers" not in scope:
            raise ValueError(
                "JWTAuthMiddleware was passed a scope without headers. "
                "Ensure it's only used for HTTP or WebSocket connections."
            )

        # Find the Authorization header
        token = None

        # Sec-WebSocket-Protocol 에서 토큰을 추출
        if "subprotocols" in scope:
            token = scope["subprotocols"][0]

        # Authenticate the token and set the user in scope
        scope["user"] = await self.authorize(token)
        return await self.inner(scope, receive, send)

    @sync_to_async
    def authorize(self, token):
        """
        Authorize user based on the JWT token.
        """
        if not token:
            return AnonymousUser()

        try:
            decoded_access = AccessToken(token)
            user_id = decoded_access.get("user_id")

            if not user_id:
                raise ValueError("Invalid user_id in token")

            user = User.objects.get(id=user_id)
            return user
        except (User.DoesNotExist, ValueError, TokenError, InvalidToken):
            return AnonymousUser()


def JWTAuthMiddlewareStack(inner):
    return CookieMiddleware(JWTAuthMiddleware(inner))
