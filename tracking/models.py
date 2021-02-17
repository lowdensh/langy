from django.db import models
from language.models import ForeignLanguage, Translation
from read.models import Book
from users.models import CustomUser


# Returns a string
#   which is a formatted representation of a datetime object
#   e.g. 2021-02-09 15:02:51
def format_datetime(datetime):
    return datetime.strftime("%Y-%m-%d %H:%M:%S")


class LangySession(models.Model):
    TYPE_CHOICES = [
        ('READ', 'Reading'),
        ('TEST', 'Testing'),
    ]
    user = models.ForeignKey(to=CustomUser, on_delete=models.CASCADE, related_name='sessions')
    foreign_language = models.ForeignKey(to=ForeignLanguage, on_delete=models.CASCADE, related_name='sessions')
    session_type = models.CharField(max_length=4, choices=TYPE_CHOICES, default='READ')
    book = models.ForeignKey(to=Book, null=True, on_delete=models.CASCADE, related_name='sessions')
    start_time = models.DateTimeField(auto_now_add=True)
    end_time = models.DateTimeField(
        null=True,
        help_text='May be null if the session is not ended in a proper manner.')
    
    @property
    def fstart(self):
        return format_datetime(self.start_time)
    
    @property
    def fend(self):
        if self.end_time:
            return format_datetime(self.end_time)

    # Returns an int
    #   representing the amount of time in seconds the user spent in this session.
    #   Returns 0 if the session has no end_time
    @property
    def duration(self):
        if self.end_time:
            return int((self.end_time - self.start_time).total_seconds())
        return 0
    
    @property
    def fduration(self):
        return format_datetime(self.duration)

    def __str__(self):
        return f'{self.user} : ({self.foreign_language.key}) {self.session_type} @ {self.fstart}'

    class Meta:
        # Oldest first
        ordering = ['start_time']


class LearningTrace(models.Model):
    user = models.ForeignKey(to=CustomUser, on_delete=models.CASCADE, related_name='traces')
    session = models.ForeignKey(to=LangySession, on_delete=models.CASCADE, related_name='traces')

    # Tracing
    translation = models.ForeignKey(to=Translation, on_delete=models.CASCADE, related_name='traces')
    prev = models.ForeignKey(
        help_text='Previous interaction <b>(LearningTrace object)</b> the user had with this translation, if any',
        to='self',
        blank=True,
        null=True,
        on_delete=models.CASCADE)

    # Statistics
    read_count = models.PositiveIntegerField(
        help_text='Total times the user has interacted with this translation during <b>reading</b>',
        default=0)
    test_count = models.PositiveIntegerField(
        help_text='Total times the user has interacted with this translation during <b>testing</b>',
        default=0)
    test_correct = models.PositiveIntegerField(
        help_text='Total times the user has <b>correctly</b> translated this word during <b>testing</b>',
        default=0)

    # Returns a datetime
    #   indicating when the linked session was started.
    @property
    def time(self):
        return self.session.start_time

    @property
    def ftime(self):
        return format_datetime(self.time)

    # Returns an int
    #   for the amount of time in seconds since the previous interaction with this Translation.
    #   Returns 0 if there has been no previous interaction.
    @property
    def delta(self):
        if self.prev:
            return int((self.time - self.prev.time).total_seconds())
        return 0

    # Returns a float
    #   for the proportion of tests where the user has correctly translated this word.
    #   Returns 0 if the user has not been tested on this word.
    @property
    def p_trans(self):
        if self.test_count != 0:
            return self.test_correct / self.test_count
        return 0

    def __str__(self):
        return f'{self.session.user} : {self.translation} @ {self.ftime}'

    class Meta:
        # Oldest first, then alphabetically by English word, a to z
        ordering = ['session__start_time', 'translation__translatable_word__english_word']
