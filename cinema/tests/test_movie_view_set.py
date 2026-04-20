from http import client

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status

from cinema.models import (Movie,
                           MovieSession,
                           CinemaHall,
                           Genre,
                           Actor)
from cinema.serializers import MovieSerializer, MovieSessionSerializer

MOVIE_URL = reverse("cinema:movie-list")
MOVIE_SESSION_URL = reverse("cinema:moviesession-list")


def detail_url(movie_id):
    return reverse("cinema:movie-detail", args=(movie_id, ))


def sample_movie(**params):
    defaults = {
        "title": "Sample movie",
        "description": "Sample description",
        "duration": 90,
    }
    defaults.update(params)

    return Movie.objects.create(**defaults)


def sample_genre(**params):
    defaults = {
        "name": "Drama",
    }
    defaults.update(params)

    return Genre.objects.create(**defaults)


def sample_actor(**params):
    defaults = {"first_name": "George", "last_name": "Clooney"}
    defaults.update(params)

    return Actor.objects.create(**defaults)


def sample_movie_session(**params):
    cinema_hall = CinemaHall.objects.create(name="Blue", rows=20, seats_in_row=20)

    defaults = {
        "show_time": "2022-06-02 14:00:00",
        "movie": None,
        "cinema_hall": cinema_hall,
    }
    defaults.update(params)

    return MovieSession.objects.create(**defaults)


class AuthenticateMovieApiTests(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email="test@test.test",
            password="testpassword",
        )
        self.client.force_authenticate(user=self.user)

    def test_movie_list(self):
        sample_movie()

        res = client.get(MOVIE_URL)
        movies = Movie.objects.all()
        serializer = MovieSerializer(movies, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data["results"], serializer.data)

    def test_retrive_movie_detail(self):
        movie = sample_movie()
        movie.objects.create(title="Sample movie",
                             description="Sample description",
                             duration=90)
        url = detail_url(movie.id)
        res = self.client.get(url)
        serializer = MovieSerializer(movie)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_create_movie_forbidden(self):
        payload = {"title": "Sample movie",
                   "description": "Sample description",
                   "duration": 90,
                   }
        res = self.client.post(MOVIE_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_movie(self):
        payload = {"title": "Sample movie",
                   "description": "Sample description",
                   "duration": 90,
                   }
        res = self.client.post(MOVIE_URL, payload)
        movie = Movie.objects.get(id=res.data["id"])
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        for key in payload:
            self.assertEqual(payload[key], getattr(movie, key))

    def test_delete_movie(self):
        movie = sample_movie()
        url = detail_url(movie.id)
        res = self.client.delete(url)
        self.assertEqual(res.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
