from django.urls import path, include
from rest_framework.routers import SimpleRouter
from spamapp import views  # Adjust 'apis' to point to the correct module where 'signup' view is defined
from rest_framework.routers import DefaultRouter

urlpatterns = [
    path('/signup', views.register_user, name='signup'),
    path('/login',views.login_user,name="login"),
    path("/spam",views.spam_number),
    path("/searchbyname",views.get_by_name),
    path("/searchbyphonenumber",views.get_by_phone_number),
    path('/user_details/<str:phone_number>/', views.get_user_details, name='get_user_details'),    # path("/search")
]








