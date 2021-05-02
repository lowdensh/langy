from django.test import RequestFactory, TestCase
from django.urls import reverse
from language.models import ForeignLanguage, TranslatableWord, Translation
from language.views import translate_english_words, save_translations
from read.models import Author, Book
from users.models import CustomUser
import tempfile


class SelectViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        superuser = CustomUser.objects.create_superuser(
            email='superuser@email.com',
            display_name='Superuser',
            password='pass')
    
    def setUp(self):
        login = self.client.login(email='superuser@email.com', password='pass')

    def test_select_url_path(self):
        response = self.client.get('/language/select')
        self.assertEqual(response.status_code, 200)

    def test_select_url_name(self):
        response = self.client.get(reverse('language:select'))
        self.assertEqual(response.status_code, 200)

    def test_select_uses_template(self):
        response = self.client.get(reverse('language:select'))
        self.assertTemplateUsed(response, 'language/select.html')

    def test_select_context(self):
        response = self.client.get(reverse('language:select'))
        self.assertIn('foreign_languages', response.context)
        self.assertIn('active_language', response.context)


class SetActiveLanguageViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        superuser = CustomUser.objects.create_superuser(
            email='superuser@email.com',
            display_name='Superuser',
            password='pass')
        fl_swedish = ForeignLanguage.objects.create(
            key = 'sv',
            english_name = 'Swedish',
            foreign_name = 'Svenska',
            flag = tempfile.NamedTemporaryFile(suffix='.png').name,
            uses_latin_script = True,
            duolingo_learners = 1260000)
    
    def setUp(self):
        login = self.client.login(email='superuser@email.com', password='pass')
    
    def test_set_active_language(self):
        english_name = 'Swedish'
        user = CustomUser.objects.get(email='superuser@email.com')
        set_active_language = self.client.get(reverse('language:set_active_language', args=(english_name,)))
        self.assertEquals(user.active_language.foreign_language.key, 'sv')


class DeleteLearningLanguageViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        superuser = CustomUser.objects.create_superuser(
            email='superuser@email.com',
            display_name='Superuser',
            password='pass')
        fl_swedish = ForeignLanguage.objects.create(
            key = 'sv',
            english_name = 'Swedish',
            foreign_name = 'Svenska',
            flag = tempfile.NamedTemporaryFile(suffix='.png').name,
            uses_latin_script = True,
            duolingo_learners = 1260000)
        fl_chinese = ForeignLanguage.objects.create(
            key = 'zh-cn',
            english_name = 'Chinese',
            foreign_name = '简体中文',
            note = 'Simplified',
            flag = tempfile.NamedTemporaryFile(suffix='.png').name,
            uses_latin_script = False,
            duolingo_learners = 4760000)
    
    def setUp(self):
        login = self.client.login(email='superuser@email.com', password='pass')
    
    def test_delete_learning_language(self):
        fl1 = 'Swedish'
        fl2 = 'Chinese'
        user = CustomUser.objects.get(email='superuser@email.com')
        set_active_language = self.client.get(reverse('language:set_active_language', args=(fl1,)))
        set_active_language = self.client.get(reverse('language:set_active_language', args=(fl2,)))
        delete_learning_language = self.client.get(reverse('language:delete_learning_language', args=(fl2,)))
        self.assertEquals(user.active_language.foreign_language.key, 'sv')


class TranslationPageViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        user = CustomUser.objects.create_user(
            email='user@email.com',
            display_name='User',
            password='pass')
        superuser = CustomUser.objects.create_superuser(
            email='superuser@email.com',
            display_name='Superuser',
            password='pass')

    def test_translation_page_url_path(self):
        login = self.client.login(email='superuser@email.com', password='pass')
        response = self.client.get('/language/translate')
        self.assertEqual(response.status_code, 200)

    def test_translation_page_url_name(self):
        login = self.client.login(email='superuser@email.com', password='pass')
        response = self.client.get(reverse('language:translation_page'))
        self.assertEqual(response.status_code, 200)

    def test_translation_page_uses_template(self):
        login = self.client.login(email='superuser@email.com', password='pass')
        response = self.client.get(reverse('language:translation_page'))
        self.assertTemplateUsed(response, 'language/translate.html')

    def test_translation_page_context(self):
        login = self.client.login(email='superuser@email.com', password='pass')
        response = self.client.get(reverse('language:translation_page'))
        self.assertIn('foreign_languages', response.context)
        self.assertIn('translatable_words', response.context)
    
    def test_translation_page_not_staff_member(self):
        login = self.client.login(email='user@email.com', password='pass')
        response = self.client.get(reverse('language:translation_page'))
        self.assertRedirects(response, '/admin/login/?next=/language/translate')


class TranslationPageBookViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        user = CustomUser.objects.create_user(
            email='user@email.com',
            display_name='User',
            password='pass')
        superuser = CustomUser.objects.create_superuser(
            email='superuser@email.com',
            display_name='Superuser',
            password='pass')
        author = Author.objects.create(
            forename = 'First',
            surname = 'Last')
        book = Book.objects.create(
            title = 'Book Title',
            author = author,
            source_url = 'url.com',
            summary = 'Some kind of description',
            cover = tempfile.NamedTemporaryFile(suffix='.jpg').name,
            pdf = tempfile.NamedTemporaryFile(suffix='.pdf').name)

    def test_translation_page_book_url_path(self):
        login = self.client.login(email='superuser@email.com', password='pass')
        book_id = Book.objects.get(title='Book Title').id
        response = self.client.get(f'/language/translate/{book_id}')
        self.assertEqual(response.status_code, 200)

    def test_translation_page_book_url_name(self):
        login = self.client.login(email='superuser@email.com', password='pass')
        book_id = Book.objects.get(title='Book Title').id
        response = self.client.get(reverse('language:translation_page_book', args=(book_id,)))
        self.assertEqual(response.status_code, 200)

    def test_translation_page_book_uses_template(self):
        login = self.client.login(email='superuser@email.com', password='pass')
        book_id = Book.objects.get(title='Book Title').id
        response = self.client.get(reverse('language:translation_page_book', args=(book_id,)))
        self.assertTemplateUsed(response, 'language/translate.html')

    def test_translation_page_book_context(self):
        login = self.client.login(email='superuser@email.com', password='pass')
        book_id = Book.objects.get(title='Book Title').id
        response = self.client.get(reverse('language:translation_page_book', args=(book_id,)))
        self.assertIn('foreign_languages', response.context)
        self.assertIn('translatable_words', response.context)
    
    def test_translation_page_book_not_staff_member(self):
        login = self.client.login(email='user@email.com', password='pass')
        book_id = Book.objects.get(title='Book Title').id
        response = self.client.get(reverse('language:translation_page_book', args=(book_id,)))
        self.assertRedirects(response, f'/admin/login/?next=/language/translate/{book_id}')


class TranslateEnglishWordsView(TestCase):
    @classmethod
    def setUpTestData(cls):
        user = CustomUser.objects.create_user(
            email='user@email.com',
            display_name='User',
            password='pass')
        superuser = CustomUser.objects.create_superuser(
            email='superuser@email.com',
            display_name='Superuser',
            password='pass')
        fl_swedish = ForeignLanguage.objects.create(
            key = 'sv',
            english_name = 'Swedish',
            foreign_name = 'Svenska',
            flag = tempfile.NamedTemporaryFile(suffix='.png').name,
            uses_latin_script = True,
            duolingo_learners = 1260000)
    
    def test_translation_page_not_staff_member(self):
        login = self.client.login(email='user@email.com', password='pass')
        key = 'sv'
        response = self.client.get(reverse('language:translate_english_words', kwargs={'key':key}))
        self.assertRedirects(response, f'/admin/login/?next=/language/translate-english-words/{key}')

    def test_translate_english_words(self):
        login = self.client.login(email='superuser@email.com', password='pass')
        key = 'sv'

        # JSON data. stringify and loads in template and view
        request = RequestFactory().post(reverse(
            'language:translate_english_words',
            kwargs={'key':key}))
        request.user = CustomUser.objects.get(email='superuser@email.com')
        request._body = b'{"english_words": ["dog"]}'

        response = translate_english_words(request, key)
        response_content = response.content.decode('utf-8')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response_content, '{"foreign_words": ["hund"], "pronunciations": [null], "enable_pronunciations": false}')


class SaveTranslationsView(TestCase):
    @classmethod
    def setUpTestData(cls):
        user = CustomUser.objects.create_user(
            email='user@email.com',
            display_name='User',
            password='pass')
        superuser = CustomUser.objects.create_superuser(
            email='superuser@email.com',
            display_name='Superuser',
            password='pass')
        fl_swedish = ForeignLanguage.objects.create(
            key = 'sv',
            english_name = 'Swedish',
            foreign_name = 'Svenska',
            flag = tempfile.NamedTemporaryFile(suffix='.png').name,
            uses_latin_script = True,
            duolingo_learners = 1260000)
    
    def test_save_translations_not_staff_member(self):
        login = self.client.login(email='user@email.com', password='pass')
        key = 'sv'
        response = self.client.get(reverse('language:save_translations', kwargs={'key':key}))
        self.assertRedirects(response, f'/admin/login/?next=/language/save-translations/{key}')

    def test_save_translations(self):
        login = self.client.login(email='superuser@email.com', password='pass')
        key = 'sv'
        twid = TranslatableWord.objects.create(english_word='dog').id

        # JSON data. stringify and loads in template and view
        request = RequestFactory().post(reverse(
            'language:save_translations',
            kwargs={'key':key}))
        request.user = CustomUser.objects.get(email='superuser@email.com')
        body_string = '{"translations":[{"translatable_word_id":0,"foreign_word":"hund","pronunciation":"hund"}]}'.replace("0", str(twid))
        request._body = str.encode(body_string)

        response = save_translations(request, key)
        translation = Translation.objects.filter(foreign_word='hund').first()

        self.assertTrue(translation.foreign_word, 'hund')
        self.assertTrue(translation.foreign_language.key, key)

