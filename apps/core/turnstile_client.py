import requests
from django.conf import settings


def verify_turnstile_token(request):

    url = "https://challenges.cloudflare.com/turnstile/v0/siteverify"

    token = request.POST.get("cf-turnstile-response")

    data = {
        "secret": settings.TURNSTILE_SECRET_KEY,
        "response": token,
    }

    try:
        response = requests.post(url, data=data)
        response_data = response.json()
        return response_data.get("success", False)

    except requests.RequestException as e:
        print(f"Error verifying Turnstile token: {e}")
        return False
