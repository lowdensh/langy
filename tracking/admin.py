from .models import LangySession, LearningTrace
from django.contrib import admin


@admin.register(LangySession)
class LangySessionAdmin(admin.ModelAdmin):
    # Main list
    list_display = ('uid', 'lang', 'session_type', 'fstart', 'fend', 'words', 'book',)
    list_display_links = ('session_type',)
    list_filter = ('user', 'foreign_language', 'session_type',)

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
    list_display = ('uid', 'lang', 'eng', 'frn', 'stype', 'ftime', 'delta', 'seen', 'interacted', 'tested', 'correct', 'p_trans',)
    list_display_links = ('ftime',)
    list_filter = ('session__user', 'translation__foreign_language',)
    search_fields = (
        'translation__translatable_word__english_word',
        'translation__foreign_word',
        'translation__pronunciation',)

    # Specific LearningTrace instance
    fieldsets = (
        ('', {'fields': ('session',)}),
        ('Tracing', {'fields': ('user', 'translation',)}),
        ('Interaction', {'fields': ('time', 'prev', 'delta')}),
        ('Statistics', {'fields': ('seen', 'interacted', 'tested', 'correct',)}),
    )
    readonly_fields = ['time', 'delta']

    # Additional attributes
    def uid(self, obj):
        return obj.user.id
    
    def lang(self, obj):
        return obj.translation.foreign_language.key

    def eng(self, obj):
        return obj.translation.translatable_word.english_word

    def stype(self, obj):
        return obj.session.session_type

    def dam(self, obj):
        return obj.translation.dam

    def jar(self, obj):
        return '{:.3f}'.format(obj.translation.jar)
    
    def p_trans(self, obj):
        return '{:.3f}'.format(obj.p_trans)
