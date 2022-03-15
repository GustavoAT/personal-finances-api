from django.urls import path
from rest_framework.authtoken import views as authviews
from personal_finances.api_server import views
from rest_framework.routers import SimpleRouter

router = SimpleRouter()
router.register('user', views.UserManagement)

apiurlpatterns = [
    path('', views.Home.as_view()),
    path('login/', authviews.obtain_auth_token),
    path('delete-token/', views.DeleteToken.as_view()),
    path('account/', views.AccountView.as_view()),
    path('account/<int:id>/', views.AccountView.as_view()),
]

apiurlpatterns.extend(router.urls)