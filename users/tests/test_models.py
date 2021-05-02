from django.test import TestCase
from users.models import CustomUser


class CustomUserModelTest(TestCase):
    def test_create_customuser(self):
        user = CustomUser.objects.create_user(
            email='newuser@email.com',
            display_name='New User',
            password='pass')
        self.assertEqual(user.email, 'newuser@email.com')
        self.assertEqual(user.display_name, 'New User')
        self.assertTrue(user.is_active)
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)
    
    def test_create_superuser(self):
        superuser = CustomUser.objects.create_superuser(
            email='newsuperuser@email.com',
            display_name='New Superuser',
            password='pass')
        self.assertEqual(superuser.email, 'newsuperuser@email.com')
        self.assertEqual(superuser.display_name, 'New Superuser')
        self.assertTrue(superuser.is_active)
        self.assertTrue(superuser.is_staff)
        self.assertTrue(superuser.is_superuser)
    
    def test_display_name_max_length(self):
        user = CustomUser.objects.create_user(
            email='maxlength@email.com',
            display_name='Display Name',
            password='pass')
        max_length = user._meta.get_field('display_name').max_length
        self.assertEqual(max_length, 20)
