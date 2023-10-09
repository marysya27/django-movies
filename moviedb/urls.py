from django.urls import path

from .views import *

urlpatterns = [
    path('', AllMovies.as_view(), name='home'),
    path('all_movies/<int:page>', AllMovies.as_view(), name='home'),
    path('pop/<int:page>', PopMovies.as_view(), name='Popular'),
    path('now/<int:page>', NowWatchMovies.as_view(), name='Now watching'),
    path('top/<int:page>', TopMovies.as_view(), name='Top rated'),
    path('people/<int:page>', PeopleList.as_view(), name='people'),
    path('desc/<int:pk>', DescriptionMovie.as_view(), name='desc'),
    path('descperson/<int:pk>', DescriptionPersonView.as_view(), name='descperson'),
    path('filter/<int:page>', filter_movies, name='filter'),
    path('cast/<int:pk>', CastList.as_view(), name='cast'),
    path('similar/<int:pk>', SimilarMovies.as_view(), name='similar'),
    path('search_person/<int:page>', SearchPerson.as_view(), name='search_person'),
    path('search_movie/<int:page>', SearchMovie.as_view(), name='search_movie'),
]
