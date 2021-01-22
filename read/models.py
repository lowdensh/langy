from django.core.validators import FileExtensionValidator
from django.db import models
from nltk.tokenize import sent_tokenize


class Author(models.Model):
    forename = models.CharField(max_length=50)
    surname = models.CharField(max_length=50)
    middle_names = models.CharField(max_length=100, blank=True)

    def format(self, name):
        if len(name) == 1:
            return f'{name}.'
        return name

    @property
    def full_name(self):
        # Forename first
        return f'{self.format(self.forename)} {self.format(self.middle_names)} {self.format(self.surname)}'

    def __str__(self):
        # Surname first, with comma
        return f'{self.format(self.surname)}, {self.format(self.forename)} {self.format(self.middle_names)}'

    class Meta:
        ordering = ['surname', 'forename', 'middle_names',]


class Book(models.Model):
    title = models.CharField(max_length=200)
    author = models.ForeignKey(to=Author, on_delete=models.SET_DEFAULT, default=1)
    source_url = models.URLField('Source URL')
    summary = models.TextField(max_length=1000, blank=True)
    cover = models.ImageField(upload_to='book_covers', default='book_covers/default.jpg')
    pdf = models.FileField(
        'PDF', upload_to='book_pdfs', blank=True, null=True,
        validators=[FileExtensionValidator(allowed_extensions=['pdf'])]
    )

    @property
    def page_count(self):
        return self.pages.count()

    @property
    def has_pages(self):
        if self.page_count > 0:
            return True
        return False

    @property
    def summary_text(self):
        if self.summary:
            return self.summary
        return f'{self.title}, written by {self.author.full_name}.'

    @property
    def has_cover(self):
        if self.cover.name == 'book_covers/default.jpg':
            return False
        return True

    @property
    def has_pdf(self):
        if self.pdf:
            return True
        return False

    @property
    def translatable_word_count(self):
        return self.translatable_words.count()

    @property
    def has_translatable_words(self):
        if self.translatable_word_count == 0:
            return False
        return True
    
    def __str__(self):
        return self.title

    class Meta:
        ordering = ['title', 'author',]


class Page(models.Model):
    book = models.ForeignKey(to=Book, on_delete=models.CASCADE, related_name='pages')
    number = models.SmallIntegerField()
    text = models.TextField()
    image = models.ImageField(upload_to='book_page_images', blank=True, null=True)

    @property
    def text_snippet(self):
        max_length = 50
        if len(self.text) <= max_length:
            return f'{self.text}'
        else:
            return f'{self.text[0:max_length]}...'

    @property
    def sentences(self):
        # Used for pages with an image
        # Split page text in half and show image between the two halves
        return sent_tokenize(self.text)

    @property
    def text_half_1(self):
        half = len(self.sentences)//2
        # Join list of sentences (strings) into one, with spaces between
        # If there is only one sentence, text_half_1 is empty
        return ' '.join(self.sentences[:half])

    @property
    def text_half_2(self):
        half = len(self.sentences)//2
        # If there is only one sentence, text_half_2 contains it
        return ' '.join(self.sentences[half:])
    
    def __str__(self):
        return f'{self.book}, pg. {self.number} ({self.text_snippet})'

    class Meta:
        ordering = ['book', 'number',]
