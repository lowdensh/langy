from django.db import models
from read.models import Book
from users.models import CustomUser


class ForeignLanguage(models.Model):
    key = models.CharField(
        max_length=5,
        help_text=('ISO-639-1 language codes for supported languages for translation. See <a '
            'href="https://py-googletrans.readthedocs.io/en/latest/#googletrans-languages">googletrans.LANGUAGES</a>.'
        )
    )
    english_name = models.CharField(max_length=20)
    foreign_name = models.CharField(max_length=20)
    note = models.CharField(max_length=20, blank=True)
    flag = models.ImageField(upload_to='language_flags')
    uses_latin_script = models.BooleanField(
        'Uses Latin script',
        default=True,
        help_text=('The English language uses Latin script, an Alphabetical <a '
            'href="https://en.wikipedia.org/wiki/Writing_system"> writing system</a>.<br>'
            'Ensure this field is False for languages which use different scripts (e.g. Russian: Cyrillic) or systems (e.g. Japanese: Kana, Kanji).'
        )
    )
    duolingo_learners = models.PositiveIntegerField(
        help_text=('The amount of learners this language course has on Duolingo. See <a '
            'href="https://www.duolingo.com/courses">Duolingo Courses</a>.'
        )
    )

    @property
    def popularity(self):
        # A measure of how popular a language is to learn
        return int(self.duolingo_learners/1000)

    class Meta:
        ordering = ['english_name']

    def __str__(self):
        return self.english_name


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
    foreign_language = models.ForeignKey(to=ForeignLanguage, on_delete=models.CASCADE, related_name='translations')
    foreign_word = models.CharField(max_length=50)
    pronunciation = models.CharField(max_length=50, blank=True)
    last_modified = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['foreign_language', 'translatable_word']

    def __str__(self):
        if self.foreign_language.uses_latin_script:
            return f'({self.foreign_language}) {self.translatable_word} : {self.foreign_word}'
        else:
            return f'({self.foreign_language}) {self.translatable_word} : {self.foreign_word} : {self.pronunciation}'
