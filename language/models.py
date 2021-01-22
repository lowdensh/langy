from django.db import models
from read.models import Book
from users.models import CustomUser


class ForeignLanguage(models.Model):
    key = models.CharField(
        max_length=5,
        help_text=('ISO-639-1 language codes for supported languages for translation. See <a '
            'href="https://py-googletrans.readthedocs.io/en/latest/#googletrans-languages">googletrans.LANGUAGES</a>.')
    )
    english_name = models.CharField(max_length=20)
    native_name = models.CharField(max_length=20)
    note = models.CharField(max_length=20, blank=True)
    duolingo_learners = models.PositiveIntegerField(
        help_text=('The amount of learners this language course has on Duolingo. See <a '
            'href="https://www.duolingo.com/courses">Duolingo Courses</a>.')
    )
    flag = models.ImageField(upload_to='language_flags')

    class Meta:
        ordering = ['english_name']

    def __str__(self):
        return self.english_name

    @property
    def popularity(self):
        # A measure of how popular a language is to learn
        return int(self.duolingo_learners/1000)


class LearningLanguage(models.Model):
    user = models.ForeignKey(to=CustomUser, on_delete=models.CASCADE, related_name='learning_languages')
    foreign_language = models.ForeignKey(to=ForeignLanguage, on_delete=models.CASCADE)
    is_active = models.BooleanField(default=True)
    date_started = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['user', 'foreign_language']

    def __str__(self):
        return f'{self.user}: {self.foreign_language}'


class TranslatableWord(models.Model):
    english_word = models.CharField(max_length=50, unique=True)
    books = models.ManyToManyField(to=Book, related_name='translatable_words')

    @property
    def book_count(self):
        return self.books.count()

    @property
    def is_used(self):
        if self.book_count == 0:
            return False
        return True

    class Meta:
        ordering = ['english_word']

    def __str__(self):
        return self.english_word


class Translation(models.Model):
    translatable_word = models.ForeignKey(to=TranslatableWord, on_delete=models.CASCADE, related_name='translations')
    language = models.ForeignKey(to=ForeignLanguage, on_delete=models.CASCADE, related_name='translations')
    # TODO check whats available from googletrans
    # native_word
    # romanisation
