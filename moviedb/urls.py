from django.urls import path

from .views import *

urlpatterns = [
    path('', all_movies, name='home'),
    path('all_movies/<int:page>', all_movies, name='home'),
    path('pop/<int:page>', popmovies, name='Popular'),
    path('now/<int:page>', nowmovies, name='Now watching'),
    path('top/<int:page>', topmovies, name='Top rated'),
    path('people/<int:page>', poppeople, name='people'),
    # path('all_movies/<int:page>', all_movies, name='all'),
    path('desc/<int:pk>', descrip, name='desc'),
    path('descperson/<int:pk>', descripperson, name='descperson'),
    path('filter/<int:page>', filter_movies, name='filter'),
    path('cast/<int:pk>', cast_list, name='cast'),
    path('similar/<int:pk>', similar_movies, name='similar'),
    path('search_person/<int:page>', search_person, name='search_person'),
    path('search_movie/<int:page>', search_movie, name='search_movie'),
]
