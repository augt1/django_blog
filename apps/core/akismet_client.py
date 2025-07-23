import requests
from django.conf import settings

AKISMET_BLOG_URL = settings.AKISMET_BLOG_URL
AKISMET_API_KEY = settings.AKISMET_API_KEY


class AkismetClientError(Exception):
    """Custom exception for Akismet client errors."""

    pass


class AkismetClient:
    """
    Expected kwargs:
        user_ip (str, required): IP address of the commenter
        comment_content (str, optional): Content of the comment
        comment_author (str, optional): Author's name
        comment_author_email (str, optional): Author's email
        comment_type (str, optional): Type of the comment
        # https://akismet.com/developers/detailed-docs/submit-spam-missed-spam/
    """

    AKISMET_VERIFY_URL = "https://rest.akismet.com/1.1/verify-key"
    AKISMET_COMMENT_CHECK = "https://rest.akismet.com/1.1/comment-check"
    # This call is for submitting comments that weren’t marked as spam but should have been.
    AKISMET_SUBMIT_SPAM = "https://rest.akismet.com/1.1/submit-spam"
    # This call is intended for the submission of false positives – items that were incorrectly classified as spam by Akismet.
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

    def comment_check(self, **kwargs):
        """Checks if a comment is spam or not"""
        data = self._build_data_dict(**kwargs)

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
            message = "Your comment has been posted successfully."

        else:
            raise AkismetClientError(f"Unexpected response from Akismet: {body}")

        return {"status": status, "message": message}

    def submit_ham(self, **kwargs):
        data = self._build_data_dict(**kwargs)

        response = requests.post(self.AKISMET_SUBMIT_HAM, data=data)
        if response.status_code != 200:
            raise AkismetClientError(f"Failed to submit ham: {response.text}")

    def submit_spam(self, **kwargs):
        data = self._build_data_dict(**kwargs)

        response = requests.post(self.AKISMET_SUBMIT_SPAM, data=data)
        if response.status_code != 200:
            raise AkismetClientError(f"Failed to submit spam: {response.text}")

    def _build_data_dict(self, **kwargs):

        data = {
            "api_key": self.api_key,
            "blog": self.blog_url,
        }

        data.update({k: v for k, v in kwargs.items() if v is not None})

        return data
