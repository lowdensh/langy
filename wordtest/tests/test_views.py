from django.test import RequestFactory, TestCase
from django.urls import reverse
from django.utils import timezone
from language.models import ForeignLanguage, LearningLanguage, TranslatableWord, Translation
from read.models import Author, Book, Page
from tracking.models import LangySession, LearningTrace
from tracking.views import add_learning_traces
from users.models import CustomUser
import tempfile


def set_up_test_data():
    # User info
    superuser = CustomUser.objects.create_superuser(
        email = 'superuser@email.com',
        display_name = 'Superuser',
        password = 'pass')
    fl_chinese = ForeignLanguage.objects.create(
        key = 'zh-cn',
        english_name = 'Chinese',
        foreign_name = '简体中文',
        note = 'Simplified',
        flag = tempfile.NamedTemporaryFile(suffix='.png').name,
        uses_latin_script = False,
        duolingo_learners = 4760000)
    learning_language = LearningLanguage.objects.create(
        user = CustomUser.objects.get(email='superuser@email.com'),
        foreign_language = ForeignLanguage.objects.get(key='zh-cn'))

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
    translations = []
    for i in range(len(foreign_words)):
        tr = Translation.objects.create(
            translatable_word = translatable_words[i],
            foreign_language = fl_chinese,
            foreign_word = foreign_words[i],
            pronunciation = pronunciations[i])
        translations.append(tr)
    
    # Tracking
    langy_session = LangySession.objects.create(
        user = superuser,
        foreign_language = superuser.active_language.foreign_language,
        session_type = 'READ',
        book = Book.objects.get(title = 'A Nice Book'),
        start_time = timezone.now(),
        end_time = timezone.now())

def create_learning_traces():
    translations = Translation.objects.all()
    user = CustomUser.objects.get(email='superuser@email.com')
    session = LangySession.objects.first()
    for i in range(len(translations)):
        learning_trace = LearningTrace.objects.create(
            user = user,
            session = session,
            translation = translations[i],
            seen = i + 1,
            interacted = i)


class InfoViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        set_up_test_data()
    
    def setUp(self):
        login = self.client.login(email='superuser@email.com', password='pass')

    def test_info_url_path(self):
        response = self.client.get('/word-test/info')
        self.assertEqual(response.status_code, 200)

    def test_info_url_name(self):
        response = self.client.get(reverse('wordtest:info'))
        self.assertEqual(response.status_code, 200)

    def test_info_uses_template(self):
        response = self.client.get(reverse('wordtest:info'))
        self.assertTemplateUsed(response, 'wordtest/info.html')

    def test_info_context(self):
        response = self.client.get(reverse('wordtest:info'))
        self.assertIn('num_words', response.context)
        self.assertIn('error_message', response.context)


class StartTestViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        set_up_test_data()
    
    def setUp(self):
        login = self.client.login(email='superuser@email.com', password='pass')

    def test_start_test_url_path(self):
        response = self.client.get(f'/word-test/start-test')
        self.assertEqual(response.status_code, 302)

    def test_start_test_url_name(self):
        response = self.client.get(reverse('wordtest:start_test'))
        self.assertEqual(response.status_code, 302)
    
    def test_start_test_no_active_language(self):
        user = CustomUser.objects.create_user(
            email='user@email.com',
            display_name='User',
            password='pass')
        login = self.client.login(email='user@email.com', password='pass')
        response = self.client.get(reverse('wordtest:start_test'))
        self.assertRedirects(response, reverse('language:select'))
    
    def test_start_test_not_enough_words(self):
        response = self.client.get(reverse('wordtest:start_test'))
        self.assertRedirects(response, reverse('wordtest:info'))
    
    def test_start_test_session_started(self):
        create_learning_traces()
        initial_session_count = len(LangySession.objects.all())
        response = self.client.get(reverse('wordtest:start_test'))
        new_session_count = len(LangySession.objects.all())
        self.assertTrue(new_session_count > initial_session_count)
