# https://docs.djangoproject.com/en/3.1/topics/db/models/
# https://docs.djangoproject.com/en/3.1/ref/models/fields/
# Allow empty strings (CharField etc.) but not NULL i.e. blank=True

from django.db import models


class Author(models.Model):
    first_name = models.CharField(max_length=50)
    other_names = models.CharField(max_length=50, blank=True)
    last_name = models.CharField(max_length=50)

    class Meta:
        ordering = ['last_name', 'first_name']

    def __str__(self):
        return f'{self.last_name}, {self.first_name} {self.other_names}'

    @property
    def full_name(self):
        return f'{self.first_name} {self.other_names} {self.last_name}'


class Book(models.Model):
    title = models.CharField(max_length=200)
    author = models.ForeignKey(Author, on_delete=models.SET_NULL, null=True)
    website = models.URLField()
    summary = models.TextField(max_length=1000, blank=True)
    pub_date = models.DateField(verbose_name='Date Published', blank=True, null=True)
    publisher = models.CharField(max_length=100, blank=True)
    isbn = models.CharField('ISBN', max_length=13, blank=True, help_text=(
        'A 10 or 13 character <a href="https://www.isbn-international.org/content/what-isbn">ISBN</a>. '
        'This is <a href="https://en.wikipedia.org/wiki/International_Standard_Book_Number#Overview">different for '
        'separate editions and variations</a> of the same book.'),
    )

    class Meta:
        ordering = ['title', 'author', '-pub_date']

    def __str__(self):
        return self.title
