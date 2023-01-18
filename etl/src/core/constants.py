class RoleType:
    ACTOR = "actor"
    WRITER = "writer"
    DIRECTOR = "director"


FW_UPDATE_KEY = "fw_date"
PERSONS_UPDATE_KEY = "p_date"
GENRES_UPDATE_KEY = "g_date"
MARKS_UPDATE_KEY = "m_date"

EX_PERSON_UPDATE_KEY = "persons_date"
EX_GENRE_UPDATE_KEY = "genres_date"

DATA_COUNT_KEY = "data_count"


FILMWORK_SQL = """
    SELECT fw.id AS f_id,
           fw.modified
    FROM content.film_work fw
    WHERE (fw.modified >= '{0}')
    ORDER BY fw.modified,
             fw.id
    """

ENRICH_SQL = """
    SELECT fw.id,
           fw.title,
           fw.description,
           fw.rating AS imdb_rating,
           fw.age_limit,
           fw.type AS fw_type,
           fw.modified,
           COALESCE (json_agg(DISTINCT jsonb_build_object('role', pfw.role, 'id', p.id, 'name', p.full_name))
                FILTER (WHERE p.id IS NOT NULL),
                '[]') AS persons,
           COALESCE (json_agg(DISTINCT jsonb_build_object('id', g.id, 'name', g.name))
                FILTER (WHERE g.id IS NOT NULL),
                '[]') AS genres,
           COALESCE (json_agg(DISTINCT jsonb_build_object('id', m.id, 'name', m.name))
                FILTER (WHERE m.id IS NOT NULL),
                '[]') AS marks
    FROM content.film_work fw
    LEFT JOIN content.person_film_work pfw ON pfw.film_work_id = fw.id
    LEFT JOIN content.person p ON p.id = pfw.person_id
    LEFT JOIN content.genre_film_work gfw ON gfw.film_work_id = fw.id
    LEFT JOIN content.genre g ON g.id = gfw.genre_id
    LEFT JOIN content.mark_film_work mfw ON mfw.film_work_id = fw.id
    LEFT JOIN content.mark m ON m.id = mfw.mark_id
    WHERE fw.id IN %s
    GROUP BY fw.id
    ORDER BY fw.id
    """

PERSON_SQL = """
    SELECT fw.id AS f_id,
           p.modified,
           p.id
    FROM content.person p
    LEFT JOIN content.person_film_work pfw ON pfw.person_id = p.id
    LEFT JOIN content.film_work fw ON pfw.film_work_id = fw.id
    WHERE (p.modified >= '{0}')
        AND (fw.modified < '{1}')
        AND (p.modified > fw.modified)
    ORDER BY p.modified,
             p.id
    """

GENRE_SQL = """
    SELECT fw.id AS f_id,
           g.modified,
           g.id
    FROM content.genre g
    LEFT JOIN content.genre_film_work gfw ON gfw.genre_id = g.id
    LEFT JOIN content.film_work fw ON gfw.film_work_id = fw.id
    WHERE (g.modified >= '{0}')
        AND (fw.modified < '{1}')
        AND (g.modified > fw.modified)
    ORDER BY g.modified,
             g.id
    """

MARK_SQL = """
    SELECT fw.id AS f_id,
           m.modified,
           m.id
    FROM content.mark m
    LEFT JOIN content.mark_film_work mfw ON mfw.mark_id = m.id
    LEFT JOIN content.film_work fw ON mfw.film_work_id = fw.id
    WHERE (m.modified >= '{0}')
        AND (fw.modified < '{1}')
        AND (m.modified > fw.modified)
    ORDER BY m.modified,
             m.id
    """

EX_PERSONS_SQL = """
    SELECT t.id,
           t.full_name,
           t.modified,
           COALESCE (json_agg(jsonb_build_object('role', t.role, 'movies', t.movies))
                                                    FILTER (WHERE t.role IS NOT NULL),
            '[]') AS movies
    FROM
        (SELECT p.id,
                p.full_name,
                p.modified,
                pfw.role,
                json_agg(jsonb_build_object('id', fw.id, 'title', fw.title)) AS movies
         FROM content.person p
         LEFT JOIN content.person_film_work pfw ON p.id = pfw.person_id
         LEFT JOIN content.film_work fw ON pfw.film_work_id = fw.id
         WHERE p.modified >= '{0}'
         GROUP BY p.id,
                  pfw.role) t
    GROUP BY t.id,
             t.full_name,
             t.modified
    ORDER BY t.modified,
             t.id
    """

EX_GENRES_SQL = """
    SELECT g.id,
           g.name,
           g.modified
    FROM content.genre g
    WHERE g.modified >='{0}'
    ORDER BY g.modified,
             g.id;
    """
