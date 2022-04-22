from rest_framework.throttling import UserRateThrottle

from personal_finances.api_server.models import UserExtras

class PremiumUserRateThrottle(UserRateThrottle):
    def __init__(self):
        pass
    
    def allow_request(self, request, view):
        try:
            usertype = request.user.userextras.type
        except UserExtras.DoesNotExist:
            return super().allow_request(request, view)
        if usertype == UserExtras.PREMIUM:
            self.scope = 'premium'
        self.num_requests, self.duration = self.parse_rate(self.get_rate())
        return super().allow_request(request, view)