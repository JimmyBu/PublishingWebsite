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
from QuestionHub import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('register', views.Register, name='register'),
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
