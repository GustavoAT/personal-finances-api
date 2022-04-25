from rest_framework.throttling import UserRateThrottle

from personal_finances.api_server.models import UserExtras

class PremiumUserRateThrottle(UserRateThrottle):
    def __init__(self):
        pass
    
    def allow_request(self, request, view):
        self.rate = self.get_rate()
        user = request.user
        if user.is_staff:
            self.scope = 'admin'
            self.rate = self.get_rate()
            self.num_requests, self.duration = self.parse_rate(self.rate)
            return super().allow_request(request, view)
        try:
            usertype = user.userextras.type
        except UserExtras.DoesNotExist:
            return self.throttle_failure()
        if usertype == UserExtras.PREMIUM:
            self.scope = 'premium'
            self.rate = self.get_rate()
            
        self.num_requests, self.duration = self.parse_rate(self.rate)
        return super().allow_request(request, view)