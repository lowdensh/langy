from .models import LearningLanguage, ForeignLanguage, WordCategory, TranslatableWord
from django.contrib import admin


@admin.register(LearningLanguage)
class LearningLanguageAdmin(admin.ModelAdmin):
    # Main list
    list_display = ('user', 'foreign_language', 'xp', 'is_active',)
    list_display_links = ('foreign_language', 'user',)
    list_filter = ('foreign_language', 'user',)


@admin.register(ForeignLanguage)
class ForeignLanguageAdmin(admin.ModelAdmin):
    # Main list
    list_display = ('key', 'english_name', 'native_name', 'popularity_score',)
    list_display_links = ('english_name',)

    # Specific ForeignLanguage instance
    fieldsets = (
        ('', {'fields': ('key', 'english_name', 'native_name', 'note', 'duolingo_learners',)}),
        ('Images', {'fields': ('flag_flat', 'flag_button',)}),
    )
    add_fieldsets = (
        ('', {'fields': ('key', 'english_name', 'native_name', 'note', 'duolingo_learners',)}),
        ('Images', {'fields': ('flag_flat', 'flag_button',)}),
    )

admin.site.register([WordCategory, TranslatableWord])
