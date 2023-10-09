
path_for_img = 'https://image.tmdb.org/t/p/w500'


def calculate_movies_data(func, get_queryset_func, get_user_context_func, page_name):
    movies = get_user_context_func(
        movies = func(get_queryset_func())[0],
        totalPages = func(get_queryset_func())[1],
        number_page = func(get_queryset_func())[2],
        page_name = page_name,
        path = path_for_img
    )
    return movies

class DataMixin:
    def get_user_context(self, **kwargs):
        context = kwargs
        return context