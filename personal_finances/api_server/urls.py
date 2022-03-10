from django.urls import path
from rest_framework.authtoken import views as authviews
from personal_finances.api_server.views import home, user
from rest_framework.routers import SimpleRouter

router = SimpleRouter()
router.register('user', user.UserManagement)

apiurlpatterns = [
    path('', home.home),
    path('login/', authviews.obtain_auth_token),
    path('delete-token/', user.delete_token),
]

apiurlpatterns.extend(router.urls)