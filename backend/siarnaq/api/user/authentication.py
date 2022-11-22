from google.auth.exceptions import GoogleAuthError
from google.auth.transport import requests
from google.oauth2 import id_token
from rest_framework import authentication
from rest_framework.exceptions import AuthenticationFailed

import siarnaq.gcloud as gcloud
from siarnaq.api.user.models import User


class GoogleCloudAuthentication(authentication.BaseAuthentication):
    """
    Authenticate the Google Cloud service account for the internal API.

    Some internal services in Galaxy need to make privileged API calls, and we want to
    authenticate them in a password-free way. This can be achieved by assuming the
    Google Cloud service account identity, which we verify here.
    """

    INTERNAL_API_USER_AGENTS = ["Google-Cloud-Scheduler", "Galaxy-Saturn"]
    """
    User agents from which an internal API call could originate. Requests with one of
    these user agent headers will be authenticated with this method, and denied access
    if authentication fails.
    """

    AUTHORIZATION_HEADER_TYPE = "Bearer"
    """The supported authorization scheme."""

    WWW_AUTHENTICATE_REALM = "api"
    """Realm for any WWW-Authenticate headers returned in a HTTP 401 response."""

    def authenticate(self, request):
        """Try to authenticate a request as the Google Cloud service agent."""
        user_agent = request.META.get("HTTP_USER_AGENT")
        if user_agent not in self.INTERNAL_API_USER_AGENTS:
            return None  # Not an attempt to authorize
        header = request.META.get("HTTP_AUTHORIZATION")
        if not header:
            return None  # Not an attempt to authorize

        try:
            method, token = header.split()
        except ValueError:
            raise AuthenticationFailed("Malformed authorization header")
        if method.lower() != self.AUTHORIZATION_HEADER_TYPE.lower():
            raise AuthenticationFailed("Unsupported authorization scheme")

        try:
            idinfo = id_token.verify_oauth2_token(
                id_token=token,
                request=requests.Request(),
            )
        except (ValueError, GoogleAuthError):
            raise AuthenticationFailed("Invalid authorization token")
        if idinfo.get("email") != gcloud.admin_email:
            raise AuthenticationFailed("Unauthorized client")

        user, _ = User.objects.get_or_create(
            username=gcloud.admin_username,
            email=gcloud.admin_email,
            is_staff=True,
        )
        return (user, None)

    def authenticate_header(self, request):
        """Return the challenge for the WWW-Authenticate header."""
        return f'{self.AUTHORIZATION_HEADER_TYPE} realm="{self.WWW_AUTHENTICATE_REALM}"'