from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('room/<str:pk>/', views.room, name='room'),
    path('create-room/', views.createRoom, name='create-room'),
    path('update-room/<str:pk>/', views.updateRoom, name='update-room'),
    path('delete-room/<str:pk>/', views.deleteRoom, name='delete-room'),
    path('login-page/',views.userLogin,name='login-page'),
    path('logout-page/',views.userLogout,name='logout-page'),
    path('register-page/',views.userRegister,name='register-page'),
    path('delete-msg/<str:pk>/',views.deleteMessage,name='delete-msg'),
    path('user-profile/<str:pk>/',views.userProfile,name='user-profile'),
    path('update-user/',views.updateUser,name='update-user'),



]
