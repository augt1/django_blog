import requests
from django.conf import settings


AKISMET_BLOG_URL = settings.AKISMET_BLOG_URL
AKISMET_API_KEY = settings.AKISMET_API_KEY


class AkismetClientError(Exception):
    """Custom exception for Akismet client errors."""

    pass


class AkismetClient:

    AKISMET_VERIFY_URL = "https://rest.akismet.com/1.1/verify-key"
    AKISMET_COMMENT_CHECK = "https://rest.akismet.com/1.1/comment-check"
    # ENdpoint for false negatives
    AKISMET_SUBMIT_SPAM = "https://rest.akismet.com/1.1/submit-spam"
    # Endpoint for false positives
    AKISMET_SUBMIT_HAM = "https://rest.akismet.com/1.1/submit-ham"

    def __init__(self, api_key=AKISMET_API_KEY, blog_url=AKISMET_BLOG_URL):
        self.api_key = api_key
        self.blog_url = blog_url

    def verify_key(self):
        """Authenticates your Akismet API key"""
        data = {
            "key": self.api_key,
            "blog": self.blog_url,
        }

        response = requests.post(self.AKISMET_VERIFY_URL, data=data)

        is_valid = response.text == "valid"
        debug_message = response.headers.get("X-akismet-debug-help")

        if debug_message:
            raise AkismetClientError(f"Akismet debug message: {debug_message}")

        return is_valid

    def comment_check(
        self,
        user_ip,
        comment_content,
        comment_author=None,
        comment_author_email=None,
        comment_type="comment",
    ):
        """Checks if a comment is spam or not"""
        data = {
            "api_key": self.api_key,
            "blog": self.blog_url,
            "user_ip": user_ip,
            "comment_content": comment_content,
            "comment_author": comment_author,
            "comment_author_email": comment_author_email,
            "comment_type": comment_type,
        }

        response = requests.post(
            self.AKISMET_COMMENT_CHECK,
            data=data,
        )
        body = response.text.strip()
        discard = response.headers.get("X-akismet-pro-tip") == "discard"

        if discard:
            status = "discard"
            message = "Your comment was detected as spam and has been discarded."
        elif body == "true":
            status = "spam"
            message = "Your comment is under review and will be published if approved."
        elif body == "false":
            status = "ham"
            message = "Your comment has been accepted and will be published."

        else:
            raise AkismetClientError(f"Unexpected response from Akismet: {body}")
        
        return {"status": status, "message": message}

