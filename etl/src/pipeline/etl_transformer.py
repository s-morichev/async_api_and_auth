from typing import Iterator

from core import etl_logger
from core.constants import RoleType
from pipeline.data_classes import ESData, Person, PersonWithRole, PGData
from pipeline.etl_pipeline import Transformer

logger = etl_logger.get_logger(__name__)


class ETLTransformer(Transformer):
    def transform_data(self, db_data: Iterator[PGData]) -> Iterator[ESData]:
        def filter_persons(lst_persons: list[PersonWithRole], role: RoleType) -> (list[Person], list[str]):
            """
            function return list of Person and list with persons names
            all persons of the role
            """
            persons_with_role = [
                Person(id=person.id, name=person.name) for person in lst_persons if person.role == role
            ]
            persons_names = [person.name for person in persons_with_role]
            return persons_with_role, persons_names

        for row in db_data:
            persons = row.persons
            ex_data = {}
            ex_data["genre"] = [genre.name for genre in row.genres]
            ex_data["mark"] = [mark.name for mark in row.marks]
            ex_data["actors"], ex_data["actors_names"] = filter_persons(persons, RoleType.ACTOR)
            ex_data["writers"], ex_data["writers_names"] = filter_persons(persons, RoleType.WRITER)
            ex_data["directors"], ex_data["directors_names"] = filter_persons(persons, RoleType.DIRECTOR)

            es_data = ESData(**(row.dict() | ex_data))
            yield es_data
