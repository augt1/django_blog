import akismet
from django.conf import settings


config = akismet.Config(key=settings.AKISMET_API_KEY, url=settings.AKISMET_BLOG_URL)
akismet_client = akismet.SyncClient.validated_client(config=config)



def check_is_spam(user_ip, comment_content, comment_author=None, comment_author_email=None, comment_type="comment"):
    try:
        classification = akismet_client.comment_check(
            user_ip=user_ip,
            comment_content=comment_content,
            comment_author=comment_author,
            comment_author_email=comment_author_email,
            comment_type=comment_type
        )


        if classification == akismet.CheckResponse.DISCARD:
            # The post was "blatant" spam, reject it.
            message = "Your comment was detected as spam and has been discarded."
            return True, 2, message
        elif classification == akismet.CheckResponse.SPAM:
            # Send it into the manual-review queue.
            message = "Your comment is under review and will be published if approved."
            return True, 1, message
        elif classification == akismet.CheckResponse.HAM:
            # The post wasn't spam, allow it.
            message = "Your comment has been accepted."
            return False, 0, message

    
    except Exception as e:
        print(f"Akismet spam check error: {e}")
        return False