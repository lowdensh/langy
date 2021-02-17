from .models import LangySession, LearningTrace
from django.contrib import admin


@admin.register(LangySession)
class LangySessionAdmin(admin.ModelAdmin):
    # Main list
    list_display = ('uid', 'lang', 'session_type', 'fstart', 'fend', 'words', 'book',)
    list_display_links = ('session_type',)
    list_filter = ('user', 'session_type',)

    # Specific Session instance
    readonly_fields = ['start_time', 'end_time',]

    # Additional or renamed attributes
    def uid(self, obj):
        return obj.user.id

    def lang(self, obj):
        return obj.foreign_language.key
    
    def words(self, obj):
        return obj.traces.count()


@admin.register(LearningTrace)
class LearningTraceAdmin(admin.ModelAdmin):
    # Main list
    list_display = ('uid', 'lang', 'eng', 'frn', 'ftime', 'delta', 'len', 'dam', 'jar', 'read', 'test', 'correct', 'p_trans',)
    list_display_links = ('ftime',)
    list_filter = ('session__user', 'translation__foreign_language',)

    # Specific LearningTrace instance
    fieldsets = (
        ('', {'fields': ('session',)}),
        ('Tracing', {'fields': ('user', 'translation',)}),
        ('Interaction', {'fields': ('time', 'prev',)}),
        ('Statistics', {'fields': ('read_count', 'test_count', 'test_correct',)}),
    )
    readonly_fields = ['time',]

    # Additional or renamed attributes
    def uid(self, obj):
        return obj.user.id

    def lang(self, obj):
        return obj.translation.foreign_language.key

    def eng(self, obj):
        return obj.translation.translatable_word.english_word

    def frn(self, obj):
        return obj.translation.readable_word

    def len(self, obj):
        return len(obj.translation.readable_word)

    def dam(self, obj):
        return obj.translation.dam

    def jar(self, obj):
        return '{:.3f}'.format(obj.translation.jar)

    def read(self, obj):
        return obj.read_count

    def test(self, obj):
        return obj.test_count

    def correct(self, obj):
        return obj.test_correct
    
    def p_trans(self, obj):
        return '{:.3f}'.format(obj.p_trans)
