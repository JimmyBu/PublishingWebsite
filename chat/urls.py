from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name="index"),
    path('friend/<str:pk>', views.detail, name="detail"),
    path("sent_msg/<str:pk>", views.sentMessages, name="sent_msg"),
    path("rec_msg/<str:pk>", views.receivedMessages, name="rec_msg"),
    path("notification", views.chatNotification, name="notification"),
    path('create-profile/', views.create_profile, name='create_profile'),
    path('add-friend/<int:friend_id>/', views.add_friend, name='add_friend'),
    path('friends/', views.friends_list, name='friends_list'),
    path('search-user/', views.search_user, name='search_user'),
]
