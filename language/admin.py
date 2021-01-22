from .models import LearningLanguage, ForeignLanguage, TranslatableWord, Translation
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
    list_display = ('key', 'english_name', 'native_name', 'note', 'popularity',)
    list_display_links = ('english_name',)


@admin.register(TranslatableWord)
class TranslatableWordAdmin(admin.ModelAdmin):
    # Main list
    list_display = ('english_word', 'is_used')
    list_display_links = ('english_word',)

    def is_used(self, instance):
        return instance.is_used

    is_used.boolean=True


# class TranslatableWordInline(admin.TabularInline):
    # model = Book.translatable_words.through
