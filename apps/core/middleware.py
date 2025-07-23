import zoneinfo

from django.utils import timezone


class TimezoneMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        
        # if request.POST.get('timezone'):
        tzname = request.session.get("user_timezone")
        if tzname:

            try:
                timezone.activate(zoneinfo.ZoneInfo(tzname))
            except Exception:
                timezone.deactivate()        
        else:
            print("deactiate")
            timezone.deactivate()
        return self.get_response(request)



