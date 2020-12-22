from django.db import models


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
    author = models.ForeignKey(Author, on_delete=models.SET_DEFAULT, default=1)
    summary = models.TextField(max_length=1000, blank=True)
    source_url = models.URLField()
    cover = models.ImageField('Book Cover', blank=True, null=True, upload_to='book_covers')
    pdf = models.FileField('Book PDF', blank=True, null=True, upload_to='book_pdfs')

    @property
    def page_count(self):
        return self.pages.count()

    @property
    def has_pages(self):
        if self.page_count > 0:
            return True
        return False

    @property
    def has_cover(self):
        if self.cover:
            return True
        return False

    @property
    def has_pdf(self):
        if self.pdf:
            return True
        return False
    
    def __str__(self):
        return self.title

    class Meta:
        ordering = ['title', 'author',]


class Page(models.Model):
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='pages')
    number = models.SmallIntegerField()
    text = models.TextField()

    @property
    def text_snippet(self):
        max_length = 50
        if len(self.text) <= max_length:
            return f'{self.text}'
        else:
            return f'{self.text[0:max_length]}...'
    
    def __str__(self):
        return f'{self.book}, pg. {self.number} ({self.text_snippet})'

    class Meta:
        ordering = ['book', 'number',]
