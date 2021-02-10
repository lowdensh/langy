from .models import LearningLanguage, ForeignLanguage, TranslatableWord, Translation, LearningTracking
from django.contrib import admin


@admin.register(LearningLanguage)
class LearningLanguageAdmin(admin.ModelAdmin):
    # Main list
    list_display = ('user', 'foreign_language', 'is_active',)
    list_display_links = ('user', 'foreign_language',)
    list_filter = ('foreign_language',)
    ordering = ('user', 'foreign_language',)

    # Specific CustomUser instance
    readonly_fields = ['date_started',]


@admin.register(ForeignLanguage)
class ForeignLanguageAdmin(admin.ModelAdmin):
    # Main list
    list_display = ('key', 'english_name', 'foreign_name', 'note', 'uses_latin_script', 'popularity',)
    list_display_links = ('english_name',)

    def uses_latin_script(self, instance):
        return instance.uses_latin_script

    uses_latin_script.boolean=True


@admin.register(TranslatableWord)
class TranslatableWordAdmin(admin.ModelAdmin):
    # Main list
    list_display = ('english_word', 'is_used', 'book_count',)
    list_display_links = ('english_word',)

    def is_used(self, instance):
        return instance.is_used

    is_used.boolean=True


@admin.register(Translation)
class TranslationAdmin(admin.ModelAdmin):
    # Main list
    list_display = ('translatable_word', 'foreign_language', 'foreign_word', 'pronunciation',)
    list_display_links = ('translatable_word',)
    list_filter = ('foreign_language',)

    # Specific Translation instance
    readonly_fields = ['last_modified',]


@admin.register(LearningTracking)
class LearningTrackingAdmin(admin.ModelAdmin):
    # Main list
    list_display = ('uid', 'lang', 'eng', 'frn', 'ftime', 'delta', 'len', 'dam', 'jar', 'read', 'test', 'correct', 'p_trans',)
    list_display_links = ('ftime',)
    list_filter = ('user',)

    # Specific Translation instance
    fieldsets = (
        ('Tracking', {'fields': ('user', 'translation',)}),
        ('Interaction', {'fields': ('time', 'prev',)}),
        ('Statistics', {'fields': ('read_count', 'test_count', 'test_correct',)}),
    )
    readonly_fields = ['time',]

    # Additional columns
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
