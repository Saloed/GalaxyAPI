import pytest
from django.db import connections

from api.command_generator import CommandGenerator
from api.description_utils import get_sql_from_file
from desccriptions.fins import Fins
from desccriptions.students_rup import StudentRup


@pytest.mark.django_db
def test_description_only_field():
    fins = Fins()
    sql = get_sql_from_file('..\\queries\\fins.sql')
    generator = CommandGenerator(fins, sql)
    with connections['galaxy_db'].cursor() as cursor:
        res = generator.run(cursor, [])
        print(res)
        assert len(res) > 0 and res[0].keys() == fins.fields.keys()


@pytest.mark.django_db
def test_description_field_and_required_param():
    student_rup = StudentRup()
    sql = get_sql_from_file('..\\queries\\students_rup.sql')
    generator = CommandGenerator(student_rup, sql)
    with connections['galaxy_db'].cursor() as cursor:
        res = generator.run(cursor, [111])
        print(res)
    # assert False
