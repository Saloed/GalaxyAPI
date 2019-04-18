import re

import sqlparse


class SqlQuery:
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
