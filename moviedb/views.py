from django.shortcuts import render
from django.views.generic import View, ListView, DetailView
import requests
import re
from decouple import config

from .utils import *

path_for_img = 'https://image.tmdb.org/t/p/w500'

api_key = config('API_KEY')

def index(url):
    response = requests.get(url, params={
        "api_key" : api_key 
    })
    data = response.json()
    movies = data.get("results", [])
    if data['total_pages'] > 20:
        total = 20
        totalPages = [pag + 1 for pag in range(total)]
    else:
        totalPages = [pag + 1 for pag in range(data['total_pages'])]

    return [movies, totalPages, data['page']]


class PopMovies(DataMixin, ListView):
    template_name = 'moviedb/movie_list.html'

    def get_queryset(self):
        page = self.kwargs.get('page')
        print(page)
        url = f"https://api.themoviedb.org/3/movie/popular?language=en-US&page={page}"
        return url
    
    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        movies_data = calculate_movies_data(index, self.get_queryset, self.get_user_context, 'Popular')
        context.update(movies_data)
        return context

class NowWatchMovies(DataMixin, ListView):
    template_name = 'moviedb/movie_list.html'

    def get_queryset(self):
        page = self.kwargs.get('page')
        url = f"https://api.themoviedb.org/3/movie/now_playing?language=en-US&page={page}"
        return url
    
    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        movies_data = calculate_movies_data(index, self.get_queryset, self.get_user_context, 'Now watching')
        context.update(movies_data)
        return context

class TopMovies(DataMixin, ListView):
    template_name = 'moviedb/movie_list.html'

    def get_queryset(self):
        page = self.kwargs.get('page')
        url = f"https://api.themoviedb.org/3/movie/top_rated?language=en-US&page={page}"
        return url
    
    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        movies_data = calculate_movies_data(index, self.get_queryset, self.get_user_context, 'Now watching')
        print(movies_data)
        context.update(movies_data)
        return context

class PeopleList(DataMixin, ListView):
    template_name = 'moviedb/person_list.html'

    def get_queryset(self):
        page = self.kwargs.get('page')
        url = f"https://api.themoviedb.org/3/person/popular?language=en-US&page={page}"
        return url
    
    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        people_data = calculate_movies_data(index, self.get_queryset, self.get_user_context, 'people')
        people_data['person'] = people_data.pop('movies')
        context.update(people_data)
        return context

class AllMovies(DataMixin, ListView):

    template_name = 'moviedb/allmovie_list.html'

    def get(self, request, *args, **kwargs):
        request.session['select_genres'] = []
        request.session['select_year'] = ''
        request.session['select_sort'] = ''
        request.session['search_form_movies'] = ''
        request.session['search_form_person'] = ''
        return super().get(request, *args, **kwargs)

    years = [i for i in range(2025, 1915, -1)]
    url_genres = f'https://api.themoviedb.org/3/genre/movie/list?api_key={api_key}'
    response_genres = requests.get(url_genres)
    data_genres = response_genres.json()

    def get_queryset(self):
        page = self.kwargs.get('page')
        url = f"https://api.themoviedb.org/3/discover/movie?language=en-US&page={page}"
        return url
    
    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        movies_data = calculate_movies_data(index, self.get_queryset, self.get_user_context, 'home')
        context.update(movies_data)
        context.update({'years' : self.years,  'genres' : self.data_genres['genres']})
        return context

class SearchMovie(DataMixin, ListView):
    template_name = 'moviedb/allmovie_list.html'

    def get_queryset(self):

        if self.request.GET.get('search_form_movie'): 
            query = self.request.GET.get('search_form_movie') 
            self.request.session['search_form_movie'] = self.request.GET.get('search_form_movie')
        else:
            query = self.request.session.get('search_form_movie')

        page = self.kwargs.get('page')
        url = f"https://api.themoviedb.org/3/search/movie?query={query}&include_adult=false&language=en-US&page={page}"
        return url

    
    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        movies_data = calculate_movies_data(index, self.get_queryset, self.get_user_context, 'search_movie')
        context.update(movies_data)
        return context


