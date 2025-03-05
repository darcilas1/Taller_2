from django.shortcuts import render
from django.http import HttpResponse

from .models import Movie
import matplotlib.pyplot as plt
import matplotlib
import io
import urllib, base64


# create your views here

def home(request):
    #return HttpResponse('<h1>Welcome to Home Page</h1>')
    #return render(request, 'home.html')
    #return render(request, 'home.html', {'name':'Paola Vallejo'})
    searchTerm = request.GET.get('searchMovie')
    if searchTerm:
        movies = Movie.objects.filter(title__icontains=searchTerm)
    else:
        movies = Movie.objects.all()
    return render(request, 'home.html', {'searchTerm':searchTerm, 'movies':movies})


def about(request):
    #return HttpResponse('<h1>Welcome to About Page</h1>')
    return render(request, 'about.html')


def signup(request):
    email = request.GET.get('email')
    return render(request, 'signup.html', {'email':email})


def statistics_view(request):
    matplotlib.use('Agg')

    # ==================== Gráfica de Películas por Año ====================
    # Obtener los años de todas las películas excluyendo valores None
    years = Movie.objects.exclude(year__isnull=True).values_list('year', flat=True).distinct().order_by('year')

    # Crear un diccionario con conteo de películas por año
    movie_counts_by_year = {int(year): Movie.objects.filter(year=year).count() for year in years if year is not None}

    # Asegurar que las claves del diccionario sean listas ordenadas
    sorted_years = sorted(movie_counts_by_year.keys())

    plt.figure(figsize=(10, 5))
    plt.bar(sorted_years, [movie_counts_by_year[year] for year in sorted_years], color='skyblue')
    plt.xlabel('Año')
    plt.ylabel('Cantidad de Películas')
    plt.title('Cantidad de Películas por Año')
    plt.xticks(rotation=45, ha='right')

    # Guardar la gráfica en un objeto BytesIO
    buffer = io.BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    plt.close()

    # Convertir la imagen en base64
    image_png = buffer.getvalue()
    buffer.close()
    graphic_years = base64.b64encode(image_png).decode('utf-8')

    # ==================== Gráfica de Películas por Género ====================
    # Obtener los géneros excluyendo valores None
    genres = Movie.objects.exclude(genre__isnull=True).values_list('genre', flat=True)

    genre_counts = {}
    for genre in genres:
        if genre:
            first_genre = genre.split(',')[0].strip()  # Tomar solo el primer género
            genre_counts[first_genre] = genre_counts.get(first_genre, 0) + 1

    plt.figure(figsize=(10, 5))
    plt.bar(genre_counts.keys(), genre_counts.values(), color='lightcoral')
    plt.xlabel('Género')
    plt.ylabel('Cantidad de Películas')
    plt.title('Cantidad de Películas por Género (Primer Género)')
    plt.xticks(rotation=45, ha='right')

    # Guardar la gráfica en un objeto BytesIO
    buffer = io.BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    plt.close()

    # Convertir la imagen en base64
    image_png = buffer.getvalue()
    buffer.close()
    graphic_genres = base64.b64encode(image_png).decode('utf-8')

    # Renderizar la plantilla con ambas gráficas
    return render(request, 'statistics.html', {
        'graphic_years': graphic_years,
        'graphic_genres': graphic_genres
    })