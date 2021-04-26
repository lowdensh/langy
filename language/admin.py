from .models import ForeignLanguage, LearningLanguage, Synonym, TranslatableWord, Translation
from django.contrib import admin


@admin.register(ForeignLanguage)
class ForeignLanguageAdmin(admin.ModelAdmin):
    # Main list
    list_display = ('key', 'english_name', 'foreign_name', 'note', 'uses_latin_script', 'duolingo_learners',)
    list_display_links = ('english_name',)

    def uses_latin_script(self, instance):
        return instance.uses_latin_script

    uses_latin_script.boolean=True


@admin.register(LearningLanguage)
class LearningLanguageAdmin(admin.ModelAdmin):
    # Main list
    list_display = ('user', 'foreign_language', 'is_active',)
    list_display_links = ('user', 'foreign_language',)
    list_filter = ('user', 'foreign_language',)
    ordering = ('user', 'foreign_language',)

    # Specific LearningLanguage instance
    readonly_fields = ['date_started',]


admin.site.register(Synonym)


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
