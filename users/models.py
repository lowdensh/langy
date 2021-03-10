from .managers import CustomUserManager
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models
from django.utils import timezone


class CustomUser(AbstractBaseUser, PermissionsMixin):
    # Required fields
    email = models.EmailField(unique=True)
    display_name = models.CharField(
        max_length=20,
        help_text='A publicly displayed name. Does not need to be unique, and can be changed whenever you want.'
    )

    # Automatic fields
    date_joined = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField('Active', default=True)
    is_staff = models.BooleanField('Staff', default=False)
    is_superuser = models.BooleanField('Super', default=False)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['display_name']
    objects = CustomUserManager()


    # Returns a LearningLanguage
    #   which is set as active for the user.
    #   Returns None if the user has no active LearningLanguage.
    @property
    def active_language(self):
        return next(
            (
                learning_language
                for learning_language in self.learning_languages.all()
                if learning_language.is_active==True
            ),
            None
        )

    # Returns a LearningLanguage
    #   belonging to the user by specifying its English name.
    #   Returns None if user has no LearningLanguage for the given English name.
    def learning_language(self, english_name):
        return next(
            (
                learning_language
                for learning_language in self.learning_languages.all()
                if learning_language.foreign_language.english_name == english_name
            ),
            None
        )
    
    # Returns a list of unique Translation IDs
    #   for the user's LearningTraces in a given ForeignLanguage.
    def traces_unique_tid(self, foreign_language):
        return [
            t['translation__id']
            for t in self.traces
                .filter(translation__foreign_language = foreign_language)
                .order_by('translation')
                .values('translation__id')
                .distinct()
        ]

    # Returns a list of LearningTraces
    #   for the user in a given ForeignLanguage.
    #   LearningTraces in the list are unique by Translation.
    #   Each LearningTrace is the user's most recent (i.e. last) interaction with each Translation.
    def traces_unique(self, foreign_language, ordering='alphabetical'):
        traces_unique = []
        for id in self.traces_unique_tid(foreign_language):
            traces_unique.append(
                self.traces
                .filter(translation__foreign_language = foreign_language)
                .filter(translation__id = id)
                .last()
            )

        if ordering == 'alphabetical':
            # Order by LearningTrace.translation.translatable_word.english_word, A to Z
            return traces_unique

        if ordering == 'oldest':
            # Order by LearningTrace.time, oldest first
            return sorted(traces_unique, key=lambda trace: trace.time)
    
    # Returns a list of Translations
    #   for the user in a given ForeignLanguage.
    #   Translations in the list are unique and the user has interacted with at least once.
    def words_learnt(self, foreign_language):
        words_learnt = []
        for trace in self.traces_unique(foreign_language):
            if trace.interacted > 0:
                words_learnt.append(trace.translation)
        return words_learnt

    def __str__(self):
        return f'{self.email}'

    class Meta:
        ordering = ['-is_superuser', 'email']
