CREATE SCHEMA IF NOT EXISTS content; 

ALTER ROLE app SET search_path TO content, public;

CREATE TABLE IF NOT EXISTS content.film_work (
    id uuid PRIMARY KEY,
    title TEXT NOT NULL,
    description TEXT,
    creation_date DATE,
    rating FLOAT,
    age_limit integer,
    type TEXT not null,
    created timestamp with time zone,
    modified timestamp with time zone
); 
CREATE TABLE IF NOT EXISTS content.genre (
    id uuid PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT,
    created timestamp with time zone,
    modified timestamp with time zone
); 

CREATE TABLE IF NOT EXISTS content.person (
    id uuid PRIMARY KEY,
    full_name TEXT NOT NULL,
    created timestamp with time zone,
    modified timestamp with time zone
);

CREATE TABLE IF NOT EXISTS content.genre_film_work (
    id uuid PRIMARY KEY,
    genre_id uuid NOT NULL REFERENCES content.genre (id) ON DELETE CASCADE,
    film_work_id uuid NOT NULL REFERENCES content.film_work (id) ON DELETE CASCADE,	
    created timestamp with time zone
);

CREATE TABLE IF NOT EXISTS content.person_film_work (
    id uuid PRIMARY KEY,
    person_id uuid NOT NULL REFERENCES content.person (id) ON DELETE CASCADE,
    film_work_id uuid NOT NULL REFERENCES content.film_work (id) ON DELETE CASCADE,
    role TEXT,    
    created timestamp with time zone
);

CREATE TABLE IF NOT EXISTS content.mark (
    id uuid PRIMARY KEY,
    name TEXT NOT NULL,
    created timestamp with time zone,
    modified timestamp with time zone
);

CREATE TABLE IF NOT EXISTS content.mark_film_work (
    id uuid PRIMARY KEY,
    mark_id uuid NOT NULL REFERENCES content.mark (id) ON DELETE CASCADE,
    film_work_id uuid NOT NULL REFERENCES content.film_work (id) ON DELETE CASCADE,
    created timestamp with time zone
);

CREATE INDEX film_work_creation_date_idx ON content.film_work(creation_date);
CREATE INDEX film_work_rating_idx ON content.film_work(rating);
CREATE INDEX film_work_modified_idx ON content.film_work(modified);
CREATE INDEX genre_modified_idx ON content.genre(modified);
CREATE INDEX person_modified_idx ON content.person(modified);
CREATE INDEX mark_modified_idx ON content.mark(modified);
CREATE UNIQUE INDEX person_film_idx ON content.person_film_work(film_work_id, person_id, role);
CREATE UNIQUE INDEX genre_film_idx ON content.genre_film_work(film_work_id, genre_id);
CREATE UNIQUE INDEX mark_film_idx ON content.mark_film_work(film_work_id, mark_id);

