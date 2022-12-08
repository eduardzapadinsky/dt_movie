from django.db.models import Q
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, redirect
from django.views import View
from django.views.generic import ListView, DetailView

from .models import Movie, Category, Actor, Genre, Rating
from .forms import ReviewForm, RatingForm


class GenreYear:
    """Жанри та роки виходу фільмів"""

    def get_genres(self):
        return Genre.objects.all()

    def get_years(self):
        return Movie.objects.filter(draft=False).values("year")


class MoviesView(GenreYear, ListView):
    """Список фільмів"""
    model = Movie
    queryset = Movie.objects.filter(draft=False)
    paginate_by = 2

    # template_name = "movies/movie_list.html"
    # django recognize _list template automatically


class MovieDetailView(GenreYear, DetailView):
    """Повний опис фільмів"""
    model = Movie
    slug_field = 'url'

    # django recognize _detail template automatically

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["star_form"] = RatingForm()
        context["form"] = ReviewForm()
        return context


class AddReview(View):
    """Відгуки"""

    def post(self, request, pk):
        form = ReviewForm(request.POST)
        movie = Movie.objects.get(id=pk)
        if form.is_valid():
            form = form.save(commit=False)
            if request.POST.get("parent", NotImplemented):
                form.parent_id = int(request.POST.get("parent"))
            form.movie = movie
            form.save()
        return redirect(movie.get_absolute_url())


class ActorView(GenreYear, DetailView):
    """Вивід інформації про актора """
    model = Actor
    template_name = 'movies/actor.html'
    slug_field = "name"


class FilterMoviesView(GenreYear, ListView):
    """Фільтр фільмів"""
    paginate_by = 2

    def get_queryset(self):
        if 'genre' in self.request.GET and 'year' in self.request.GET:
            print('if genre and year')
            queryset = Movie.objects.filter(
                Q(year__in=self.request.GET.getlist("year")),
                Q(genres__in=self.request.GET.getlist("genre"))
            ).distinct()
        else:
            print('else')
            queryset = Movie.objects.filter(
                Q(year__in=self.request.GET.getlist("year")) |
                Q(genres__in=self.request.GET.getlist("genre"))
            ).distinct()
        return queryset

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context["year"] = ''.join([f"year={x}&" for x in self.request.GET.getlist("year")])
        context["genre"] = ''.join([f"genre={x}&" for x in self.request.GET.getlist("genre")])
        return context


class AddStarRating(View):
    """Додавання рейтингу до фільму"""

    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip

    def post(self, request):
        form = RatingForm(request.POST)
        if form.is_valid():
            Rating.objects.update_or_create(
                ip=self.get_client_ip(request),
                movie_id=int(request.POST.get("movie")),
                defaults={'star_id': int(request.POST.get("star"))}
            )
            return HttpResponse(status=201)
        else:
            return HttpResponse(status=400)


class Search(ListView):
    """Пошук фільмів"""
    paginate_by = 2

    def get_queryset(self):
        return Movie.objects.filter(title__iregex=self.request.GET.get("q"))

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context["q"] = f'q={self.request.GET.get("q")}&'
        return context
