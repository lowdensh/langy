from django.db import models
from read.models import Book
from users.models import CustomUser
import jellyfish


class ForeignLanguage(models.Model):
    key = models.CharField(
        max_length=5,
        help_text=('ISO-639-1 language codes for supported languages for translation. See <a '
            'href="https://py-googletrans.readthedocs.io/en/latest/#googletrans-languages">googletrans.LANGUAGES</a>.')
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
            'Ensure this field is False for languages which use different scripts (e.g. Russian: Cyrillic) or systems (e.g. Japanese: Kana, Kanji).')
    )
    duolingo_learners = models.PositiveIntegerField(
        help_text=('The amount of learners this language course has on Duolingo. See <a '
            'href="https://www.duolingo.com/courses">Duolingo Courses</a>.')
    )

    def __str__(self):
        return self.english_name

    class Meta:
        ordering = ['english_name']


class LearningLanguage(models.Model):
    user = models.ForeignKey(to=CustomUser, on_delete=models.CASCADE, related_name='learning_languages')
    foreign_language = models.ForeignKey(to=ForeignLanguage, on_delete=models.CASCADE)
    is_active = models.BooleanField(default=True)
    date_started = models.DateTimeField(auto_now_add=True)
    
    # Returns a list of Translations
    #   for this LearningLanguage's user.
    #   Translations in the list are unique and the user has interacted with at least once.
    @property
    def words_learnt(self):
        words_learnt = []
        for trace in self.user.traces_unique(self.foreign_language):
            words_learnt.append(trace.translation)
        return words_learnt

    def __str__(self):
        return f'{self.user} : {self.foreign_language}'

    class Meta:
        ordering = ['user', 'foreign_language']


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

    # Returns the Translation
    #   for this word in a given ForeignLanguage.
    #   Returns None if no Translation in this language exists.
    def translation(self, foreign_language):
        return self.translations.filter(foreign_language = foreign_language).first()

    def __str__(self):
        return self.english_word

    class Meta:
        ordering = ['english_word']


class Translation(models.Model):
    translatable_word = models.ForeignKey(to=TranslatableWord, on_delete=models.CASCADE, related_name='translations')
    foreign_language = models.ForeignKey(to=ForeignLanguage, on_delete=models.CASCADE, related_name='translations')
    foreign_word = models.CharField(max_length=50)
    pronunciation = models.CharField(max_length=50, blank=True)
    last_modified = models.DateTimeField(auto_now_add=True)

    # Returns a string
    #   representing the readable form of foreign_word.
    @property
    def readable_word(self):
        if (not self.foreign_language.uses_latin_script
            and self.pronunciation):
                return self.pronunciation
        return self.foreign_word
    
    # Similarity measure: Damerau-Levenshtein Distance
    # Returns an int
    #   representing the number of insertions, deletions, substitutions and transpositions required
    #   to get from the English to the Foreign word.
    @property
    def dam(self):
        return jellyfish.damerau_levenshtein_distance(self.translatable_word.english_word, self.readable_word)
    
    # Similarity measure: Jaro-Winkler Similarity
    # Returns a float
    #   between 0 and 1 representing the similarity of the English and the Foreign word.
    #   0 means no similarity,
    #   1 means complete similarity.
    @property
    def jar(self):
        return jellyfish.jaro_winkler_similarity(self.translatable_word.english_word, self.readable_word)

    def __str__(self):
        if self.foreign_language.uses_latin_script:
            return f'({self.foreign_language.key}) {self.translatable_word} -> {self.foreign_word}'
        return f'({self.foreign_language.key}) {self.translatable_word} -> {self.pronunciation} / {self.foreign_word}'

    class Meta:
        ordering = ['foreign_language', 'translatable_word']
