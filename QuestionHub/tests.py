from django.test import TestCase
from django.urls import reverse
from .models import Post, Response, Topic, UserProfile, Vote
from django.contrib.auth.models import User

class TestViews(TestCase):
    def setUp(self):
        # Create a test user and profile
        self.user = User.objects.create_user(username='testuser', password='Password123!')
        self.user2 = User.objects.create_user(username='testuser2', password='Password123!')
        self.profile = UserProfile.objects.create(user=self.user)
        self.profile2 = UserProfile.objects.create(user=self.user2)
        # Create test topics
        self.topic1 = Topic.objects.create(name='Topic 1')
        self.topic2 = Topic.objects.create(name='Topic 2')
        # Create test posts
        self.post1 = Post.objects.create(topic = self.topic1, title='Post 1', author=self.user)
        self.post2 = Post.objects.create(topic = self.topic2, title='Post 2', author=self.user)
        # Create test response for post1
        self.response = Response.objects.create(user=self.user, post=self.post1)
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

    #Test post detail page
    def test_post_detail(self):
        response = self.client.get(reverse('post_detail', args=[self.post1.id]))
        self.assertEqual(response.status_code, 200)
        #Check if post 1 and its comments are loaded
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
        response = self.client.post(reverse('register'), {'username': 'testuser1', 'password1': 'Password123!', 'password2': 'Password123!'})
        user_exists = User.objects.filter(username='testuser1').exists()
        #Check if user was created
        self.assertTrue(user_exists)   
        self.assertEqual(response.status_code, 302)
        
    #Test user profile page
    def test_user_profile(self):
        response = self.client.get(reverse('user_profile', kwargs={'id': self.user.id}))
        self.assertEqual(response.status_code, 200)
        #Check if correct user's page loaded
        self.assertEqual(response.context['user'], self.user)

    #Test my profile page
    def test_my_profile(self):
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

    #test sending friend request
    def test_send_friend_request(self):
        #test sending a friend request:
        self.client.force_login(self.user)
        response = self.client.post(reverse('send_friend_request', kwargs={'id': self.user2.id}))
        self.assertEqual(response.status_code, 200)
        updated_profile2 = UserProfile.objects.get(user=self.user2)
        self.assertTrue(updated_profile2.friend_requests.filter(id=self.user.id).exists())

        #test sending friend request simultaneously:
        self.client.force_login(self.user2)
        response = self.client.post(reverse('send_friend_request', kwargs={'id': self.user.id}))
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
        response = self.client.post(reverse('send_friend_request', kwargs={'id': self.user2.id}))

        self.client.force_login(self.user2)
        response = self.client.post(reverse('add_friend', kwargs={'id': self.user.id}))
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
        response = self.client.post(reverse('send_friend_request', kwargs={'id': self.user2.id}))
        response = self.client.post(reverse('reject_friend_request', kwargs={'id': self.user2.id}))
        self.assertEqual(response.status_code, 200)

        updated_profile2 = UserProfile.objects.get(user=self.user2)
        self.assertFalse(updated_profile2.friend_requests.filter(id=self.user.id).exists())


    #reject a friend request that was received
    def test_reject_friend_request(self):
        self.client.force_login(self.user)
        response = self.client.post(reverse('send_friend_request', kwargs={'id': self.user2.id}))
        self.client.force_login(self.user2)
        response = self.client.post(reverse('reject_friend_request', kwargs={'id': self.user.id}))
        self.assertEqual(response.status_code, 200)

        updated_profile2 = UserProfile.objects.get(user=self.user2)
        self.assertFalse(updated_profile2.friend_requests.filter(id=self.user.id).exists())


    #unfriending someone after accepting their friend request
    def test_unfriend(self):
        self.client.force_login(self.user)
        response = self.client.post(reverse('send_friend_request', kwargs={'id': self.user2.id}))

        self.client.force_login(self.user2)
        response = self.client.post(reverse('add_friend', kwargs={'id': self.user.id}))
        self.assertEqual(response.status_code, 200)

        response = self.client.post(reverse('unfriend', kwargs={'id': self.user.id}))
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
        response = self.client.post(reverse('login'), {'username': 'testuser', 'password': 'Password123!'})
        self.assertEqual(response.status_code, 302)  # Redirects to home upon successful login
        self.assertIn('_auth_user_id', self.client.session)
        
    #Test logging out
    def test_logout(self):
        self.client.login(username='testuser', password='Password123!')
        self.assertIn('_auth_user_id', self.client.session)
        response = self.client.get(reverse('logout'))
        self.assertEqual(response.status_code, 302)
        self.assertNotIn('_auth_user_id', self.client.session)
       
    #Test creating a topic 
    def test_create_topic(self):
        self.client.login(username='testuser', password='Password123!')
        response = self.client.post(reverse('create_topic'), {'name': 'Test Topic'})
        self.assertEqual(response.status_code, 302)
        #Check if topic was successfully created
        self.assertTrue(Topic.objects.filter(name='Test Topic').exists()) 

    #Test creating a post
    def test_create_post(self):
        self.client.login(username='testuser', password='Password123!')
        response = self.client.post(reverse('create_post'), {'topic': 1, 'title': 'Test Post', 'body': 'This is a test post body.'})
        self.assertEqual(response.status_code, 302)
        #Check if post was successfully created
        self.assertTrue(Post.objects.filter(title='Test Post').exists())
        self.profile.refresh_from_db()
        #Check if user's number of posts increased
        self.assertEqual(self.profile.num_posts, 1)
    
    #Test replying to a post
    def test_reply(self):    
        self.client.login(username='testuser', password='Password123!')
        response = self.client.post(reverse('reply'), self.response_data)
        self.assertEqual(response.status_code, 302)  
        created_reply = Response.objects.filter(body='Test comment body').first()
        self.assertIsNotNone(created_reply)
        #Check if reply was created
        self.assertEqual(created_reply.user, self.user)
        self.assertEqual(created_reply.post_id, self.response_data['post'])
        self.profile.refresh_from_db()
        #Check if user's number of comments increased
        self.assertEqual(self.profile.num_comments, 1)
     
    #Test upvoting a post
    def test_upvote_post(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse('upvote_post', kwargs={'pk': self.post1.pk, 'vote': 'U'}))
        self.assertEqual(response.status_code, 302)
        self.post1.refresh_from_db()
        self.profile.refresh_from_db()
        #Check if the post's score and user's karma increased by  1
        self.assertEqual(self.post1.score, 1)
        self.assertEqual(self.profile.karma, 1)
        #Check if vote exists
        self.assertEqual(Vote.objects.filter(user=self.user, post=self.post1).count(), 1)

    #Test removing an upvote on a post
    def test_remove_upvote_post(self):
        self.client.force_login(self.user)
        self.client.get(reverse('upvote_post', kwargs={'pk': self.post1.pk, 'vote': 'U'}))
        response = self.client.get(reverse('upvote_post', kwargs={'pk': self.post1.pk, 'vote': 'U'}))
        self.assertEqual(response.status_code, 302)
        self.post1.refresh_from_db()
        self.profile.refresh_from_db()
        self.assertEqual(self.post1.score, 0)
        self.assertEqual(self.profile.karma, 0)
        self.assertEqual(Vote.objects.filter(user=self.user, post=self.post1).count(), 0)

    #Test downvoting a post
    def test_downvote_post(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse('upvote_post', kwargs={'pk': self.post1.pk, 'vote': 'D'}))
        self.assertEqual(response.status_code, 302)
        self.post1.refresh_from_db()
        self.profile.refresh_from_db()
        self.assertEqual(self.post1.score, -1)
        self.assertEqual(self.profile.karma, -1)
        self.assertEqual(Vote.objects.filter(user=self.user, post=self.post1).count(), 1)

    #Test removing a downvote on a post
    def test_remove_downvote_post(self):
        self.client.force_login(self.user)
        self.client.get(reverse('upvote_post', kwargs={'pk': self.post1.pk, 'vote': 'D'}))
        response = self.client.get(reverse('upvote_post', kwargs={'pk': self.post1.pk, 'vote': 'D'}))
        self.assertEqual(response.status_code, 302)
        self.post1.refresh_from_db()
        self.profile.refresh_from_db()
        self.assertEqual(self.post1.score, 0)
        self.assertEqual(self.profile.karma, 0)
        self.assertEqual(Vote.objects.filter(user=self.user, post=self.post1).count(), 0)
        
    #Test upvoting a comment
    def test_upvote_comment(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse('upvote_comment', kwargs={'pk': self.response.pk, 'vote': 'U'}))
        self.assertEqual(response.status_code, 302)
        self.response.refresh_from_db()
        self.profile.refresh_from_db()
        self.assertEqual(self.response.score, 1)
        self.assertEqual(self.profile.karma, 1)
        self.assertEqual(Vote.objects.filter(user=self.user, comment=self.response).count(), 1)

    #Test removing an upvote on a comment
    def test_remove_upvote_comment(self):
        self.client.force_login(self.user)
        self.client.get(reverse('upvote_comment', kwargs={'pk': self.response.pk, 'vote': 'U'}))
        response = self.client.get(reverse('upvote_comment', kwargs={'pk': self.response.pk, 'vote': 'U'}))
        self.assertEqual(response.status_code, 302)
        self.response.refresh_from_db()
        self.profile.refresh_from_db()
        self.assertEqual(self.response.score, 0)
        self.assertEqual(self.profile.karma, 0)
        self.assertEqual(Vote.objects.filter(user=self.user, comment=self.response).count(), 0)

    #Test downvoting a comment
    def test_downvote_comment(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse('upvote_comment', kwargs={'pk': self.response.pk, 'vote': 'D'}))
        self.assertEqual(response.status_code, 302)
        self.response.refresh_from_db()
        self.profile.refresh_from_db()
        self.assertEqual(self.response.score, -1)
        self.assertEqual(self.profile.karma, -1)
        self.assertEqual(Vote.objects.filter(user=self.user, comment=self.response).count(), 1)

    #Test removing a downvote on a comment
    def test_remove_downvote_comment(self):
        self.client.force_login(self.user)
        self.client.get(reverse('upvote_comment', kwargs={'pk': self.response.pk, 'vote': 'D'}))
        response = self.client.get(reverse('upvote_comment', kwargs={'pk': self.response.pk, 'vote': 'D'}))
        self.assertEqual(response.status_code, 302)
        self.response.refresh_from_db()
        self.profile.refresh_from_db()
        self.assertEqual(self.response.score, 0)
        self.assertEqual(self.profile.karma, 0)
        self.assertEqual(Vote.objects.filter(user=self.user, comment=self.response).count(), 0)



