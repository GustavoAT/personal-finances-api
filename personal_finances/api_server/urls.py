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
    path('change-password/', views.change_password),
    path('account/', views.AccountView.as_view()),
    path('account/<int:id>/', views.AccountView.as_view()),
    path('category/', views.CategoryView.as_view()),
    path('category/<int:id>/', views.CategoryView.as_view()),
    path('subcategory/', views.SubcategoryView.as_view()),
    path('subcategory/<int:id>/', views.SubcategoryView.as_view()),
    path('transaction/', views.TransactionView.as_view()),
    path('transaction/<int:id>/', views.TransactionView.as_view()),
    path('credit-card/', views.CreditCardView.as_view()),
    path('credit-card/<int:id>/', views.CreditCardView.as_view()),
    path(
        'credit-card/<int:credit_card_id>/expense/',
        views.CreditCardExpenseView.as_view()
    ),
    path(
        'credit-card/<int:credit_card_id>/expense/<int:id>/',
        views.CreditCardExpenseView.as_view()
    ),
    path('transference/', views.create_transference),
    path('total-balance/', views.get_total_balance),
]

apiurlpatterns.extend(router.urls)