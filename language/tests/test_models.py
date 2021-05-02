from django.test import TestCase
from language.models import ForeignLanguage, LearningLanguage, Synonym, TranslatableWord, Translation
from read.models import Author, Book
from users.models import CustomUser
import tempfile


class ForeignLanguageModelTest(TestCase):
    def test_create_foreign_language(self):
        foreign_language = ForeignLanguage.objects.create(
            key = 'fl-cr',
            english_name = 'English name',
            foreign_name = 'Foreign name',
            note = 'Variant',
            flag = tempfile.NamedTemporaryFile(suffix='.png').name,
            uses_latin_script = True,
            duolingo_learners = 1)
        self.assertEqual(foreign_language.key, 'fl-cr')
        self.assertEqual(foreign_language.english_name, 'English name')
        self.assertEqual(foreign_language.foreign_name, 'Foreign name')
        self.assertEqual(foreign_language.note, 'Variant')
        self.assertTrue(foreign_language.flag.name is not None)
        self.assertTrue(foreign_language.uses_latin_script)
        self.assertEqual(foreign_language.duolingo_learners, 1)


class LearningLanguageModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        superuser = CustomUser.objects.create_superuser(
            email='superuser@email.com',
            display_name='Superuser',
            password='pass')
        foreign_language = ForeignLanguage.objects.create(
            key = 'fl-ll',
            english_name = 'English name',
            foreign_name = 'Foreign name',
            note = 'Variant',
            flag = tempfile.NamedTemporaryFile(suffix='.png').name,
            uses_latin_script = True,
            duolingo_learners = 1)

    def test_create_learning_language(self):
        learning_language = LearningLanguage.objects.create(
            user = CustomUser.objects.get(email='superuser@email.com'),
            foreign_language = ForeignLanguage.objects.get(key='fl-ll'))
        self.assertEqual(learning_language.user.email, 'superuser@email.com')
        self.assertEqual(learning_language.foreign_language.key, 'fl-ll')
        self.assertTrue(learning_language)
        self.assertTrue(learning_language.date_started is not None)
        self.assertEqual(len(learning_language.words_seen), 0)


class SynonymModelTest(TestCase):
    def test_create_synonym(self):
        synonym = Synonym.objects.create(english_word = 'English word')
        self.assertEqual(synonym.english_word, 'English word')


class TranslatableWordModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        s1 = Synonym.objects.create(english_word = 'Synonym 1')
        s2 = Synonym.objects.create(english_word = 'Synonym 2')
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

    def test_create_translatable_word(self):
        translatable_word = TranslatableWord.objects.create(english_word='English word')
        translatable_word.synonyms.add(Synonym.objects.get(english_word='Synonym 1'))
        translatable_word.synonyms.add(Synonym.objects.get(english_word='Synonym 2'))
        translatable_word.books.add(Book.objects.get(title='Book Title'))
        self.assertEquals(translatable_word.english_word, 'English word')
        self.assertEquals(translatable_word.synonyms.count(), 2)
        self.assertEquals(translatable_word.books.count(), 1)


class TranslationModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        translatable_word = TranslatableWord.objects.create(
            english_word = 'English word')
        foreign_language = ForeignLanguage.objects.create(
            key = 'fl-tr',
            english_name = 'English name',
            foreign_name = 'Foreign name',
            note = 'Variant',
            flag = tempfile.NamedTemporaryFile(suffix='.png').name,
            uses_latin_script = True,
            duolingo_learners = 1)

    def test_create_translation(self):
        translation = Translation.objects.create(
            translatable_word = TranslatableWord.objects.get(english_word='English word'),
            foreign_language = ForeignLanguage.objects.get(key='fl-tr'),
            foreign_word = 'Foreign word',
            pronunciation = 'Pronunciation')
        self.assertEquals(translation.translatable_word.english_word, 'English word')
        self.assertEquals(translation.foreign_language.key, 'fl-tr')
        self.assertEquals(translation.foreign_word, 'Foreign word')
        self.assertEquals(translation.pronunciation, 'Pronunciation')
        self.assertTrue(translation.last_modified is not None)
        self.assertEquals(translation.readable_word, 'Foreign word')