class SearchPerson(DataMixin, ListView):
    template_name = 'moviedb/person_list.html'

    def get_queryset(self):
        if self.request.GET.get('search_form_person'): 
            query = self.request.GET.get('search_form_person') 
            self.request.session['search_form_person'] = self.request.GET.get('search_form_person')
        else:
            query = self.request.session.get('search_form_person') 

        page = self.kwargs.get('page')
        url = f"https://api.themoviedb.org/3/search/person?query={query}&include_adult=false&language=en-US&page={page}"
        return url

    
    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        person_data = calculate_movies_data(index, self.get_queryset, self.get_user_context, 'search_movie')
        person_data['person'] = person_data.pop('movies')
        context.update(person_data)
        return context

class CastList(DataMixin, ListView):
    template_name = 'moviedb/cast_list.html'

    def get_queryset(self):
        pk = self.kwargs.get('pk')
        cast = f'https://api.themoviedb.org/3/movie/{pk}/credits?api_key={api_key}'
        response_cast = requests.get(cast)
        data_cast = response_cast.json()
        return data_cast['cast']

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['cast'] = self.get_queryset
        context['pk'] = self.kwargs.get('pk')
        context['path'] = path_for_img
        return context

class SimilarMovies(DataMixin, ListView):
    template_name = 'moviedb/similar_movie.html'

    def get_queryset(self):
        pk = self.kwargs.get('pk')
        url = f'https://api.themoviedb.org/3/movie/{pk}/similar?api_key={api_key}'
        return url

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        movies_data = calculate_movies_data(index, self.get_queryset, self.get_user_context, None)
        context['pk'] = self.kwargs.get('pk')
        context.update(movies_data)
        return context


class DescriptionPersonView(View):
    template_name = 'moviedb/descripperson.html'

    def get_queryset(self):
        pk = self.kwargs.get('pk')
        url = f'https://api.themoviedb.org/3/person/{pk}?api_key={api_key}'
        return url

    def post(self, request, pk):
        if request.method == 'POST':
            known_for = request.POST.get('known_for')
            pattern = r"'id': (\d+)"
            matches = re.findall(pattern, known_for)
            id_list = [int(match) for match in matches]

            known_for_movie = []
            for id in id_list:
                result = self.data_each_movie(id)
                if len(result) > 3:
                    known_for_movie.append({'id_movie' : id, 'title' : result['title'], 'poster_path' : result['poster_path']})

            response = requests.get(self.get_queryset())
            data = response.json()
            
            context = {
                'person': data,
                'path': path_for_img,
                'known_for_movie': known_for_movie,
            }
            return render (request, self.template_name, context)
        
    def data_each_movie(self, pk):
        url_movie = f'https://api.themoviedb.org/3/movie/{pk}?language=en-US&api_key={api_key}'
        response_movie = requests.get(url_movie)
        data_movie = response_movie.json()
        return data_movie

