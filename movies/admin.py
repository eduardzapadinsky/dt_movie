from django.contrib import admin
from django import forms
from django.utils.safestring import mark_safe
from .models import Category, Actor, Genre, Movie, MovieShots, RatingStar, Rating, Reviews
from ckeditor_uploader.widgets import CKEditorUploadingWidget
from modeltranslation.admin import TranslationAdmin


class MovieAdminForm(forms.ModelForm):
    """Форма з віджетом ckeditor"""
    description_uk = forms.CharField(label="Опис", widget=CKEditorUploadingWidget())
    description_en = forms.CharField(label="Опис", widget=CKEditorUploadingWidget())

    class Meta:
        model = Movie
        fields = '__all__'


@admin.register(Category)
class CategoryAdmin(TranslationAdmin):
    """Категорії"""
    list_display = ("id", "name", "url")
    list_display_links = ("name",)


# class ReviewInline(admin.StackedInline):
#     model = Reviews
#     extra = 1

class ReviewInline(admin.TabularInline):
    """Відгуки на сторінці фільму"""
    model = Reviews
    extra = 1
    readonly_fields = ("name", "email")


class MovieShotsInline(admin.TabularInline):
    """Кадри з фільму на сторінці фільму"""
    model = MovieShots
    extra = 1
    readonly_fields = ("get_image",)

    # Відображення зображень
    def get_image(self, obj):
        return mark_safe(f'<img src={obj.image.url} height="150"')

    get_image.short_description = "Зображення"


@admin.register(Movie)
class MovieAdmin(TranslationAdmin):
    """Фільми"""
    list_display = ("title", "category", "url", "draft")
    list_filter = ("category", "year")
    search_fields = ("title", "category__name", "actors__name")
    inlines = [MovieShotsInline, ReviewInline]
    save_on_top = True
    save_as = True
    list_editable = ("category", "draft",)
    form = MovieAdminForm
    actions = ["publish", "unpublish"]
    readonly_fields = ("get_image",)
    fieldsets = (
        (None, {"fields": (("title", "tagline"),)}),
        (None, {"fields": ("description", ("poster", "get_image"))}),
        (None, {"fields": (("year", "world_premiere", "country"),)}),
        ("Actors", {
            "classes": ("collapse",),
            "fields": (("actors", "directors", "genres", "category"),)
        }),
        (None, {"fields": (("budget", "fees_in_usa", "fees_in_world"),)}),
        ("Options", {"fields": (("url", "draft"),)}),
    )

    # Відображення зображень
    def get_image(self, obj):
        return mark_safe(f'<img src={obj.poster.url} height="150"')

    def unpublish(self, request, queryset):
        """Зняти з публікації"""
        row_update = queryset.update(draft=True)
        if row_update == 1:
            message_bit = "1 запис було оновлено"
        elif 2 <= row_update <= 4:
            message_bit = f"{row_update} записи було оновлено"
        else:
            message_bit = f"{row_update} записів було оновлено"
        self.message_user(request, f"{message_bit}")

    def publish(self, request, queryset):
        """Опублікувати"""
        row_update = queryset.update(draft=False)
        if row_update == 1:
            message_bit = "1 запис було оновлено"
        elif 2 <= row_update <= 4:
            message_bit = f"{row_update} записи було оновлено"
        else:
            message_bit = f"{row_update} записів було оновлено"
        self.message_user(request, f"{message_bit}")

    unpublish.short_description = "Зняти з публікації"
    unpublish.allowed_permissions = ('change',)

    publish.short_description = "Опублікувати"
    publish.allowed_permissions = ('change',)

    get_image.short_description = "Постер"


@admin.register(Actor)
class ActorAdmin(TranslationAdmin):
    """Актори"""
    list_display = ("name", "age", "get_image")
    readonly_fields = ("get_image",)

    # Відображення зображень акторів
    def get_image(self, obj):
        return mark_safe(f'<img src={obj.image.url} height="60"')

    get_image.short_description = "Зображення"


@admin.register(Reviews)
class ReviewsAdmin(admin.ModelAdmin):
    """Відгуки"""
    list_display = ("name", "email", "parent", "movie")
    readonly_fields = ("name", "email")


@admin.register(Genre)
class GenreAdmin(TranslationAdmin):
    """Жанри"""
    list_display = ("name", "url")


@admin.register(Rating)
class RatingAdmin(admin.ModelAdmin):
    """Рейтинг"""
    list_display = ("star", "movie", "ip")


@admin.register(MovieShots)
class MovieShotsAdmin(TranslationAdmin):
    """Кадри з фільму"""
    list_display = ("title", "movie", "get_image")
    readonly_fields = ("get_image",)

    # Відображення зображень кадрів
    def get_image(self, obj):
        return mark_safe(f'<img src={obj.image.url} height="60"')

    get_image.short_description = "Зображення"


admin.site.register(RatingStar)

admin.site.site_title = "DjangoY Movies"
admin.site.site_header = "DjangoY Movies"
