from django.db import models
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
    flag_flat = models.ImageField(upload_to='language_flags/flat')
    flag_button = models.ImageField(upload_to='language_flags/button')

    class Meta:
        ordering = ['english_name']

    def __str__(self):
        return self.english_name

    @property
    def popularity_score(self):
        # A measure of how popular a language is to learn
        return int(self.duolingo_learners/1000)


class LearningLanguage(models.Model):
    user = models.ForeignKey(to=CustomUser, on_delete=models.CASCADE)
    foreign_language = models.OneToOneField(to='ForeignLanguage', on_delete=models.CASCADE)
    is_active = models.BooleanField(default=True)
    xp = models.PositiveIntegerField(verbose_name='Experience', default=0)

    class Meta:
        ordering = ['user', 'foreign_language']

    def __str__(self):
        return f'{self.user}: {self.foreign_language}'


class WordCategory(models.Model):
    name = models.CharField(max_length=50, unique=True)

    class Meta:
        ordering = ['name']
        verbose_name_plural = 'Word categories'

    def __str__(self):
        return self.name


class TranslatableWord(models.Model):
    english_word = models.CharField(max_length=50, unique=True)
    categories = models.ManyToManyField(to='WordCategory')

    class Meta:
        ordering = ['english_word']

    def __str__(self):
        return self.english_word
