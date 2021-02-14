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


    # Get a user's active LearningLanguage
    # Return None if user has no active LearningLanguage
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

    # Get a user's LearningLanguage by its English name
    # Return None if user has no LearningLanguage for the given English name
    def learning_language(self, english_name):
        return next(
            (
                learning_language
                for learning_language in self.learning_languages.all()
                if learning_language.foreign_language.english_name == english_name
            ),
            None
        )
    
    # Returns a QuerySet of LearningTracking objects
    #   for a user in a given ForeignLanguage.
    def tracking_history(self, foreign_language):
        return self.learning_tracking.filter(translation__foreign_language = foreign_language)
    
    # Returns a list of unique Translation IDs
    #   for a user's LearningTracking objects in a given ForeignLanguage.
    def tracking_history_tid(self, foreign_language):
        return [
            t['translation__id']
            for t in self.tracking_history(foreign_language)
            .order_by('translation')
            .values('translation__id')
            .distinct()
        ]

    # Returns a list of LearningTracking objects
    #   for a user in a given ForeignLanguage.
    #   LearningTracking objects in the list are unique by Translation.
    #   Each LearningTracking is the user's most recent interaction with each Translation.
    def tracking_history_unique(self, foreign_language):
        tracking_history_unique = []
        for id in self.tracking_history_tid(foreign_language):
            # Take the most recent (last) LearningTracking from tracking_history
            tracking_history_unique.append(
                self.tracking_history(foreign_language).filter(translation__id = id).last()
            )
        return tracking_history_unique
    
    # Returns a list of Translation objects
    #   for a user in a given ForeignLanguage.
    #   Objects in the list are unique Translations the user has interacted with at least once.
    def words_learned(self, foreign_language):
        words_learned = []
        for lt in self.tracking_history_unique(foreign_language):
            words_learned.append(lt.translation)
        return words_learned

    def __str__(self):
        return f'{self.email} ({self.display_name})'

    class Meta:
        ordering = ['-is_superuser', 'email']
