from django.shortcuts import render
import requests
import re
from decouple import config

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


def popmovies(request, page):
    url = f"https://api.themoviedb.org/3/movie/popular?language=en-US&page={page}"
    return render(request, "moviedb/movie_list.html", {"movies": index(url)[0], 'totalPages':index(url)[1], 'number_page' : index(url)[2], 'page_name': 'Popular', 'path' : path_for_img})

def nowmovies(request, page):
    url = f"https://api.themoviedb.org/3/movie/now_playing?language=en-US&page={page}"
    return render(request, "moviedb/movie_list.html", {"movies": index(url)[0], 'totalPages':index(url)[1], 'number_page' : index(url)[2], 'page_name': 'Now watching', 'path' : path_for_img})

def topmovies(request, page):
    url = f"https://api.themoviedb.org/3/movie/top_rated?language=en-US&page={page}"
    return render(request, "moviedb/movie_list.html", {"movies": index(url)[0], 'totalPages':index(url)[1], 'number_page' : index(url)[2], 'page_name': 'Top rated', 'path' : path_for_img})

def poppeople(request, page):
    url = f"https://api.themoviedb.org/3/person/popular?language=en-US&page={page}"
    return render(request, "moviedb/person_list.html", {"person": index(url)[0], 'totalPages':index(url)[1], 'number_page' : index(url)[2],
                                                         'page_name': 'people', 'path' : path_for_img})

def descripperson(request, pk):
    url = f'https://api.themoviedb.org/3/person/{pk}?api_key={api_key}'
    response = requests.get(url)
    data = response.json()

    if request.method == 'POST':
        known_for = request.POST.get('known_for')
        
        pattern = r"'id': (\d+)"
        matches = re.findall(pattern, known_for)
        id_list = [int(match) for match in matches]

    known_for_movie = []
    def data_each_movie(pk):
        url_movie = f'https://api.themoviedb.org/3/movie/{pk}?language=en-US&api_key={api_key}'
        response_movie = requests.get(url_movie)
        data_movie = response_movie.json()

        return data_movie

    
    for id in id_list:
        result = data_each_movie(id)
        if len(result) > 3:
            known_for_movie.append({'id_movie' : id, 'title' : result['title'], 'poster_path' : result['poster_path']})

    return render(request, 'moviedb/descripperson.html', {'person' : data, 'path' : path_for_img, 'known_for_movie' : known_for_movie })

def search_movie(request, page):
    if request.GET.get('search_form_movie'): 
        query = request.GET.get('search_form_movie') 
        request.session['search_form_movie'] = request.GET.get('search_form_movie')
    else:
        query = request.session.get('search_form_movie') 

    url = f"https://api.themoviedb.org/3/search/movie?query={query}&include_adult=false&language=en-US&page={page}"
    print(url)
    return render(request, 'moviedb/allmovie_list.html', {'movies' : index(url)[0], 'totalPages':index(url)[1], 'number_page' : index(url)[2], 'page_name': 'search_movie', 'path' : path_for_img})

def search_person(request, page):
    if request.GET.get('search_form_person'): 
        query = request.GET.get('search_form_person') 
        request.session['search_form_person'] = request.GET.get('search_form_person')
    else:
        query = request.session.get('search_form_person') 

    url = f"https://api.themoviedb.org/3/search/person?query={query}&include_adult=false&language=en-US&page={page}"
    print(url)
    return render(request, 'moviedb/person_list.html', {'person' : index(url)[0], 'totalPages':index(url)[1], 'number_page' : index(url)[2], 'page_name': 'search_person', 'path' : path_for_img})

def all_movies(request, page=1):
    request.session['select_genres'] = []
    request.session['select_year'] = ''
    request.session['select_sort'] = ''
    request.session['search_form_movies'] = ''
    request.session['search_form_person'] = ''

    years = [i for i in range(2025, 1915, -1)]


    url = f'https://api.themoviedb.org/3/discover/movie?language=en-US&page={page}'
    url_genres = f'https://api.themoviedb.org/3/genre/movie/list?api_key={api_key}'
    response = requests.get(url_genres)
    data = response.json()
    return render(request, "moviedb/allmovie_list.html", {"movies": index(url)[0], 'totalPages':index(url)[1], 'page_name': 'home',
                                                          'genres' : data['genres'], 'path' : path_for_img, 'number_page' : index(url)[2],
                                                          'years' : years, 'what' : 'movies'})

