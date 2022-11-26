class RoleType:
    ACTOR = 'actor'
    WRITER = 'writer'
    DIRECTOR = 'director'


FW_UPDATE_KEY = 'fw_date'
PERSONS_UPDATE_KEY = 'p_date'
GENRES_UPDATE_KEY = 'g_date'
DATA_COUNT_KEY = 'data_count'

FW_SQL = '''
            SELECT
               fw.id,
               fw.title,
               fw.description,
               fw.rating as imdb_rating,
               fw.type as fw_type,
               fw.modified,
               COALESCE (
                   json_agg(
                       DISTINCT jsonb_build_object(
                           'role', pfw.role,
                           'id', p.id,
                           'name', p.full_name
                       )
                   ) FILTER (WHERE p.id is not null),
                   '[]'
               ) as persons,
                COALESCE (
                   json_agg(
                       DISTINCT jsonb_build_object(
                            'id', g.id,
                            'name', g.name
                       )
                    ) FILTER (WHERE g.id is not null),
                   '[]'
               ) as genres
            FROM content.film_work fw
            LEFT JOIN content.person_film_work pfw ON pfw.film_work_id = fw.id
            LEFT JOIN content.person p ON p.id = pfw.person_id
            LEFT JOIN content.genre_film_work gfw ON gfw.film_work_id = fw.id
            LEFT JOIN content.genre g ON g.id = gfw.genre_id
            WHERE fw.modified >= '{0}'
            GROUP BY fw.id
            ORDER BY fw.modified
    '''

FILMWORK_SQL = '''
   SELECT fw.id, fw.modified
        FROM content.film_work fw
        WHERE (fw.modified >= '{0}')
        ORDER BY fw.modified
        '''

ENRICH_SQL = '''
            SELECT
               fw.id,
               fw.title,
               fw.description,
               fw.rating as imdb_rating,
               fw.type as fw_type,
               fw.modified,
               COALESCE (
                   json_agg(
                       DISTINCT jsonb_build_object(
                           'role', pfw.role,
                           'id', p.id,
                           'name', p.full_name
                       )
                   ) FILTER (WHERE p.id is not null),
                   '[]'
               ) as persons,
                COALESCE (
                   json_agg(
                       DISTINCT jsonb_build_object(
                            'id', g.id,
                            'name', g.name
                       )
                    ) FILTER (WHERE g.id is not null),
                   '[]'
               ) as genres
            FROM content.film_work fw
            LEFT JOIN content.person_film_work pfw ON pfw.film_work_id = fw.id
            LEFT JOIN content.person p ON p.id = pfw.person_id
            LEFT JOIN content.genre_film_work gfw ON gfw.film_work_id = fw.id
            LEFT JOIN content.genre g ON g.id = gfw.genre_id
            WHERE fw.id IN %s
            GROUP BY fw.id
        '''

PERSON_SQL = '''
        SELECT fw.id, p.modified
        FROM content.person p
        left join content.person_film_work pfw ON pfw.person_id = p.id
        left join content.film_work fw on pfw.film_work_id = fw.id
        WHERE (p.modified >= '{0}') and (fw.modified < '{1}') and (p.modified > fw.modified)
        ORDER BY p.modified
        '''

GENRE_SQL = '''
           SELECT
               fw.id, g.modified
           FROM content.genre g
           LEFT JOIN content.genre_film_work gfw ON gfw.genre_id = g.id
           LEFT JOIN content.film_work fw ON gfw.film_work_id = fw.id
           WHERE (g.modified >= '{0}') AND (fw.modified < '{1}') AND (g.modified > fw.modified)
           ORDER BY g.modified
       '''
