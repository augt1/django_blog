import os
import requests
from django.conf import settings
from django.core.files.storage import default_storage
from easy_thumbnails.files import get_thumbnailer


def delete_image_and_thumbnails(instance, delete=False):
    # Find is old image exists and is not the same as the new one
    old_image = instance._meta.model.objects.get(pk=instance.pk).image
    if old_image and old_image != instance.image:
        if old_image and default_storage.exists(old_image.name):
            default_storage.delete(old_image.name)
            get_thumbnailer(old_image).delete_thumbnails()
    
    if delete:
        default_storage.delete(instance.image.name)
        get_thumbnailer(instance.image).delete_thumbnails()

        image_path = instance.image.path
        image_dir = os.path.dirname(image_path)

        try:
            os.rmdir(image_dir) #removes if directory is empty only
        except OSError:
            pass #directory not empty, pass


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
