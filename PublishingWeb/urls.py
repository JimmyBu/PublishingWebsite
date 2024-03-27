"""
URL configuration for PublishingWeb project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from QuestionHub import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('chat/friend/<int:pk>', views.detail, name="chat_detail"),
    path("chat/sent_msg/<int:pk>", views.sentMessages, name="sent_msg"),
    path("chat/rec_msg/<int:pk>", views.receivedMessages, name="rec_msg"),
    path("chat/notification", views.chatNotification, name="notification"),
    path('add-friend/<int:friend_id>/', views.add_friend, name='add_friend'),
    path('send-friend-request/<int:friend_id>/', views.send_friend_request, name='send_friend_request'),
    path('reject-friend-request/<int:friend_id>/', views.reject_friend_request, name='reject_friend_request'),
    path('unfriend/<int:friend_id>/', views.unfriend, name='unfriend'),
    path('register', views.Register, name='register'),
    path('edit-profile-pic', views.editProfilePic, name='edit_pic'),
    path('profile', views.my_profile, name='my_profile'),
    path('profile/', views.my_profile, name='my_profile'),
    path('profile/<int:id>/', views.user_profile, name='user_profile'),
    path('login', views.Login, name='login'),
    path('logout', views.Logout, name='logout'),
    path('login/', views.Login, name='login'),
    path('logout/', views.Logout, name='logout'),
    path('reply/', views.reply_list, name='reply'),
    path('comment/<int:comment_id>/', views.edit_comment, name='edit_comment'),
    path('comment/<int:pk>/<str:vote>/', views.upvote_comment, name='upvote_comment'),
    path('post/<int:pk>/<str:vote>/', views.upvote_post, name='upvote_post'),
    path('post/<int:id>/', views.post_detail, name='post_detail'),
    path('comment/<int:id>/<str:delete1>/<str:delete2>/', views.delete_comment, name='delete_comment'),
    path('post/<int:id>/<str:delete1>/<str:delete2>/', views.delete_post, name='delete_post'),
    path('ask/', views.create_post, name='create_post'),
    path('topic/', views.create_topic, name='create_topic'),
    path('topic/<int:id>/', views.topic_detail, name='topic_detail'),
    path('', views.Home, name='home'),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
