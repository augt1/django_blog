from django.core.files.storage import default_storage
from easy_thumbnails.files import get_thumbnailer
import requests
from django.conf import settings


def delete_image_and_thumbanails(self, image):
    if image and default_storage.exists(image.name):
        default_storage.delete(image.name)
        get_thumbnailer(image).delete_thumbnails()


### TURNSTILE ###
def verify_turnistile_token(request):

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
    

