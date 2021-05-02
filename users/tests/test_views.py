from django.test import TestCase, SimpleTestCase
from django.urls import reverse
from users.models import CustomUser


class SignUpViewTest(SimpleTestCase):
    def test_url_path(self):
        response = self.client.get('/users/sign-up')
        self.assertEqual(response.status_code, 200)

    def test_url_name(self):
        response = self.client.get(reverse('users:sign_up'))
        self.assertEqual(response.status_code, 200)

    def test_uses_template(self):
        response = self.client.get(reverse('users:sign_up'))
        self.assertTemplateUsed(response, 'users/sign-up.html')

    def test_in_context(self):
        response = self.client.get(reverse('users:sign_up'))
        self.assertIn('form', response.context)


class LoginTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        superuser = CustomUser.objects.create_superuser(
            email='superuser@email.com',
            display_name='Superuser',
            password='pass')
        superuser.save()

    def test_redirect_if_not_logged_in(self):
        response = self.client.get(reverse('read:books'))
        self.assertRedirects(response, '/accounts/login/?next=/read/books')
    
    def test_login(self):
        login = self.client.login(email='superuser@email.com', password='pass')
        response = self.client.get(reverse('read:books'))
        self.assertEqual(str(response.context['user']), 'superuser@email.com')


class ProfileViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        superuser = CustomUser.objects.create_superuser(
            email='superuser@email.com',
            display_name='Superuser',
            password='pass')
        superuser.save()
    
    def setUp(self):
        login = self.client.login(email='superuser@email.com', password='pass')

    def test_url_path_user_id_missing(self):
        response = self.client.get('/users/profile')
        self.assertEqual(response.status_code, 404)
    
    def test_url_path(self):
        uid = CustomUser.objects.get(email='superuser@email.com').id
        response = self.client.get(f'/users/profile/{uid}')
        self.assertEqual(response.status_code, 200)

    def test_url_name(self):
        uid = CustomUser.objects.get(email='superuser@email.com').id
        response = self.client.get(reverse('users:profile', args=(uid,)))
        self.assertEqual(response.status_code, 200)

    def test_uses_template(self):
        uid = CustomUser.objects.get(email='superuser@email.com').id
        response = self.client.get(reverse('users:profile', args=(uid,)))
        self.assertTemplateUsed(response, 'users/profile.html')

    def test_in_context(self):
        uid = CustomUser.objects.get(email='superuser@email.com').id
        response = self.client.get(reverse('users:profile', args=(uid,)))
        self.assertIn('profile_user', response.context)
        self.assertIn('learning_languages', response.context)
        self.assertIn('active_language', response.context)

