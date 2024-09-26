from typing import List, Optional

import psycopg2
import psycopg2.extras


class QueryRunner:
    def __init__(self, config: dict):
        self.db_config = self._config_to_postgres_config(config)

    def _config_to_postgres_config(self, config: dict) -> dict:
        return dict(
            database=config["DB_NAME"],
            user=config["DB_USER"],
            host=config["DB_HOST"],
            password=config["DB_PASSWORD"],
            port=config["DB_PORT"],
        )

    def _get_connection(
        self, return_dict: bool = True
    ) -> psycopg2.extensions.connection:
        # Potential improvement: use pools
        cursor_factory = psycopg2.extras.RealDictCursor if return_dict else None
        return psycopg2.connect(
            **self.db_config,
            cursor_factory=cursor_factory,
        )

    def execute_query(
        self,
        query: str,
        params: dict = None,
        fetch_one: bool = False,
        return_dict: bool = True,
    ):
        conn = self._get_connection(return_dict=return_dict)
        try:
            # This context manager only closes the transaction, not the connection
            with conn:
                with conn.cursor() as cur:
                    cur.execute(query, params)
                    return cur.fetchone() if fetch_one else cur.fetchall()
        finally:
            conn.close()

    def execute_update(
        self,
        query: str,
        params: dict = None,
        conn: Optional[psycopg2.extensions.connection] = None,
        return_cursor_fetch: bool = False,
    ) -> int:
        """Execute an insert, update or delete query

        Args:
            query: insert, update or delete SQL query
            params: named parameters to be replaced in the query.
                key: parameter name, value: parameter value.
                They should appear as `%(name)s` placeholders in the query.
            conn: connection to be reused. When given, the transaction won't be commited.
        Returns:
            If return_cursor_fetch = false, number of affected rows.
            Else, first value in first result fetched from cursor.
        """

        def _run_query(conn: psycopg2.extensions.connection):
            with conn.cursor() as cur:
                cur.execute(query, params)
                return cur.fetchone()[0] if return_cursor_fetch else cur.rowcount

        if conn is not None:
            return _run_query(conn)

        conn = self._get_connection(return_dict=False)
        try:
            # This context manager only closes the transaction, not the connection
            with conn:
                rowcount = _run_query(conn)
                conn.commit()
                return rowcount
        finally:
            conn.close()

    def execute_update_many(
        self,
        query: str,
        params_template: str,
        params: List[dict] = None,
        conn: Optional[psycopg2.extensions.connection] = None,
    ) -> int:
        """Execute an insert, update or delete query potentially affecting many rows.

        Args:
            query: insert, update or delete SQL query. It must contain a single %s placeholder,
                which will be replaced by the given `params` properly formatted.
                Example: "INSERT INTO mytable (id, f1, f2) VALUES %s"
            params_template: placeholders of expected parameters for a single query.
                Example: "(%(id)s, %(name)s, 33)", where 33 is an example constant.
            params: named parameters to be replaced in the query.
                key: parameter name, value: parameter value.
                They should appear as `%(name)s` placeholders in `params_placeholder`.
        Returns:
            number of affected rows
        """

        def _run_query(conn):
            with conn.cursor() as cur:
                psycopg2.extras.execute_values(cur, query, params, params_template)
                return cur.rowcount

        if conn is not None:
            return _run_query(conn)

        conn = self._get_connection()
        try:
            # This context manager only closes the transaction, not the connection
            with conn:
                rowcount = _run_query(conn)
                conn.commit()
                return rowcount
        finally:
            conn.close()
