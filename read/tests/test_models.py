from django.test import TestCase
from read.models import Author, Book, Page
from users.models import CustomUser
import tempfile


class AuthorModelTest(TestCase):
    def test_create_author(self):
        author = Author.objects.create(
            forename = 'First',
            surname = 'Last',
            middle_names = 'Middle')
        self.assertEqual(author.forename, 'First')
        self.assertEqual(author.surname, 'Last')
        self.assertEqual(author.middle_names, 'Middle')
        

class BookModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        author = Author.objects.create(
            forename = 'First',
            surname = 'Last',
            middle_names = 'Middle')

    def test_create_book(self):
        author = Author.objects.get(forename='First')
        book = Book.objects.create(
            title = 'Book Title',
            author = author,
            source_url = 'url.com',
            cover = tempfile.NamedTemporaryFile(suffix='.jpg').name,
            pdf = tempfile.NamedTemporaryFile(suffix='.pdf').name)

        self.assertEqual(book.title, 'Book Title')
        self.assertEqual(book.author.forename, 'First')
        self.assertEqual(book.source_url, 'url.com')
        self.assertEqual(book.summary, '')
        self.assertEqual(book.summary_text, 'Book Title, written by First Middle Last.')
        self.assertTrue(book.cover is not None)
        self.assertTrue(book.pdf is not None)
        self.assertFalse(book.has_pages)
    
    def test_create_book_with_pages(self):
        author = Author.objects.get(forename='First')
        book = Book.objects.create(
            title = 'Book with Pages',
            author = author,
            source_url = 'url.com',
            cover = tempfile.NamedTemporaryFile(suffix='.jpg').name,
            pdf = tempfile.NamedTemporaryFile(suffix='.pdf').name)
        for i in range(5):
            page = Page.objects.create(
                book = book,
                number = i,
                text = 'Just a single sentence')
            book.pages.add(page)
        self.assertTrue(book.has_pages)
        self.assertEqual(book.page_count, 5)


class PageModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        author = Author.objects.create(
            forename = 'First',
            surname = 'Last',
            middle_names = 'Middle')
        book = Book.objects.create(
            title = 'Book Title',
            author = author,
            source_url = 'url.com',
            cover = tempfile.NamedTemporaryFile(suffix='.jpg').name,
            pdf = tempfile.NamedTemporaryFile(suffix='.pdf').name)
    
    def test_create_page(self):
        book = Book.objects.get(title='Book Title')
        page = Page.objects.create(
            book = book,
            number = 1,
            text = ('This is the text in the first Page of the Book.'
                ' It\'s a couple of sentences long.'
                ' This is the last sentence of the Page.'),
            image = tempfile.NamedTemporaryFile(suffix='.jpg').name)
        self.assertEqual(page.book.title, 'Book Title')
        self.assertEqual(page.number, 1)
        self.assertEqual(len(page.text), 119)
        self.assertEqual(page.text_snippet, 'This is the text in the first Page of the Book. It...')