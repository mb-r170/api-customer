from src.utils.db.postgres import QueryRunner
import pytest


@pytest.fixture
def query_runner():
    config = {
        "DB_NAME": "business",
        "DB_USER": "postgres",
        "DB_HOST": "localhost",
        "DB_PASSWORD": "thepassword",
        "DB_PORT": 5432,
    }
    return QueryRunner(config)


def test_query_runner_execute_query(query_runner):
    query = "SELECT 1;"
    result = query_runner.execute_query(query)
    # Convert RealDictRow to tuple
    result_as_tuples = [tuple(row.values()) for row in result]

    assert result_as_tuples == [(1,)]
