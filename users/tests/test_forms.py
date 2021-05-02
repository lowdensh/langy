from django.test import TestCase
from users.forms import CustomUserCreationForm


class CustomUserCreationFormTest(TestCase):
    def test_creation_form_email_label(self):
        form = CustomUserCreationForm()
        self.assertTrue(form.fields['email'].label is None or form.fields['email'].label == 'email')

    def test_creation_form_display_name_label(self):
        form = CustomUserCreationForm()
        self.assertTrue(form.fields['display_name'].label is None or form.fields['display_name'].label == 'display_name')

    def test_creation_form_display_name_help_text(self):
        form = CustomUserCreationForm()
        self.assertEqual(form.fields['display_name'].help_text, 'A publicly displayed name. Does not need to be unique.')

    def test_creation_form_email_invalid(self):
        email = 'no at symbol'
        display_name = 'Display Name'
        password = 'qp10wo29ei38ru47ty56.'
        form = CustomUserCreationForm(data={
            'email': email,
            'display_name': display_name,
            'password1': password,
            'password2': password,
        })
        self.assertFalse(form.is_valid())

    def test_creation_form_display_name_too_long(self):
        email = 'creationform@email.com'
        display_name = 'Display Name Over 20 Characters'
        password = 'qp10wo29ei38ru47ty56.'
        form = CustomUserCreationForm(data={
            'email': email,
            'display_name': display_name,
            'password1': password,
            'password2': password,
        })
        self.assertFalse(form.is_valid())

    def test_creation_form_data_empty(self):
        form = CustomUserCreationForm(data={})
        self.assertFalse(form.is_valid())

    def test_creation_form_data_valid(self):
        email = 'creationform@email.com'
        display_name = 'Display Name'
        password = 'qp10wo29ei38ru47ty56.'
        form = CustomUserCreationForm(data={
            'email': email,
            'display_name': display_name,
            'password1': password,
            'password2': password,
        })
        self.assertTrue(form.is_valid())
