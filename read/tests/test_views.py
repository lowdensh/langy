from django.test import RequestFactory, TestCase
from django.urls import reverse
from language.models import ForeignLanguage, TranslatableWord, Translation
from read.models import Author, Book, Page
from read.views import pages_save, words_save
from tracking.models import LangySession
from users.models import CustomUser
import tempfile


def set_up_test_data():
    # User info
    superuser = CustomUser.objects.create_superuser(
        email='superuser@email.com',
        display_name='Superuser',
        password='pass')
    fl_chinese = ForeignLanguage.objects.create(
        key = 'zh-cn',
        english_name = 'Chinese',
        foreign_name = '简体中文',
        note = 'Simplified',
        flag = tempfile.NamedTemporaryFile(suffix='.png').name,
        uses_latin_script = False,
        duolingo_learners = 4760000)

    # Book info
    author = Author.objects.create(
        forename = 'First',
        surname = 'Last',
        middle_names = 'Middle')
    book = Book.objects.create(
        title = 'A Nice Book',
        author = author,
        source_url = 'url.com',)
    p1 = Page.objects.create(
        book = book,
        number = 1,
        text = 'A nice page about animals! First up, we have dogs. A dog is a friendly animal. My dog was called Ruby. She was a nice dog! Next, we have cats. A cat is a sneaky animal. My cat is called Storm. She is a nice cat, but not as nice as Ruby! Last, we have rabbits. A rabbit is a quiet animal. I think a rabbit would be a nice pet. I have never had a rabbit before.')
    p2 = Page.objects.create(
        book = book,
        number = 2,
        text = 'Now this page is about colours! Our first colour is yellow. The sun is yellow and bright. Cheese is a yellow food. Next is green. Grass is green and lovely. Avocado is a green food. Finally, we have blue. The sky is blue and beautiful. Can you think of any blue food? I can’t!')
    p3 = Page.objects.create(
        book = book,
        number = 2,
        text = 'This is the first sentence on the last page. This is the second sentence on the last page. And this is the very nice, very last sentence!')
    book.pages.add(p1)
    book.pages.add(p2)
    book.pages.add(p3)

    # TranslatableWords
    english_words = ['nice', 'sentence', 'dog', 'cat', 'rabbit', 'yellow', 'green', 'blue']
    translatable_words = []
    for i in range(len(english_words)):
        tw = TranslatableWord.objects.create(english_word=english_words[i])
        tw.books.add(book)
        translatable_words.append(tw)

    # Translations
    foreign_words = ['好的', '句子', '狗', '猫', '兔子', '黄色的', '绿色', '蓝色的']
    pronunciations = ['hǎo de', 'jùzi', 'gǒu', 'māo', 'tùzǐ', 'huángsè de', 'lǜsè', 'lán sè de']
    for i in range(len(foreign_words)):
        tr = Translation.objects.create(
            translatable_word = translatable_words[i],
            foreign_language = fl_chinese,
            foreign_word = foreign_words[i],
            pronunciation = pronunciations[i])


class BooksViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        superuser = CustomUser.objects.create_superuser(
            email='superuser@email.com',
            display_name='Superuser',
            password='pass')
    
    def setUp(self):
        login = self.client.login(email='superuser@email.com', password='pass')

    def test_books_url_path(self):
        response = self.client.get('/read/books')
        self.assertEqual(response.status_code, 200)

    def test_books_url_name(self):
        response = self.client.get(reverse('read:books'))
        self.assertEqual(response.status_code, 200)

    def test_books_uses_template(self):
        response = self.client.get(reverse('read:books'))
        self.assertTemplateUsed(response, 'read/books.html')

    def test_books_context(self):
        response = self.client.get(reverse('read:books'))
        self.assertIn('books_readable', response.context)
        self.assertIn('books_unreadable', response.context)
    

class DetailsViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        set_up_test_data()
        user = CustomUser.objects.create_user(
            email='user@email.com',
            display_name='User',
            password='pass')

    def test_details_url_path(self):
        login = self.client.login(email='superuser@email.com', password='pass')
        set_active_language = self.client.get(reverse('language:set_active_language', args=('Chinese',)))
        book_id = Book.objects.get(title='A Nice Book').id
        response = self.client.get(f'/read/{book_id}/details')
        self.assertEqual(response.status_code, 200)

    def test_details_url_name(self):
        login = self.client.login(email='superuser@email.com', password='pass')
        set_active_language = self.client.get(reverse('language:set_active_language', args=('Chinese',)))
        book_id = Book.objects.get(title='A Nice Book').id
        response = self.client.get(reverse('read:details', args=(book_id,)))
        self.assertEqual(response.status_code, 200)

    def test_details_book_id_invalid(self):
        login = self.client.login(email='superuser@email.com', password='pass')
        set_active_language = self.client.get(reverse('language:set_active_language', args=('Chinese',)))
        book_id = 999999
        response = self.client.get(reverse('read:details', args=(book_id,)))
        self.assertEqual(response.status_code, 404)

    def test_details_no_active_language(self):
        login = self.client.login(email='user@email.com', password='pass')
        book_id = Book.objects.get(title='A Nice Book').id
        response = self.client.get(reverse('read:details', args=(book_id,)))
        self.assertRedirects(response, reverse('language:select'))

    def test_details_uses_template(self):
        login = self.client.login(email='superuser@email.com', password='pass')
        set_active_language = self.client.get(reverse('language:set_active_language', args=('Chinese',)))
        book_id = Book.objects.get(title='A Nice Book').id
        response = self.client.get(reverse('read:details', args=(book_id,)))
        self.assertTemplateUsed(response, 'read/details.html')

    def test_details_context(self):
        login = self.client.login(email='superuser@email.com', password='pass')
        set_active_language = self.client.get(reverse('language:set_active_language', args=('Chinese',)))
        book_id = Book.objects.get(title='A Nice Book').id
        response = self.client.get(reverse('read:details', args=(book_id,)))
        self.assertIn('book', response.context)
        self.assertIn('words_to_learn', response.context)
        self.assertIn('difficulty', response.context)
    

class PagesManageViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        set_up_test_data()
        user = CustomUser.objects.create_user(
            email='user@email.com',
            display_name='User',
            password='pass')

    def test_pages_manage_url_path(self):
        login = self.client.login(email='superuser@email.com', password='pass')
        book_id = Book.objects.get(title='A Nice Book').id
        response = self.client.get(f'/read/{book_id}/pages/manage')
        self.assertEqual(response.status_code, 200)

    def test_pages_manage_url_name(self):
        login = self.client.login(email='superuser@email.com', password='pass')
        book_id = Book.objects.get(title='A Nice Book').id
        response = self.client.get(reverse('read:pages_manage', args=(book_id,)))
        self.assertEqual(response.status_code, 200)

    def test_pages_manage_book_id_invalid(self):
        login = self.client.login(email='superuser@email.com', password='pass')
        book_id = 999999
        response = self.client.get(reverse('read:pages_manage', args=(book_id,)))
        self.assertEqual(response.status_code, 404)

    def test_pages_manage_uses_template(self):
        login = self.client.login(email='superuser@email.com', password='pass')
        book_id = Book.objects.get(title='A Nice Book').id
        response = self.client.get(reverse('read:pages_manage', args=(book_id,)))
        self.assertTemplateUsed(response, 'read/pages-manage.html')

    def test_pages_manage_context(self):
        login = self.client.login(email='superuser@email.com', password='pass')
        book_id = Book.objects.get(title='A Nice Book').id
        response = self.client.get(reverse('read:pages_manage', args=(book_id,)))
        self.assertIn('book', response.context)
    
    def test_pages_manage_not_staff_member(self):
        login = self.client.login(email='user@email.com', password='pass')
        book_id = Book.objects.get(title='A Nice Book').id
        response = self.client.get(reverse('read:pages_manage', args=(book_id,)))
        self.assertRedirects(response, f'/admin/login/?next=/read/{book_id}/pages/manage')
    

class PagesGenerateViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        set_up_test_data()
        user = CustomUser.objects.create_user(
            email='user@email.com',
            display_name='User',
            password='pass')

    def test_pages_generate_url_path(self):
        login = self.client.login(email='superuser@email.com', password='pass')
        book_id = Book.objects.get(title='A Nice Book').id
        response = self.client.get(f'/read/{book_id}/pages/generate')
        self.assertEqual(response.status_code, 200)

    def test_pages_generate_url_name(self):
        login = self.client.login(email='superuser@email.com', password='pass')
        book_id = Book.objects.get(title='A Nice Book').id
        response = self.client.get(reverse('read:pages_generate', args=(book_id,)))
        self.assertEqual(response.status_code, 200)

    def test_pages_generate_book_id_invalid(self):
        login = self.client.login(email='superuser@email.com', password='pass')
        book_id = 999999
        response = self.client.get(reverse('read:pages_generate', args=(book_id,)))
        self.assertEqual(response.status_code, 404)

    def test_pages_generate_uses_template(self):
        login = self.client.login(email='superuser@email.com', password='pass')
        book_id = Book.objects.get(title='A Nice Book').id
        response = self.client.get(reverse('read:pages_generate', args=(book_id,)))
        self.assertTemplateUsed(response, 'read/pages-generate.html')

    def test_pages_generate_context(self):
        login = self.client.login(email='superuser@email.com', password='pass')
        book_id = Book.objects.get(title='A Nice Book').id
        response = self.client.get(reverse('read:pages_generate', args=(book_id,)))
        self.assertIn('book', response.context)
        self.assertIn('text_content', response.context)
    
    def test_pages_generate_not_staff_member(self):
        login = self.client.login(email='user@email.com', password='pass')
        book_id = Book.objects.get(title='A Nice Book').id
        response = self.client.get(reverse('read:pages_generate', args=(book_id,)))
        self.assertRedirects(response, f'/admin/login/?next=/read/{book_id}/pages/generate')
    

class PagesSaveViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        set_up_test_data()
        user = CustomUser.objects.create_user(
            email='user@email.com',
            display_name='User',
            password='pass')
    
    def test_pages_save_not_staff_member(self):
        login = self.client.login(email='user@email.com', password='pass')
        book_id = Book.objects.get(title='A Nice Book').id
        response = self.client.get(reverse('read:pages_save', args=(book_id,)))
        self.assertRedirects(response, f'/admin/login/?next=/read/{book_id}/pages/save')

    def test_pages_save(self):
        login = self.client.login(email='superuser@email.com', password='pass')
        book = Book.objects.get(title='A Nice Book')

        # JSON data. stringify and loads in template and view
        request = RequestFactory().post(reverse(
            'read:pages_save',
            args=(book.id,)))
        request.user = CustomUser.objects.get(email='superuser@email.com')
        request._body = b'{"text_content": ["first page", "second page"]}'
        response = pages_save(request, book.id)

        self.assertEqual(book.pages.count(), 2)
    

class WordsManageViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        set_up_test_data()
        user = CustomUser.objects.create_user(
            email='user@email.com',
            display_name='User',
            password='pass')

    def test_words_manage_url_path(self):
        login = self.client.login(email='superuser@email.com', password='pass')
        book_id = Book.objects.get(title='A Nice Book').id
        response = self.client.get(f'/read/{book_id}/words/manage')
        self.assertEqual(response.status_code, 200)

    def test_words_manage_url_name(self):
        login = self.client.login(email='superuser@email.com', password='pass')
        book_id = Book.objects.get(title='A Nice Book').id
        response = self.client.get(reverse('read:words_manage', args=(book_id,)))
        self.assertEqual(response.status_code, 200)

    def test_words_manage_book_id_invalid(self):
        login = self.client.login(email='superuser@email.com', password='pass')
        book_id = 999999
        response = self.client.get(reverse('read:words_manage', args=(book_id,)))
        self.assertEqual(response.status_code, 404)

    def test_words_manage_uses_template(self):
        login = self.client.login(email='superuser@email.com', password='pass')
        book_id = Book.objects.get(title='A Nice Book').id
        response = self.client.get(reverse('read:words_manage', args=(book_id,)))
        self.assertTemplateUsed(response, 'read/words-manage.html')

    def test_words_manage_context(self):
        login = self.client.login(email='superuser@email.com', password='pass')
        book_id = Book.objects.get(title='A Nice Book').id
        response = self.client.get(reverse('read:words_manage', args=(book_id,)))
        self.assertIn('book', response.context)
    
    def test_words_manage_not_staff_member(self):
        login = self.client.login(email='user@email.com', password='pass')
        book_id = Book.objects.get(title='A Nice Book').id
        response = self.client.get(reverse('read:words_manage', args=(book_id,)))
        self.assertRedirects(response, f'/admin/login/?next=/read/{book_id}/words/manage')
    

class WordsGenerateViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        set_up_test_data()
        user = CustomUser.objects.create_user(
            email='user@email.com',
            display_name='User',
            password='pass')

    def test_words_generate_url_path(self):
        login = self.client.login(email='superuser@email.com', password='pass')
        book_id = Book.objects.get(title='A Nice Book').id
        response = self.client.get(f'/read/{book_id}/words/generate')
        self.assertEqual(response.status_code, 200)

    def test_words_generate_url_name(self):
        login = self.client.login(email='superuser@email.com', password='pass')
        book_id = Book.objects.get(title='A Nice Book').id
        response = self.client.get(reverse('read:words_generate', args=(book_id,)))
        self.assertEqual(response.status_code, 200)

    def test_words_generate_book_id_invalid(self):
        login = self.client.login(email='superuser@email.com', password='pass')
        book_id = 999999
        response = self.client.get(reverse('read:words_generate', args=(book_id,)))
        self.assertEqual(response.status_code, 404)

    def test_words_generate_book_no_pages(self):
        login = self.client.login(email='superuser@email.com', password='pass')
        book = Book.objects.create(
            title = 'An Empty Book',
            author = Author.objects.get(forename = 'First'),
            source_url = 'url.com',)
        response = self.client.get(reverse('read:words_generate', args=(book.id,)))
        self.assertRedirects(response, reverse('read:words_manage', args=(book.id,)))

    def test_words_generate_uses_template(self):
        login = self.client.login(email='superuser@email.com', password='pass')
        book_id = Book.objects.get(title='A Nice Book').id
        response = self.client.get(reverse('read:words_generate', args=(book_id,)))
        self.assertTemplateUsed(response, 'read/words-generate.html')

    def test_words_generate_context(self):
        login = self.client.login(email='superuser@email.com', password='pass')
        book_id = Book.objects.get(title='A Nice Book').id
        response = self.client.get(reverse('read:words_generate', args=(book_id,)))
        self.assertIn('book', response.context)
        self.assertIn('unique_word_count', response.context)
        self.assertIn('minimum_frequency', response.context)
        self.assertIn('common_words', response.context)
    
    def test_words_generate_not_staff_member(self):
        login = self.client.login(email='user@email.com', password='pass')
        book_id = Book.objects.get(title='A Nice Book').id
        response = self.client.get(reverse('read:words_generate', args=(book_id,)))
        self.assertRedirects(response, f'/admin/login/?next=/read/{book_id}/words/generate')
    

class WordsSaveViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        set_up_test_data()
        user = CustomUser.objects.create_user(
            email='user@email.com',
            display_name='User',
            password='pass')
    
    def test_words_save_not_staff_member(self):
        login = self.client.login(email='user@email.com', password='pass')
        book_id = Book.objects.get(title='A Nice Book').id
        response = self.client.get(reverse('read:words_save', args=(book_id,)))
        self.assertRedirects(response, f'/admin/login/?next=/read/{book_id}/words/save')

    def test_words_save(self):
        login = self.client.login(email='superuser@email.com', password='pass')
        book = Book.objects.get(title='A Nice Book')
        initial_tw_count = len(TranslatableWord.objects.all())

        # JSON data. stringify and loads in template and view
        request = RequestFactory().post(reverse(
            'read:words_save',
            args=(book.id,)))
        request.user = CustomUser.objects.get(email='superuser@email.com')
        request._body = b'{"words": ["rainbows", "butterflies"]}'
        response = words_save(request, book.id)
        new_tw_count = len(TranslatableWord.objects.all())

        self.assertTrue(new_tw_count > initial_tw_count)


class StartReadViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        set_up_test_data()
    
    def setUp(self):
        login = self.client.login(email='superuser@email.com', password='pass')
        set_active_language = self.client.get(reverse('language:set_active_language', args=('Chinese',)))

    def test_start_read_url_path(self):
        book_id = Book.objects.get(title='A Nice Book').id
        response = self.client.get(f'/read/{book_id}/start-read')
        self.assertEqual(response.status_code, 302)

    def test_start_read_url_name(self):
        book_id = Book.objects.get(title='A Nice Book').id
        response = self.client.get(reverse('read:start_read', args=(book_id,)))
        self.assertEqual(response.status_code, 302)

    def test_start_read_book_no_pages(self):
        book = Book.objects.create(
            title = 'An Empty Book',
            author = Author.objects.get(forename = 'First'),
            source_url = 'url.com',)
        response = self.client.get(reverse('read:start_read', args=(book.id,)))
        self.assertRedirects(response, reverse('read:details', args=(book.id,)))

    def test_start_read_book_id_invalid(self):
        book_id = 999999
        response = self.client.get(reverse('read:start_read', args=(book_id,)))
        self.assertEqual(response.status_code, 404)
    
    def test_start_read_no_active_language(self):
        user = CustomUser.objects.create_user(
            email='user@email.com',
            display_name='User',
            password='pass')
        login = self.client.login(email='user@email.com', password='pass')
        book_id = Book.objects.get(title='A Nice Book').id
        response = self.client.get(reverse('read:start_read', args=(book_id,)))
        self.assertRedirects(response, reverse('language:select'))
    
    def test_start_read_session_started(self):
        book_id = Book.objects.get(title='A Nice Book').id
        initial_session_count = len(LangySession.objects.all())
        response = self.client.get(reverse('read:start_read', args=(book_id,)))
        new_session_count = len(LangySession.objects.all())
        self.assertTrue(new_session_count > initial_session_count)



    


