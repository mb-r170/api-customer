import pytest
from src.repository.statistics.postgres import PostgresStatisticsRepository


@pytest.fixture
def test_config():
    return {
        "DB_NAME": "business",
        "DB_USER": "postgres",
        "DB_HOST": "localhost",
        "DB_PASSWORD": "thepassword",
        "DB_PORT": 5432,
    }


def test_check_table_name(test_config):
    stats_repo = PostgresStatisticsRepository(test_config)
    table_name = "business"
    assert stats_repo.check_table_name(table_name) == False


def test_get_row_count(test_config):
    stats_repo = PostgresStatisticsRepository(test_config)
    table_name = "customers"
    print(stats_repo.get_number_of_rows(table_name))
    assert stats_repo.get_number_of_rows(table_name) > 1
