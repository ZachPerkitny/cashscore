from django.contrib.auth import views as auth_views
from django.urls import path

from . import views


app_name = 'accounts'

urlpatterns = [
    path('activate/<uidb64>/<token>/', views.ActivationView.as_view(), name='activate'),
    path('login/', auth_views.LoginView.as_view(template_name='accounts/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('signup/', views.SignUpView.as_view(), name='signup'),
    path('account/', views.PaymentMethodsView.as_view(), name='edit_account'),
]
