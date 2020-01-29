from django.urls import path

from . import views


app_name = 'score'

urlpatterns = [
    path('applications/', views.ApplicationsView.as_view(), name='applications'),
    path('add-applicant/', views.AddApplicantView.as_view(), name='add_applicant'),
    path('add-property/', views.AddPropertyView.as_view(), name='add_property'),
    path('applicant/<aidb64>/<token>/', views.ApplicantView.as_view(), name='applicant_entry'),
]
