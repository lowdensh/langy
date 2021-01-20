from .models import LearningLanguage, ForeignLanguage, WordCategory, TranslatableWord
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


admin.site.register([WordCategory, TranslatableWord])
