from django.core.exceptions import ValidationError
from PIL import Image


def validate_image_size(image, max_mb=2):
    max_size = max_mb * 1024 * 1024
    if image.size > max_size:
        raise ValidationError(f"Image file size exceeds upload limit (>{max_mb}MB ).")
    

def validate_image_file(file):
    try:
        img = Image.open(file)
        img.verify()
        
    except Exception:
        raise ValidationError("Invalid image file.")