from .models import Author, Book, Page
from django.contrib import admin


@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    # Main list
    list_display = ('__str__', 'surname', 'forename', 'middle_names',)
    list_display_links = ('__str__',)
    search_fields = ( 'surname','forename', 'middle_names',)
    ordering = ('surname', 'forename', 'middle_names',)


admin.site.register(Page)


class PageInline(admin.TabularInline):
    model = Page


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    # Main list
    list_display = ('title', 'author', 'has_pages', 'has_cover', 'has_pdf',)
    list_display_links = ('title',)
    list_filter = ('author',)
    search_fields = ('title', 'author',)
    ordering = ('title', 'author',)

    def has_pages(self, instance):
        return instance.has_pages

    def has_cover(self, instance):
        return instance.has_cover

    def has_pdf(self, instance):
        return instance.has_pdf

    has_pages.boolean=True
    has_cover.boolean=True
    has_pdf.boolean=True

    # Specific Book
    inlines = [PageInline]