def descrip(request, pk):
    url = f'https://api.themoviedb.org/3/movie/{pk}?language=en-US&api_key={api_key}'
    response = requests.get(url)
    data = response.json()

    filled_stars = [v + 1 for v in range(int(data['vote_average']))]
    stars = 10 - int(data['vote_average'])
    empty_stars = [v + 1 for v in range(stars)]

    def clean_data(data):
        result = ''
        for d in data:
            if data.index(d) == len(data)-1:
                result += d
            else:
                result += d + ', '
        return result

    data_countrys = data['production_countries']
    countrys = map(lambda d: d['name'], data_countrys)
    list_country = list(countrys)
    result_country = clean_data(list_country)

    data_companies = data['production_companies']
    companies = map(lambda d: d['name'], data_companies)
    list_companies = list(companies)
    result_companys = clean_data(list_companies)
    
    data_genres = data['genres']
    genres = map(lambda d: d['name'], data_genres)
    list_genres = list(genres)
    result_genres = clean_data(list_genres)

    def count_money(sum):
        res = ''
        counter = 0
        for i in sum[::-1]:
            res += i
            counter += 1
            if counter%3 == 0 and sum.index(i) != 0:
                res += '.'
                counter = 0

        return res[::-1]

    
    return render(request, 'moviedb/desc.html', {'d' : data, 'path' : path_for_img, 'filled_stars' : filled_stars,
                                                'empty_stars' : empty_stars, 'country' : result_country,
                                                'companys' : result_companys, 'genres' : result_genres,
                                                'budget' : count_money(str(data['budget'])),
                                                'revenue' : count_money(str(data['revenue']))})

def cast_list(request, pk):
    cast = f'https://api.themoviedb.org/3/movie/{pk}/credits?api_key={api_key}'
    response_cast = requests.get(cast)
    data_cast = response_cast.json()

    return render(request, 'moviedb/cast_list.html', {'cast' : data_cast['cast'], 'pk' : pk, 'path' : path_for_img})

def similar_movies(request, pk):
    sim_movie = f'https://api.themoviedb.org/3/movie/{pk}/similar?api_key={api_key}'
    response_sim = requests.get(sim_movie)
    data_sim = response_sim.json()
    sim_movie = data_sim.get("results", [])

    
    return render(request, 'moviedb/similar_movie.html', {'movies' : sim_movie,  'pk' : pk, 'path' : path_for_img})
    

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
        url += '&primary_release_year=' + str(request.GET.get('year'))
    else:
        year = request.session.get('select_year', '')
        url += '&primary_release_year=' + str(year)

    if request.method == 'GET' and request.GET.get('sort'):
        sort = request.GET.get('sort')
        request.session['select_sort'] = sort
        url += '&sort_by=' + request.GET.get('sort') + '.desc'
    elif not request.session['select_sort']: 
        url += '&sort_by=popularity.desc'
    else:
        sort = request.session.get('select_sort')
        url += '&sort_by=' + sort + '.desc'

    # print(url)

    relevant_sort_list = {
        "primary_release_date" : 'Release date',
        "popularity" : 'Popularity',
        "vote_count" : 'Votes count',
        "revenue" : 'Revenue',
    }

    if not request.session['select_sort']:
        selected_sort = 0
    else:
        selected_sort = relevant_sort_list[sort]


    years = [i for i in range(2025, 1915, -1)]


    return render(request, "moviedb/allmovie_list.html", {"movies": index(url)[0], 'totalPages':index(url)[1], 'genres' : data['genres'],
                                                          'path' : path_for_img, 'page_name': 'filter', 'select_genres' : select_g,
                                                          'select_year' : year, 'select_sort' : selected_sort, 'years' : years})




