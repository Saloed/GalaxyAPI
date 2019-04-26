import re
import sqlparse

from typing import Union, List, Dict, Any
from django.db import connections


class Query:
    def __init__(self, name: str, pagination_key: str):
        self.name = name
        self.pagination_key = pagination_key


class Param:
    def __init__(self, name: str, condition: str, value: Union[str, int]):
        self.name = name
        self.condition = condition
        self.value = value


class RequiredParam:
    def __init__(self, name: str, value: Union[str, int]):
        self.name = name
        self.value = value


class Page:
    def __init__(self, size: int, number: int):
        self.size = size
        self.number = number


class _SqlQuery:
    def __init__(self, sql):
        self.sql = sql
        self.tokens = sqlparse.parse(sql)

    def count_required_params(self):
        return len(re.findall('(%s)', self.sql))

    def may_apply_filters(self):
        if len(self.tokens) != 1 or not isinstance(self.tokens[0], sqlparse.sql.Statement):
            return False
        statement = self.tokens[0]
        if len(statement.tokens) < 1:
            return False
        first_token = statement.tokens[0]
        if first_token.ttype != sqlparse.tokens.DML or first_token.value != 'SELECT':
            return False
        return True

    def add_filters(self, filters):
        if not filters:
            return
        statement = self.tokens[0]
        where_token = statement.token_matching(lambda tk: isinstance(tk, sqlparse.sql.Where), 0)
        filter_tokens = [sqlparse.sql.Token(sqlparse.tokens.Comparison, it) for it in filters]
        and_token = sqlparse.sql.Token(sqlparse.tokens.Keyword, 'AND')
        whitespace = sqlparse.sql.Token(sqlparse.tokens.Whitespace, ' ')
        where_tk = sqlparse.sql.Token(sqlparse.tokens.Keyword, 'WHERE')

        def combine_filters_with_and(need_trailing):
            result = []
            if need_trailing:
                result += [whitespace, and_token, whitespace]

            for tk in filter_tokens[:-1]:
                result += [tk, whitespace, and_token, whitespace]

            result += [filter_tokens[-1]]
            return result

        if where_token is None:
            where_token = sqlparse.sql.Where([where_tk, whitespace] + combine_filters_with_and(False))
            statement.tokens.append(where_token)
        else:
            where_token.tokens += combine_filters_with_and(True)

        self.sql = str(statement)
        self.tokens = sqlparse.parse(self.sql)

    def paginate(self, pagination_key, page_size, page_number):
        paginated_sql = f"""SELECT * FROM (
        {self.sql}
        ) query
        ORDER BY {pagination_key}
        OFFSET {page_number * page_size} ROWS FETCH NEXT {page_size}  ROWS ONLY
        """
        self.sql = paginated_sql
        self.tokens = sqlparse.parse(paginated_sql)

    def execute(self, required_params, params):
        with connections['galaxy_db'].cursor() as cursor:
            cursor.execute(self.sql, required_params + params)
            columns = [col[0] for col in cursor.description]
            return [
                dict(zip(columns, row))
                for row in cursor.fetchall()
            ]


def execute_query(
        query: Query, required_params: List[RequiredParam], params: List[Param], page: Page
) -> List[Dict[str, Any]]:
    with open(f'queries/{query.name}', encoding='utf8') as sql_file:
        query_text = ''.join(sql_file.readlines())
    sql_query = _SqlQuery(query_text)
    required_params_count = sql_query.count_required_params()
    if required_params_count != len(required_params):
        error_msg = f'Not enough required params for query {query.name}: ' \
            f'expected {required_params_count} actual {len(required_params)}'
        raise ValueError(error_msg)

    if sql_query.may_apply_filters() and params:
        sql_query.add_filters([param.condition for param in params])

    sql_query.paginate(query.pagination_key, page.size, page.number)

    return sql_query.execute([param.value for param in required_params], [param.value for param in params])
