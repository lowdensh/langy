from django.test import RequestFactory, TestCase
from django.urls import reverse
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
    for i in range(len(foreign_words)):
        tr = Translation.objects.create(
            translatable_word = translatable_words[i],
            foreign_language = fl_chinese,
            foreign_word = foreign_words[i],
            pronunciation = pronunciations[i])


class AddLearningTracesViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        set_up_test_data()
    
    def setUp(self):
        login = self.client.login(email='superuser@email.com', password='pass')
    
    def do_request(self, sid, t1id, t2id):
        # JSON data. stringify and loads in template and view
        request = RequestFactory().post(reverse('tracking:add_learning_traces'))
        request.user = CustomUser.objects.get(email='superuser@email.com')
        body_string = (
            '{"langy_session_id":A, "translation_ids":[B, C], "mode": "seen"}'
            ).replace("A", str(sid)).replace("B", str(t1id)).replace("C", str(t2id))
        request._body = str.encode(body_string)
        response = add_learning_traces(request)
        return response

    def test_add_learning_traces(self):
        user = CustomUser.objects.get(email = 'superuser@email.com')
        langy_session = LangySession.objects.create(
            user = user,
            foreign_language = user.active_language.foreign_language,
            session_type = 'READ',
            book = Book.objects.get(title = 'A Nice Book'))
        t1 = Translation.objects.get(translatable_word__english_word = 'dog')
        t2 = Translation.objects.get(translatable_word__english_word = 'cat')
        response = self.do_request(langy_session.id, t1.id, t2.id)
        self.assertEquals(len(LearningTrace.objects.all()), 2)
        self.assertTrue(LearningTrace.objects.filter(
            translation__translatable_word__english_word='dog').first()
            is not None)
        self.assertTrue(LearningTrace.objects.filter(
            translation__translatable_word__english_word='cat').first()
            is not None)

    def test_add_learning_traces_invalid_translation_id(self):
        user = CustomUser.objects.get(email = 'superuser@email.com')
        langy_session = LangySession.objects.create(
            user = user,
            foreign_language = user.active_language.foreign_language,
            session_type = 'READ',
            book = Book.objects.get(title = 'A Nice Book'))
        response = self.do_request(langy_session.id, 9999, 8888)
        self.assertEquals(len(LearningTrace.objects.all()), 0)