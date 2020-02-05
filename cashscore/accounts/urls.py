from django.contrib.auth import views as auth_views
from django.urls import path

from . import views


app_name = 'accounts'

urlpatterns = [
    path('activate/<uidb64>/<token>/', views.ActivationView.as_view(), name='activate'),
    path('login/', auth_views.LoginView.as_view(template_name='accounts/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('signup/', views.SignUpView.as_view(), name='signup'),
    path('account/', views.AccountView.as_view(), name='account'),
    path('account/payment-methods/', views.PaymentMethodsView.as_view(), name='payment_methods'),
    path('account/payment-methods/delete/<id>/', views.DeletePaymentMethodView.as_view(), name='delete_payment_method'),
    path('account/payment-methods/set-default/<id>/', views.SetDefaultPaymentMethodView.as_view(), name='set_default_payment_method'),
    path('password-reset/', views.PasswordResetView.as_view(), name='password_reset'),
    path('password-reset/done/', views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('reset/done/', views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),
]
