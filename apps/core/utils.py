from django.core.files.storage import default_storage
from easy_thumbnails.files import get_thumbnailer


def delete_image_and_thumbanails(self, image):
    if image and default_storage.exists(image.name):
        default_storage.delete(image.name)
        get_thumbnailer(image).delete_thumbnails()