class DescriptionMovie(View): 
    template_name ='moviedb/desc.html'

    def get_queryset(self):
        pk = self.kwargs.get('pk')
        url = f'https://api.themoviedb.org/3/movie/{pk}?language=en-US&api_key={api_key}'
        return url

    def get(self, request, pk):
        response = requests.get(self.get_queryset())
        data = response.json()

        filled_stars = [v + 1 for v in range(int(data['vote_average']))]
        stars = 10 - int(data['vote_average'])
        empty_stars = [v + 1 for v in range(stars)]

        data_countrys = data['production_countries']
        countrys = map(lambda d: d['name'], data_countrys)
        list_country = list(countrys)
        result_country = self.clean_data(list_country)

        data_companies = data['production_companies']
        companies = map(lambda d: d['name'], data_companies)
        list_companies = list(companies)
        result_companys = self.clean_data(list_companies)

        data_genres = data['genres']
        genres = map(lambda d: d['name'], data_genres)
        list_genres = list(genres)
        result_genres = self.clean_data(list_genres)

        context = {'d' : data, 
                   'path' : path_for_img, 
                   'filled_stars' : filled_stars, 
                   'empty_stars' : empty_stars, 
                   'country' : result_country, 
                   'companys' : result_companys, 
                   'genres' : result_genres, 
                   'budget' : self.count_money(str(data['budget'])), 
                   'revenue' : self.count_money(str(data['revenue']))
        }

        return render(request, self.template_name, context)

    def clean_data(self, data):
        result = ''
        for d in data:
            if data.index(d) == len(data)-1:
                result += d
            else:
                result += d + ', '
        return result

    def count_money(self, sum):
        res = ''
        counter = 0
        for i in sum[::-1]:
            res += i
            counter += 1
            if counter%3 == 0 and sum.index(i) != 0:
                res += '.'
                counter = 0

        return res[::-1]



def filter_movies(request, page):
    if request.GET.get("button") == 'reset':
        request.session['select_genres'] = []
        request.session['select_year'] = ''
        request.session['select_sort'] = ''

    if request.GET.getlist('genres') and request.session['select_genres']:
        s = request.session.get('select_genres', [])
        q = request.GET.getlist('genres')
        for i in q:
            if i in s:
                s.remove(i)
            else:
                s.append(i)
 
        select_genres = s
        request.session['select_genres'] = select_genres
    elif request.GET.getlist('genres'):
        select_genres = request.GET.getlist('genres')
        request.session['select_genres'] = select_genres
    else:
        select_genres = request.session.get('select_genres', [])


    select_g = map(lambda x: int(x), select_genres)
    select_g = list(select_g)

    genre = ''
    for i in select_genres:
        genre += i + ','

    genre = genre[:-1]

    url_genres = f'https://api.themoviedb.org/3/genre/movie/list?api_key={api_key}'
    response = requests.get(url_genres)
    data = response.json()

    url = f'https://api.themoviedb.org/3/discover/movie?language=en-US&with_genres={genre}&page={page}'   

    if request.method == 'GET' and request.GET.get('year'):
        year = request.GET.get('year')
        request.session['select_year'] = year
        if year == 'none':
            url += '&primary_release_year=' 
        else:
            url += '&primary_release_year=' + str(request.GET.get('year'))
    else:
        year = request.session.get('select_year', '')
        url += '&primary_release_year=' + str(year)

    if request.method == 'GET' and request.GET.get('sort'):
        sort = request.GET.get('sort')
        if sort == 'none':
            request.session['select_sort'] = sort
            url += '&sort_by=popularity.desc'
        else: 
            request.session['select_sort'] = sort
            url += '&sort_by=' + request.GET.get('sort') + '.desc'
    elif not request.session['select_sort']: 
        url += '&sort_by=popularity.desc'
    else:
        sort = request.session.get('select_sort')
        url += '&sort_by=' + sort + '.desc'

    relevant_sort_list = {
        "primary_release_date" : 'Release date',
        "popularity" : 'Popularity',
        "vote_count" : 'Votes count',
        "revenue" : 'Revenue',
        'none' : None
    }

    if not request.session['select_sort']:
        selected_sort = 0
    else:
        selected_sort = relevant_sort_list[sort]


    years = [i for i in range(2025, 1915, -1)]


    return render(request, "moviedb/allmovie_list.html", {"movies": index(url)[0], 'totalPages':index(url)[1], 'number_page' : index(url)[2],  'genres' : data['genres'],
                                                          'path' : path_for_img, 'page_name': 'filter', 'select_genres' : select_g,
                                                          'select_year' : year, 'select_sort' : selected_sort, 'years' : years})




