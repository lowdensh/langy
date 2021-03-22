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
    end_time = models.DateTimeField(null=True)
    
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
        help_text='User\'s previous <b>LearningTrace</b> for this translation, if any',
        to='self',
        blank=True,
        null=True,
        on_delete=models.CASCADE)

    # Statistics
    seen = models.PositiveIntegerField(
        help_text='Amount of times the user has <b>seen</b> this translation during <b>reading and testing</b>',
        default=0)
    interacted = models.PositiveIntegerField(
        help_text='Amount of times the user has <b>interacted</b> with this translation during <b>reading</b>',
        default=0)
    tested = models.PositiveIntegerField(
        help_text='Amount of times the user has been <b>tested</b> on this translation',
        default=0)
    correct = models.PositiveIntegerField(
        help_text='Amount of times the user has <b>correctly</b> translated this word during <b>testing</b>',
        default=0)
    
    # Returns a string
    #   of the readable foreign word for the related translation.
    @property
    def frn(self):
        return self.translation.readable_word

    # Returns a datetime
    #   indicating when the related LangySession was started.
    @property
    def time(self):
        return self.session.start_time

    @property
    def ftime(self):
        return format_datetime(self.time)

    # Returns an int
    #   for the amount of time in seconds the user last saw this trace's Translation.
    #   Returns 0 if the user has never seen it before.
    @property
    def delta(self):
        if self.prev:
            return int((self.time - self.prev.time).total_seconds())
        return 0

    # Returns a float
    #   for the proportion of tests where the user has correctly translated this word.
    #   Returns 0 if the user has never been tested on it before.
    @property
    def p_trans(self):
        if self.tested != 0:
            return self.correct / self.tested
        return 0

    def __str__(self):
        return f'{self.session.user} : {self.translation} @ {self.ftime}'

    class Meta:
        # Oldest first, then alphabetically by English word, A to Z
        ordering = ['session__start_time', 'translation__translatable_word__english_word']
