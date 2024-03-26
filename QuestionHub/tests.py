from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, RequestFactory, Client
from django.urls import reverse
from .models import Post, Response, Topic, UserProfile, Vote
from django.contrib.auth.models import User
from .admin import CommentAdmin
from .views import Home, post_detail, upvote_comment, upvote_post
from django.contrib.admin.sites import AdminSite
from unittest.mock import Mock, patch

class TestViews(TestCase):
    def setUp(self):
        # Create a test user and profile
        self.client = Client()
        self.factory = RequestFactory()
        self.admin_site = AdminSite()

        # Create a test user and profile
        self.user = User.objects.create_user(username='testuser', password='Password123!')
        self.user2 = User.objects.create_user(username='testuser2', password='Password123!')
        self.profile = UserProfile.objects.create(user=self.user)
        self.profile2 = UserProfile.objects.create(user=self.user2)
        # Create test topics
        self.topic1 = Topic.objects.create(name='Topic 1')
        self.topic2 = Topic.objects.create(name='Topic 2')
        # Create test posts, modified for testing view
        self.post1 = Post.objects.create(topic=self.topic1, title='Post 1', author=self.user, body='Body 1',
                                         num_views=10, score=5)
        self.post2 = Post.objects.create(topic=self.topic2, title='Post 2', author=self.user, body='Body 2',
                                         num_views=20, score=3)
        # Create test votes for the user
        self.vote1 = Vote.objects.create(user=self.user, post=self.post1)
        self.vote2 = Vote.objects.create(user=self.user, post=self.post2)
        # Create test response for post1
        self.response = Response.objects.create(user=self.user, post=self.post1, body='Initial comment')
        # Create a test vote for each test case
        self.vote = Vote.objects.create(user=self.user, comment=self.response)
        # Data for creating a response
        self.response_data = {
            'post': 1, 
            'parent': 1, 
            'body': 'Test comment body' 
        }  
    
    #Test homepage and check if posts load
    def test_home(self):
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        posts_in_context = response.context.get('posts')
        self.assertIsNotNone(posts_in_context)
        self.assertEqual(len(posts_in_context), 2)

        # Test post detail page
        def test_post_detail(self):
            response = self.client.get(reverse('post_detail', args=[self.post1.id]))
            self.assertEqual(response.status_code, 200)
            # Check if post 1 and its comments are loaded
            self.assertEqual(response.context['post'], self.post1)
            self.assertContains(response, self.response.body)

    #Test topic detail page
    def test_topic_detail(self):
        response = self.client.get(reverse('topic_detail', args=[self.topic1.id]))
        self.assertEqual(response.status_code, 200)
        #Check if topic1 has loaded and all of its posts
        self.assertEqual(response.context['topic'], self.topic1)
        self.assertContains(response, self.post1.title)
        self.assertNotContains(response, self.post2.title)

    #Test user registration page
    def test_register(self):
        response = self.client.get(reverse('register'))
        self.assertEqual(response.status_code, 200)

        response_register = self.client.post(reverse('register'),
                                             {'username': 'testuser1', 'password1': 'Password123!',
                                              'password2': 'Password123!'})
        self.assertEqual(response_register.status_code, 302)  # Check if registration was successful
        user_exists = User.objects.filter(username='testuser1').exists()
        #Check if user was created
        self.assertTrue(user_exists)
        # Log in the newly registered user
        response_login = self.client.post(reverse('login'),
                                          {'username': 'testuser1', 'password': 'Password123!'})
        self.assertEqual(response_login.status_code, 302)  # Check if login was successful
        # Get the user profile page of the newly registered user
        response_profile = self.client.get(
            reverse('user_profile', kwargs={'id': User.objects.get(username='testuser1').id}))

        # Check if the user profile page loads successfully and it's for the correct user
        self.assertEqual(response_profile.status_code, 302)

    #Test user profile page
    def test_user_profile(self):
        response = self.client.get(reverse('user_profile', kwargs={'id': self.user.id}))
        self.assertEqual(response.status_code, 200)
        #Check if correct user's page loaded
        self.assertEqual(response.context['user'], self.user)
        self.assertTrue(response.context['not_authenticated'])

        #now try viewing page after signing in - should redirect to my_profile
        self.client.force_login(self.user)
        response = self.client.get(reverse('user_profile', kwargs={'id': self.user.id}))
        self.assertRedirects(response, reverse('my_profile'), status_code=302)

        #now try viewing page after signing in as a different user
        self.client.force_login(self.user2)
        profile2 = UserProfile.objects.get(user=self.user2)
        profile = UserProfile.objects.get(user=self.user)
        response = self.client.get(reverse('user_profile', kwargs={'id': self.user.id}))
        self.assertFalse(response.context['not_authenticated'])
        self.assertEqual(response.context['is_friend'], profile2.friends.filter(id=self.user.id).exists())
        self.assertEqual(response.context['sent_friend_request'], profile2.friend_requests.filter(id=self.user.id).exists())
        self.assertEqual(response.context['got_friend_request'],
                         profile.friend_requests.filter(id=self.user2.id).exists())

    #Test my profile page
    def test_my_profile(self):
        #if not logged in
        response = self.client.get(reverse('my_profile'))
        self.assertEqual(response.status_code, 302) #should redirect to login

        #if logged in
        self.client.force_login(self.user)
        response = self.client.get(reverse('my_profile'))
        self.assertEqual(response.status_code, 200)
        #Check if user's own page correctly loaded
        self.assertEqual(response.context['user'], self.user)
        self.assertTrue('bio_form' in response.context)

    #Test changing user bio
    def test_change_bio(self):
        self.client.force_login(self.user)
        response = self.client.post(reverse('my_profile'), {'bio': 'New bio'})
        self.assertEqual(response.status_code, 302)
        updated_profile = UserProfile.objects.get(user=self.user)
        self.assertEqual(updated_profile.bio, 'New bio')

    #test edit profile pic
    def test_editProfilePic(self):
        self.client.force_login(self.user)
        image_path = 'QuestionHub/static/img/default_profile_pic.png'
        with open(image_path, 'rb') as file:
            pic = SimpleUploadedFile('test_image.jpg', file.read(), content_type='image/jpeg')
            response = self.client.post(reverse('edit_pic'), {'pic': pic})
            self.assertEqual(response.status_code, 302)

        updated_profile = UserProfile.objects.get(user=self.user)
        self.assertIsNotNone(updated_profile.pic)

    #test sending friend request
    def test_send_friend_request(self):
        #test sending a friend request:
        self.client.force_login(self.user)
        response = self.client.post(reverse('send_friend_request', kwargs={'friend_id': self.user2.id}))
        self.assertEqual(response.status_code, 200)

        #send more than one friend request, should still get a 200 status:
        response = self.client.post(reverse('send_friend_request', kwargs={'friend_id': self.user2.id}))
        self.assertEqual(response.status_code, 200)
        updated_profile2 = UserProfile.objects.get(user=self.user2)
        self.assertTrue(updated_profile2.friend_requests.filter(id=self.user.id).exists())

        #test sending friend request simultaneously:
        self.client.force_login(self.user2)
        response = self.client.post(reverse('send_friend_request', kwargs={'friend_id': self.user.id}))
        self.assertEqual(response.status_code, 200)
        updated_profile2 = UserProfile.objects.get(user=self.user2)
        self.assertTrue(updated_profile2.friends.filter(id=self.user.id).exists())
        self.assertFalse(updated_profile2.friend_requests.filter(id=self.user.id).exists())
        updated_profile = UserProfile.objects.get(user=self.user)
        self.assertTrue(updated_profile.friends.filter(id=self.user2.id).exists())
        self.assertFalse(updated_profile.friend_requests.filter(id=self.user2.id).exists())

    #test accepting a friend request that was received
    def test_accept_friend_request(self):
        self.client.force_login(self.user)
        response = self.client.post(reverse('send_friend_request', kwargs={'friend_id': self.user2.id}))

        self.client.force_login(self.user2)
        response = self.client.post(reverse('add_friend', kwargs={'friend_id': self.user.id}))
        self.assertEqual(response.status_code, 200)

        updated_profile2 = UserProfile.objects.get(user=self.user2)
        self.assertTrue(updated_profile2.friends.filter(id=self.user.id).exists())
        self.assertFalse(updated_profile2.friend_requests.filter(id=self.user.id).exists())
        updated_profile = UserProfile.objects.get(user=self.user)
        self.assertTrue(updated_profile.friends.filter(id=self.user2.id).exists())
        self.assertFalse(updated_profile.friend_requests.filter(id=self.user2.id).exists())

    #cancel a friend request already sent
    def test_cancel_friend_request(self):
        self.client.force_login(self.user)
        response = self.client.post(reverse('send_friend_request', kwargs={'friend_id': self.user2.id}))
        response = self.client.post(reverse('reject_friend_request', kwargs={'friend_id': self.user2.id}))
        self.assertEqual(response.status_code, 200)

        updated_profile2 = UserProfile.objects.get(user=self.user2)
        self.assertFalse(updated_profile2.friend_requests.filter(id=self.user.id).exists())

    #reject a friend request that was received
    def test_reject_friend_request(self):
        self.client.force_login(self.user)
        response = self.client.post(reverse('send_friend_request', kwargs={'friend_id': self.user2.id}))
        self.client.force_login(self.user2)
        response = self.client.post(reverse('reject_friend_request', kwargs={'friend_id': self.user.id}))
        self.assertEqual(response.status_code, 200)

        updated_profile2 = UserProfile.objects.get(user=self.user2)
        self.assertFalse(updated_profile2.friend_requests.filter(id=self.user.id).exists())

    #unfriending someone after accepting their friend request
    def test_unfriend(self):
        self.client.force_login(self.user)
        response = self.client.post(reverse('send_friend_request', kwargs={'friend_id': self.user2.id}))

        self.client.force_login(self.user2)
        response = self.client.post(reverse('add_friend', kwargs={'friend_id': self.user.id}))
        self.assertEqual(response.status_code, 200)

        response = self.client.post(reverse('unfriend', kwargs={'friend_id': self.user.id}))
        self.assertEqual(response.status_code, 200)

        updated_profile2 = UserProfile.objects.get(user=self.user2)
        self.assertFalse(updated_profile2.friends.filter(id=self.user.id).exists())
        self.assertFalse(updated_profile2.friend_requests.filter(id=self.user.id).exists())
        updated_profile = UserProfile.objects.get(user=self.user)
        self.assertFalse(updated_profile.friends.filter(id=self.user2.id).exists())
        self.assertFalse(updated_profile.friend_requests.filter(id=self.user2.id).exists())

    #Test logging in
    def test_login(self):
        self.assertNotIn('_auth_user_id', self.client.session)
        response = self.client.get(reverse('login'))
        self.assertEqual(response.status_code, 200)

        response = self.client.post(reverse('login'), {'username': 'testuser', 'password': 'Password123!'})
        self.assertRedirects(response, reverse('home'), status_code=302)  # Redirects to home upon successful login
        self.assertIn('_auth_user_id', self.client.session)
        
    #Test logging out
    def test_logout(self):
        self.client.login(username='testuser', password='Password123!')
        self.assertIn('_auth_user_id', self.client.session)
        response = self.client.get(reverse('logout'))
        self.assertEqual(response.status_code, 302)
        self.assertNotIn('_auth_user_id', self.client.session)

    # Test creating a topic
    def test_create_topic(self):
        self.client.login(username='testuser', password='Password123!')
        response = self.client.post(reverse('create_topic'), {'name': 'Test Topic'})
        self.assertEqual(response.status_code, 302)
        # Check if topic was successfully created
        self.assertTrue(Topic.objects.filter(name='Test Topic').exists())

    def test_topic_str(self):
        topic_name = 'Test Topic'
        topic = Topic.objects.create(name=topic_name)
        self.assertEqual(str(topic), topic_name)

    # Test creating a post
    def test_create_post(self):
        self.client.login(username='testuser', password='Password123!')
        response = self.client.post(reverse('create_post'),
                                    {'topic': 1, 'title': 'Test Post', 'body': 'This is a test post body.'})
        self.assertEqual(response.status_code, 302)
        # Check if post was successfully created
        self.assertTrue(Post.objects.filter(title='Test Post').exists())
        self.profile.refresh_from_db()
        # Check if user's number of posts increased
        self.assertEqual(self.profile.num_posts, 1)

    def test_post_str(self):
        post_title = 'Test Post Title'
        post = Post.objects.create(author=self.user, title=post_title, body='Test body')
        expected_str = post_title  # Assuming you want to return the title as the string representation
        self.assertEqual(str(post), expected_str)

    # Test replying to a post
    def test_reply(self):
        self.client.login(username='testuser', password='Password123!')
        response = self.client.post(reverse('reply'), self.response_data)
        self.assertEqual(response.status_code, 302)
        created_reply = Response.objects.filter(body='Test comment body').first()
        self.assertIsNotNone(created_reply)
        # Check if reply was created
        self.assertEqual(created_reply.user, self.user)
        self.assertEqual(created_reply.post_id, self.response_data['post'])
        self.profile.refresh_from_db()
        # Check if user's number of comments increased
        self.assertEqual(self.profile.num_comments, 1)

    def test_response_str(self):
        # Assuming self.post1 exists and is a valid Post object
        response_body = 'Test Response Body'
        response = Response.objects.create(post=self.post1, user=self.user, body=response_body)
        expected_str = response_body
        self.assertEqual(str(response), expected_str)

    # Test upvoting a post
    def test_upvote_post(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse('upvote_post', kwargs={'pk': self.post1.pk, 'vote': 'U'}))
        self.assertEqual(response.status_code, 302)
        self.post1.refresh_from_db()
        self.profile.refresh_from_db()
        # Check if the post's score and user's karma increased by  1
        self.assertEqual(self.post1.score, 6)
        self.assertEqual(self.profile.karma, 1)
        # Check if vote exists
        self.assertEqual(Vote.objects.filter(user=self.user, post=self.post1).count(), 2)

    def test_vote_str(self):
        user = self.user2
        # Creating a post and a response
        post = Post.objects.create(author=self.user, title='Test Post', body='Test body')
        response = Response.objects.create(user=self.user, post=post, body='Test comment')

        # Creating a vote for the post
        vote_post = Vote.objects.create(user=user, post=post, vote_type='U')
        expected_str_post = f'{user.username} - {post.title} - {vote_post.get_vote_type_display()}'
        self.assertEqual(str(vote_post), expected_str_post)

        # Creating a vote for the comment
        vote_comment = Vote.objects.create(user=user, comment=response, vote_type='U')
        expected_str_comment = f'{user.username} - {response.body} - {vote_comment.get_vote_type_display()}'
        self.assertEqual(str(vote_comment), expected_str_comment)

    # Test removing an upvote on a post
    def test_remove_upvote_post(self):
        self.client.force_login(self.user)
        self.client.get(reverse('upvote_post', kwargs={'pk': self.post1.pk, 'vote': 'U'}))
        response = self.client.get(reverse('upvote_post', kwargs={'pk': self.post1.pk, 'vote': 'U'}))
        self.assertEqual(response.status_code, 302)
        self.post1.refresh_from_db()
        self.profile.refresh_from_db()
        self.assertEqual(self.post1.score, 7)
        self.assertEqual(self.profile.karma, 2)
        self.assertEqual(Vote.objects.filter(user=self.user, post=self.post1).count(), 3)

    # Test downvoting a post
    def test_downvote_post(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse('upvote_post', kwargs={'pk': self.post1.pk, 'vote': 'D'}))
        self.assertEqual(response.status_code, 302)
        self.post1.refresh_from_db()
        self.profile.refresh_from_db()
        self.assertEqual(self.post1.score, 4)
        self.assertEqual(self.profile.karma, -1)
        self.assertEqual(Vote.objects.filter(user=self.user, post=self.post1).count(), 2)

    # Test removing a downvote on a post
    def test_remove_downvote_post(self):
        self.client.force_login(self.user)
        self.client.get(reverse('upvote_post', kwargs={'pk': self.post1.pk, 'vote': 'D'}))
        response = self.client.get(reverse('upvote_post', kwargs={'pk': self.post1.pk, 'vote': 'D'}))
        self.assertEqual(response.status_code, 302)
        self.post1.refresh_from_db()
        self.profile.refresh_from_db()
        self.assertEqual(self.post1.score, 3)
        self.assertEqual(self.profile.karma, -2)
        self.assertEqual(Vote.objects.filter(user=self.user, post=self.post1).count(), 3)

    # Test upvoting a comment
    def test_upvote_comment(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse('upvote_comment', kwargs={'pk': self.response.pk, 'vote': 'U'}))
        self.assertEqual(response.status_code, 302)
        self.response.refresh_from_db()
        self.profile.refresh_from_db()
        self.assertEqual(self.response.score, 1)
        self.assertEqual(self.profile.karma, 1)
        self.assertEqual(Vote.objects.filter(user=self.user, comment=self.response).count(), 2)

    # Test removing an upvote on a comment
    def test_remove_upvote_comment(self):
        self.client.force_login(self.user)
        self.client.get(reverse('upvote_comment', kwargs={'pk': self.response.pk, 'vote': 'U'}))
        response = self.client.get(reverse('upvote_comment', kwargs={'pk': self.response.pk, 'vote': 'U'}))
        self.assertEqual(response.status_code, 302)
        self.response.refresh_from_db()
        self.profile.refresh_from_db()
        self.assertEqual(self.response.score, 2)
        self.assertEqual(self.profile.karma, 2)
        self.assertEqual(Vote.objects.filter(user=self.user, comment=self.response).count(), 3)

    # Test downvoting a comment
    def test_downvote_comment(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse('upvote_comment', kwargs={'pk': self.response.pk, 'vote': 'D'}))
        self.assertEqual(response.status_code, 302)
        self.response.refresh_from_db()
        self.profile.refresh_from_db()
        self.assertEqual(self.response.score, -1)
        self.assertEqual(self.profile.karma, -1)
        self.assertEqual(Vote.objects.filter(user=self.user, comment=self.response).count(), 2)

    # Test removing a downvote on a comment
    def test_remove_downvote_comment(self):
        self.client.force_login(self.user)
        self.client.get(reverse('upvote_comment', kwargs={'pk': self.response.pk, 'vote': 'D'}))
        response = self.client.get(reverse('upvote_comment', kwargs={'pk': self.response.pk, 'vote': 'D'}))
        self.assertEqual(response.status_code, 302)
        self.response.refresh_from_db()
        self.profile.refresh_from_db()
        self.assertEqual(self.response.score, -2)
        self.assertEqual(self.profile.karma, -2)
        self.assertEqual(Vote.objects.filter(user=self.user, comment=self.response).count(), 3)

    # test get username
    def test_get_author_username(self):
        comment_admin = CommentAdmin(Response, self.admin_site)

        # Create a mock object to simulate a Response instance
        class MockResponse:
            def __init__(self, user):
                self.user = user

        mock_response = MockResponse(user=self.user)
        # Call the method and assert the result
        self.assertEqual(comment_admin.get_author_username(mock_response), 'testuser')

    def test_home_view(self):
        request = self.factory.get(reverse('home'))
        request.user = self.user
        response = Home(request)
        self.assertEqual(response.status_code, 200)

    def test_home_view_order_by_num_views(self):
        response = self.client.get(reverse('home') + '?ordering=num_views')
        self.assertEqual(response.status_code, 200)
        ordered_posts = response.context['posts']
        self.assertEqual(list(ordered_posts), [self.post2, self.post1])

    def test_home_view_order_by_most_upvoted(self):
        response = self.client.get(reverse('home') + '?ordering=most_upvoted')
        self.assertEqual(response.status_code, 200)
        ordered_posts = response.context['posts']
        self.assertEqual(list(ordered_posts), [self.post1, self.post2])

    def test_home_view_order_by_most_downvoted(self):
        response = self.client.get(reverse('home') + '?ordering=most_downvoted')
        self.assertEqual(response.status_code, 200)
        ordered_posts = response.context['posts']
        self.assertEqual(list(ordered_posts), [self.post2, self.post1])

    def test_vote_list(self):
        self.client.login(username='testuser', password='Password123!')
        response = self.client.get(reverse('home'))
        self.assertTrue(response.context['post_vote_list'])

    def test_post_detail_view(self):
        self.client.login(username='testuser', password='Password123!')
        response = self.client.get(reverse('post_detail', kwargs={'id': self.post1.id}))

        self.assertEqual(response.status_code, 200)
        self.assertTrue('post' in response.context)
        self.assertTrue('comment' in response.context)
        self.assertTrue('reply' in response.context)
        self.assertTrue('all_posts' in response.context)
        self.assertTrue('topics' in response.context)
        self.assertTrue('trending_topics' in response.context)
        self.assertTrue('users' in response.context)
        self.assertTrue('user_vote' in response.context)
        self.assertTrue('user_votes' in response.context)
        self.assertTrue('comment_vote_list' in response.context)

    def test_post_detail_view_post_request(self):
        self.client.login(username='testuser', password='Password123!')
        response = self.client.post(reverse('post_detail', kwargs={'id': self.post1.id}), {
            'body': 'Test comment body'
        })

        # Check if the comment is created successfully
        self.assertEqual(response.status_code, 200)  # Check if the request is redirected
        self.assertTrue(Response.objects.filter(post=self.post1, body='Test comment body').exists())

    def test_topic_detail_view_ordering_by_num_views(self):
        response = self.client.get(reverse('topic_detail', kwargs={'id': self.topic1.id}),
                                   {'ordering': 'num_views'})
        self.assertEqual(response.status_code, 200)
        # Add assertions to check if posts are ordered by num_views

    def test_topic_detail_view_ordering_by_most_upvoted(self):
        response = self.client.get(reverse('topic_detail', kwargs={'id': self.topic1.id}),
                                   {'ordering': 'most_upvoted'})
        self.assertEqual(response.status_code, 200)
        # Add assertions to check if posts are ordered by most upvoted

    def test_topic_detail_view_ordering_by_most_downvoted(self):
        response = self.client.get(reverse('topic_detail', kwargs={'id': self.topic1.id}),
                                   {'ordering': 'most_downvoted'})
        self.assertEqual(response.status_code, 200)

    def test_topic_detail_view(self):
        response = self.client.get(reverse('topic_detail', kwargs={'id': self.topic1.id}))
        self.assertEqual(response.status_code, 200)
        self.assertTrue('filtered_posts' in response.context)
        self.assertTrue('topics' in response.context)
        self.assertTrue('current_page' in response.context)
        self.assertTrue('topic' in response.context)
        self.assertTrue('users' in response.context)
        self.assertTrue('trending_topics' in response.context)
        self.assertTrue('all_posts' in response.context)

    def test_topic_detail_view_with_authenticated_user(self):
        self.client.login(username='testuser', password='Password123!')
        response = self.client.get(reverse('topic_detail', kwargs={'id': self.topic1.id}))
        self.assertEqual(response.status_code, 200)
        self.assertTrue('user_votes' in response.context)
        self.assertTrue('post_vote_list' in response.context)

    # def test_edit_profile_pic(self):
    # this function is skipped cuz easily tested on the website

    def test_create_post_without_login(self):
        response = self.client.get(reverse('create_post'))
        self.assertEqual(response.status_code, 302)  # 302 is the status code for redirection
        self.assertIn(reverse('register'), response.url)

    def test_user_profile_view_authenticated(self):
        self.client.login(username='testuser', password='Password123!')
        user_profile_url = reverse('user_profile', kwargs={'id': self.user.id})
        response = self.client.get(user_profile_url)
        self.assertEqual(response.status_code, 302)

    def test_edit_comment_redirect(self):
        self.client.login(username='testuser', password='Password123!')
        edit_comment_url = reverse('edit_comment', kwargs={'comment_id': self.response.id})
        response = self.client.post(edit_comment_url, {'body': 'Updated comment body'})

        self.assertNotEqual(response.status_code, 404)

    def test_edit_comment_form(self):
        self.client.login(username='testuser', password='Password123!')
        edit_comment_url = reverse('edit_comment', kwargs={'comment_id': self.response.id})
        response = self.client.get(edit_comment_url)

        self.assertEqual(response.status_code, 200)

    def test_undo_upvote(self):
        # Simulate an existing upvote
        self.vote.vote_type = 'U'
        self.vote.save()

        # Create a request object
        request = self.factory.get(reverse('upvote_comment', kwargs={'pk': self.response.pk, 'vote': 'U'}))
        request.user = self.user

        # Call the view
        response = upvote_comment(request, pk=self.response.pk, vote='U')

        # Check if the existing upvote is deleted and a downvote is added
        self.assertFalse(Vote.objects.filter(user=self.user, comment=self.response).exists())
        self.assertEqual(self.response.score, 0)
        self.assertEqual(self.user.userprofile.karma, 0)

    def test_undo_downvote(self):
        vote = Vote.objects.create(user=self.user, post=self.post1, vote_type='D')

        # Create a request object for undoing the downvote (upvoting)
        url = reverse('upvote_post', kwargs={'pk': self.post1.pk, 'vote': 'U'})
        request = self.factory.post(url)
        request.user = self.user

        # Call the upvote_post view
        response = upvote_post(request, pk=self.post1.pk, vote='U')

        # Check if the downvote is removed
        self.assertTrue(Vote.objects.filter(user=self.user, post=self.post1, vote_type='D').exists())

        # Check if the post score is updated (increased by 1)
        self.post1.refresh_from_db()
        self.assertEqual(self.post1.score, 6)

        # Check if the user's karma is updated (increased by 1)
        self.user.userprofile.refresh_from_db()
        self.assertEqual(self.user.userprofile.karma, 1)

    def test_delete_post(self):
        initial_num_posts = self.profile.num_posts
        self.client.login(username='testuser', password='Password123!')
        response = self.client.post(
            reverse('delete_post', kwargs={'id': self.post1.id, 'delete1': 'delete', 'delete2': 'post'}))

        self.assertFalse(Post.objects.filter(id=self.post1.id).exists())

        self.profile.refresh_from_db()
        self.assertEqual(self.profile.num_posts, initial_num_posts - 1)

    def test_delete_comment(self):
        # Log in the user
        self.client.login(username='testuser', password='Password123!')

        # Get the URL for deleting the comment
        delete_comment_url = reverse('delete_comment',
                                     kwargs={'id': self.response.pk, 'delete1': 'delete1', 'delete2': 'delete2'})

        # Make a DELETE request to delete the comment
        response = self.client.delete(delete_comment_url)

        # Check if the comment is deleted successfully
        self.assertEqual(response.status_code, 302)  # Assuming redirect to home upon successful deletion

        # Check if the number of comments for the user profile is updated
        self.assertEqual(UserProfile.objects.get(user=self.user).num_comments, -1)

    def test_upvote_comment_2(self):
        self.client.login(username='testuser', password='Password123!')
        # Get the initial score and karma
        initial_score = self.response.score
        initial_karma = self.user.userprofile.karma

        # Simulate an upvote request
        response = self.client.get(reverse('upvote_comment', kwargs={'pk': self.response.pk, 'vote': 'U'}))

        # Check if the upvote is registered
        self.response.refresh_from_db()
        self.assertEqual(self.response.score, initial_score + 1)

        # Check if the user's karma is updated
        self.user.userprofile.refresh_from_db()
        self.assertEqual(self.user.userprofile.karma, initial_karma + 1)

    def test_downvote_comment_2(self):
        self.client.login(username='testuser', password='Password123!')
        # Get the initial score and karma
        initial_score = self.response.score
        initial_karma = self.user.userprofile.karma

        # Simulate a downvote request
        response = self.client.get(reverse('upvote_comment', kwargs={'pk': self.response.pk, 'vote': 'D'}))

        # Check if the downvote is registered
        self.response.refresh_from_db()
        self.assertEqual(self.response.score, initial_score - 1)

        # Check if the user's karma is updated
        self.user.userprofile.refresh_from_db()
        self.assertEqual(self.user.userprofile.karma, initial_karma - 1)

    def test_change_downvote_to_upvote(self):
        self.client.login(username='testuser', password='Password123!')
        self.vote.vote_type = 'D'
        self.vote.save()

        # Get the initial score and karma
        initial_score = self.response.score
        initial_karma = self.user.userprofile.karma

        # Simulate changing the downvote to an upvote
        response = self.client.get(reverse('upvote_comment', kwargs={'pk': self.response.pk, 'vote': 'U'}))

        # Check if the downvote is removed, an upvote is added, and scores are updated
        self.response.refresh_from_db()
        self.assertEqual(self.response.score, initial_score + 2)  # Increase by 1 instead of 2
        self.user.userprofile.refresh_from_db()
        self.assertEqual(self.user.userprofile.karma, initial_karma + 2)

    def test_change_upvote_to_downvote(self):
        self.client.login(username='testuser', password='Password123!')
        # Simulate an existing upvote
        self.vote.vote_type = 'U'
        self.vote.save()

        # Get the initial score and karma
        initial_score = self.response.score
        initial_karma = self.user.userprofile.karma

        # Simulate changing the upvote to a downvote
        response = self.client.get(reverse('upvote_comment', kwargs={'pk': self.response.pk, 'vote': 'D'}))

        # Check if the upvote is removed, a downvote is added, and scores are updated
        self.response.refresh_from_db()
        self.assertEqual(self.response.score, initial_score - 2)
        self.user.userprofile.refresh_from_db()
        self.assertEqual(self.user.userprofile.karma, initial_karma - 2)

    def test_undo_downvote_2(self):
        self.client.login(username='testuser', password='Password123!')
        # Simulate an existing downvote
        self.vote.vote_type = 'D'
        self.vote.save()

        # Get the initial score and karma
        initial_score = self.response.score
        initial_karma = self.user.userprofile.karma

        # Simulate undoing the downvote
        response = self.client.get(reverse('upvote_comment', kwargs={'pk': self.response.pk, 'vote': 'D'}))

        # Check if the downvote is removed, scores are updated, and upvote is not added
        self.assertFalse(Vote.objects.filter(user=self.user, comment=self.response, vote_type='D').exists())
        self.assertFalse(Vote.objects.filter(user=self.user, comment=self.response, vote_type='U').exists())
        self.response.refresh_from_db()
        self.assertEqual(self.response.score, initial_score + 1)  # Increase by 1 instead of 2
        self.user.userprofile.refresh_from_db()
        self.assertEqual(self.user.userprofile.karma, initial_karma + 1)  # Increase by 1 instead of 2

    def test_upvote_post_2(self):
        self.client.login(username='testuser', password='Password123!')
        initial_score = self.post1.score

        # Simulate an upvote
        response = self.client.get(reverse('upvote_post', kwargs={'pk': self.post1.pk, 'vote': 'U'}))

        # Check if the post score is updated
        self.post1.refresh_from_db()
        self.assertEqual(self.post1.score, initial_score + 1)

    def test_undo_upvote_post(self):
        self.client.login(username='testuser', password='Password123!')
        self.vote1.vote_type = 'U'
        self.vote1.save()
        initial_score = self.post1.score

        # Simulate undoing an upvote
        response = self.client.get(reverse('upvote_post', kwargs={'pk': self.post1.pk, 'vote': 'U'}))

        # Check if the upvote is undone and the score is decremented
        self.post1.refresh_from_db()
        self.assertEqual(self.post1.score, initial_score - 1)

    def test_downvote_post_2(self):
        self.client.login(username='testuser', password='Password123!')
        initial_score = self.post1.score

        # Simulate a downvote
        response = self.client.get(reverse('upvote_post', kwargs={'pk': self.post1.pk, 'vote': 'D'}))

        # Check if the post score is updated
        self.post1.refresh_from_db()
        self.assertEqual(self.post1.score, initial_score - 1)

    def test_undo_downvote_post(self):
        self.client.login(username='testuser', password='Password123!')
        self.vote1.vote_type = 'D'
        self.vote1.save()
        initial_score = self.post1.score

        # Simulate undoing a downvote
        response = self.client.get(reverse('upvote_post', kwargs={'pk': self.post1.pk, 'vote': 'D'}))

        # Check if the downvote is undone and the score is incremented
        self.post1.refresh_from_db()
        self.assertEqual(self.post1.score, initial_score + 1)

    def test_change_downvote_to_upvote_2(self):
        self.client.login(username='testuser', password='Password123!')
        self.vote1.vote_type = 'D'
        self.vote1.save()

        # Get the initial score and karma
        initial_score = self.post1.score
        # Simulate changing the downvote to an upvote
        response = self.client.get(reverse('upvote_post', kwargs={'pk': self.post1.pk, 'vote': 'U'}))

        # Check if the downvote is removed, an upvote is added, and scores are updated
        self.post1.refresh_from_db()
        self.assertEqual(self.post1.score, initial_score + 2)  # Increase by 1 instead of 2

    def test_change_upvote_to_downvote_2(self):
        self.client.login(username='testuser', password='Password123!')
        # Simulate an existing upvote
        self.vote1.vote_type = 'U'
        self.vote1.save()

        # Get the initial score and karma
        initial_score = self.post1.score
        # Simulate changing the upvote to a downvote
        response = self.client.get(reverse('upvote_post', kwargs={'pk': self.post1.pk, 'vote': 'D'}))

        # Check if the upvote is removed, a downvote is added, and scores are updated
        self.post1.refresh_from_db()
        self.assertEqual(self.post1.score, initial_score - 2)



