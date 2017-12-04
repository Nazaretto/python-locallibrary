from django.contrib import admin

# Register your models here.
from .models import Author, Genre, Book, BookInstance

admin.site.register(Genre)


def duplicate_event(modeladmin, request, queryset):
    for object in queryset:
        object.id = None
        object.save()
duplicate_event.short_description = "Duplicate selected record"


class BooksInstanceInline(admin.TabularInline):
    model = BookInstance
    actions = [duplicate_event]
    extra = 0

class AuthorInline(admin.TabularInline):
    model = Author
    list_display = ('date_of_death')
    #actions = [duplicate_event]


@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):

    list_filter = ('last_name', 'first_name')
    list_display = ('last_name', 'first_name', 'date_of_birth', 'date_of_death')
    fields = ['first_name', 'last_name', ('date_of_birth', 'date_of_death')]
# Register the admin class with the associated model


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'display_genre')
    inlines = [BooksInstanceInline]


# Register the Admin classes for BookInstance using the decorator
@admin.register(BookInstance)
class BookInstanceAdmin(admin.ModelAdmin):
    list_filter = ('status', 'due_back')
    list_display = ('book', 'imprint', 'status', 'borrower',  'id')
    fieldsets = (
        ('Шось украинськє', {
            'fields': ('book', 'imprint', 'id')
        }),
        ('Availability', {
            'fields': ('status', 'due_back', 'borrower')
        }),
    )
    actions = [duplicate_event]
