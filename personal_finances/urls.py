from django.urls import path
from django.urls import include
from personal_finances.api_server.urls import apiurlpatterns

urlpatterns = [
    path('v1/', include(apiurlpatterns)),
]
