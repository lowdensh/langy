from django.test import TestCase
from language.models import ForeignLanguage, LearningLanguage, TranslatableWord, Translation
from read.models import Author, Book, Page
from tracking.models import LangySession, LearningTrace
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


class LangySessionModelTest(TestCase):
    def test_create_langy_session(self):
        set_up_test_data()
        user = CustomUser.objects.get(email = 'superuser@email.com')
        foreign_language = user.active_language.foreign_language
        session_type = 'READ'
        book = Book.objects.get(title = 'A Nice Book')

        langy_session = LangySession.objects.create(
            user = user,
            foreign_language = foreign_language,
            session_type = session_type,
            book = book)

        self.assertEqual(langy_session.user, user)
        self.assertEqual(langy_session.foreign_language, foreign_language)
        self.assertEqual(langy_session.session_type, session_type)
        self.assertEqual(langy_session.book, book)
        self.assertTrue(langy_session.start_time is not None)
        self.assertTrue(langy_session.end_time is None)


class LearningTraceModelTest(TestCase):
    def test_create_learning_trace(self):
        set_up_test_data()
        user = CustomUser.objects.get(email = 'superuser@email.com')
        langy_session = LangySession.objects.create(
            user = user,
            foreign_language = user.active_language.foreign_language,
            session_type = 'READ',
            book = Book.objects.get(title = 'A Nice Book'))
        translation = Translation.objects.get(translatable_word__english_word = 'nice')
        
        learning_trace = LearningTrace.objects.create(
            user = user,
            session = langy_session,
            translation = translation)

        self.assertEqual(learning_trace.user, user)
        self.assertEqual(learning_trace.session, langy_session)
        self.assertEqual(learning_trace.translation, translation)
        self.assertEqual(learning_trace.prev, None)
        self.assertEqual(learning_trace.seen, 0)
        self.assertEqual(learning_trace.interacted, 0)
        self.assertEqual(learning_trace.tested, 0)
        self.assertEqual(learning_trace.correct, 0)
        self.assertEqual(learning_trace.frn, 'hǎo de')
        self.assertEqual(learning_trace.delta, 0)
        self.assertEqual(learning_trace.p_trans, 0)
        
