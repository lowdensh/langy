from django.db import models
from read.models import Book
from users.models import CustomUser
import jellyfish


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

    # Get the Translation for this word in a given ForeignLanguage
    # Returns None if it does not exist
    def translation(self, foreign_language):
        return self.translations.filter(foreign_language = foreign_language).first()

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

    # Readable form of foreign_word
    @property
    def readable_word(self):
        if (not self.foreign_language.uses_latin_script
            and self.pronunciation):
                return self.pronunciation
        return self.foreign_word
    
    # Similarity measure: Damerau-Levenshtein Distance
    #   Return the number of insertions, deletions, substitutions and transpositions required
    #   to get from English to Foreign word
    @property
    def dam(self):
        return jellyfish.damerau_levenshtein_distance(self.translatable_word.english_word, self.readable_word)
    
    # Similarity measure: Jaro-Winkler Similarity
    #   Return a float between 0 and 1 representing the similarity between
    #   the English and Foreign word
    #   where 0 means no similarity
    #   and 1 represents complete similarity
    @property
    def jar(self):
        return jellyfish.jaro_winkler_similarity(self.translatable_word.english_word, self.readable_word)

    class Meta:
        ordering = ['foreign_language', 'translatable_word']

    def __str__(self):
        if self.foreign_language.uses_latin_script:
            return f'({self.foreign_language}) {self.translatable_word} : {self.foreign_word}'
        else:
            return f'({self.foreign_language}) {self.translatable_word} : {self.foreign_word} : {self.pronunciation}'
    

class LearningTracking(models.Model):
    # Tracking
    user = models.ForeignKey(to=CustomUser, null=True, on_delete=models.SET_NULL, related_name='learning_tracking')
    translation = models.ForeignKey(to=Translation, on_delete=models.CASCADE, related_name='learning_tracking')

    # Interaction
    time = models.DateTimeField(
        help_text='Time when the user interacted with this word',
        auto_now_add=True)
    prev = models.ForeignKey(
        help_text='Previous interaction <b>(LearningTracking object)</b> the user had with this word, if any',
        to='self',
        blank=True,
        null=True,
        on_delete=models.CASCADE)

    # Statistics
    read_count = models.PositiveIntegerField(
        help_text='Total times the user has interacted with this word during <b>reading</b>',
        default=0)
    test_count = models.PositiveIntegerField(
        help_text='Total times the user has interacted with this word during <b>testing</b>',
        default=0)
    test_correct = models.PositiveIntegerField(
        help_text='Total times the user has <b>correctly</b> translated this word during <b>testing</b>',
        default=0)

    # Formatted time
    # e.g. 2021-02-09 15:02:51
    @property
    def ftime(self):
        return self.time.strftime("%Y-%m-%d %H:%M:%S")

    # Return an int representing the amount of time in seconds since the previous interaction with this word
    # Return None if there has been no previous interaction
    @property
    def delta(self):
        if self.prev:
            return int((self.time - self.prev.time).total_seconds())
        return None

    # Proportion of tests where the user has correctly translated this word
    # Return None if the user has not been tested on this word
    @property
    def p_trans(self):
        if self.test_count != 0:
            return self.test_correct / self.test_count
        return None

    class Meta:
        # Oldest first
        ordering = ['time']
        verbose_name = ' Learning Tracking'
        verbose_name_plural = ' Learning Tracking'

    # Formatted time and readable word
    def __str__(self):
        return f'{self.ftime} ({self.translation.readable_word})'
