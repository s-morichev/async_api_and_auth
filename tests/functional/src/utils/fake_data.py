import json
import random
import uuid
from pprint import pprint

from utils.dto_models import ElasticFilm, ExtendedFilm, ExtendedPerson, Film, Genre, Person, RoleMovies

# ------------------------------------------------------------------------------ #
#print = pprint
persons_count = 20
genres_count = 6
films_count = 20

person_names = [f"Person {i}" for i in range(persons_count)]
person_names[0] = "First Person"
person_names[persons_count // 2] = "Middle"
person_names[-1] = "Person Last"

film_titles = [f"Movie {i}" for i in range(films_count)]
film_titles[0] = "First film"
film_titles[films_count // 2] = "Middle movie"
film_titles[-1] = "Film Last"

genre_names = [f"Genre {i}" for i in range(genres_count)]
genre_names[0] = "First Genre"
genre_names[genres_count // 2] = "Middle"
genre_names[-1] = "Genre Last"

roles = ["actor", "writer", "director"]

genres = [Genre(id=uuid.uuid4(), name=name) for name in genre_names]
films = [Film(id=uuid.uuid4(), title=title) for title in film_titles]


def gen_roles_movies(roles, movies):
    """
    функция возвращает разбиение по случайной выборке фильмов по ролям
    :param roles:
    :param movies:
    :return:
    """

    roles_movies = []
    count = 0
    for role in roles:
        k = random.randint(0, len(movies)//2)
        count += k
        random_choice = random.sample(movies, k=k)
        if random_choice:
            roles_movies.append(RoleMovies(role=role, movies=random_choice))

    if not count:  # так получилось, что человек без фильмов
        # то добавляем для первой роли два фильма
        roles_movies.append(RoleMovies(role=roles[0], movies=random.sample(movies, k=2)))

    return roles_movies


def filter_roles(persons: list[ExtendedPerson], person_list: dict[uuid, Person]) -> dict:
    """
    создает словарь [film_id][role]=list[Person]
    по нему проще заполнять фильмы
    """
    result = {}
    for person in persons:
        for role_movies in person.movies:
            role = role_movies.role
            for film in role_movies.movies:
                film_roles = result.setdefault(film.id, {})
                film_roles.setdefault(role, []).append(person_list[person.id])

    return result


persons = [
    ExtendedPerson(id=uuid.uuid4(), full_name=name, movies=gen_roles_movies(roles, films)) for name in person_names
]

persons_list = {person.id: Person(id=person.id, full_name=person.full_name) for person in persons}
film_persons = filter_roles(persons, persons_list)

extended_films = [
    ExtendedFilm(
        id=film.id,
        title=film.title,
        genres=random.choices(genres, k=random.randint(1, len(genres))),
        description="random description",
        imdb_rating=random.randint(0, 100) / 10,
        rars_rating=random.choice([0, 6, 12, 16, 18]),
        fw_type=random.choice(["movie", "tv show"]),
        actors=film_persons[film.id].get("actor") or [],
        directors=film_persons[film.id].get("director") or [],
        writers=film_persons[film.id].get("writer") or [],
    )
    for film in films
]


elastic_films = [
    ElasticFilm(
        **film.dict(),
        genre=[genre.name for genre in film.genres],
        directors_names=[director.name for director in film.directors],
        actors_names=[actor.name for actor in film.actors],
        writers_names=[writer.name for writer in film.writers],
    )
    for film in extended_films
]


class UUIDEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, uuid.UUID):
            # if the obj is uuid, we simply return the value of uuid
            return str(obj)
        return json.JSONEncoder.default(self, obj)


data = [el.dict() for el in persons]
with open("persons.json", "w") as file:
    file.write(json.dumps(data, indent=4, cls=UUIDEncoder))
    print(f'write {file.name}')

data = [el.dict() for el in elastic_films]
with open("films.json", "w") as file:
    file.write(json.dumps(data, indent=4, cls=UUIDEncoder))
    print(f'write {file.name}')

data = [el.dict() for el in genres]
with open("genres.json", "w") as file:
    file.write(json.dumps(data, indent=4, cls=UUIDEncoder))
    print(f'write {file.name}')