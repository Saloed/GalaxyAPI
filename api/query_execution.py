import hashlib
import os
import re
from typing import Union, List, Dict, Any

import sqlparse
from django.conf import settings
from django.db import connections
from django.utils import encoding
from django.core.cache import cache


class Query:
    def __init__(self, name: str):
        self.name = name


class Param:
    def __init__(self, name: str, condition: str, value: Union[str, int]):
        self.name = name
        self.condition = condition
        self.value = value

    def get_value(self):
        substitution_count = len(re.findall('(%s)', self.condition))
        return [self.value] * substitution_count


class RequiredParam:
    def __init__(self, name: str, value: Union[str, int]):
        self.name = name
        self.value = value

    def get_value(self):
        return [self.value]


class Page:
    def __init__(self, pagination_key: str, size: int, number: int):
        self.pagination_key = pagination_key
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

    @staticmethod
    def _fix_percents_signs(query):
        query_text = query.replace('%s', '<$parameter_placeholder$>')
        query_text = query_text.replace('%', '%%')
        query_text = query_text.replace('<$parameter_placeholder$>', '%s')
        return query_text

    def execute(self, required_params, params):
        sql = self._fix_percents_signs(self.sql)
        with connections['galaxy_db'].cursor() as cursor:
            cursor.execute(sql, required_params + params)
            columns = [col[0] for col in cursor.description]
            return [
                dict(zip(columns, row))
                for row in cursor.fetchall()
            ]


def _generate_cache_key(query: Query, required_params: List[RequiredParam], params: List[Param], page: Page):
    required_params_key = ','.join([f'{param.name}:{param.value}' for param in required_params])
    params_key = ','.join([f'{param.name}:{param.value}' for param in params])
    page_key = page and f'{page.pagination_key}:{page.size}:{page.number}'
    key = f'{query.name}| rp {required_params_key}| p {params_key}| pg {page_key}'
    key_hash = hashlib.sha256(encoding.force_bytes(key))
    digest = key_hash.hexdigest()
    return f'galaxy.api.query.{digest}'


def _get_param_values(params):
    return [
        value
        for param in params
        for value in param.get_value()
    ]


def _execute_query(
        query: Query, required_params: List[RequiredParam], params: List[Param], page: Page
) -> List[Dict[str, Any]]:
    with open(os.path.join(settings.QUERIES_DIR, 'sql', query.name), encoding='utf8') as sql_file:
        query_text = ''.join(sql_file.readlines())
    sql_query = _SqlQuery(query_text)
    required_params_count = sql_query.count_required_params()
    if required_params_count != len(required_params):
        error_msg = f'Not enough required params for query {query.name}: ' \
            f'expected {required_params_count} actual {len(required_params)}'
        raise ValueError(error_msg)

    if sql_query.may_apply_filters() and params:
        sql_query.add_filters([param.condition for param in params])

    if page is not None:
        sql_query.paginate(page.pagination_key, page.size, page.number)

    required_param_values = _get_param_values(required_params)
    param_values = _get_param_values(params)
    return sql_query.execute(required_param_values, param_values)


def execute_query(
        query: Query, required_params: List[RequiredParam], params: List[Param], page: Page
) -> List[Dict[str, Any]]:
    key = _generate_cache_key(query, required_params, params, page)
    cached_result = cache.get(key)
    if cached_result:
        return cached_result
    result = _execute_query(query, required_params, params, page)
    cache.set(key, result, settings.SQL_QUERY_CACHE_TIMEOUT_SECONDS)
    return result
