from ..base import statisticsRepository
from ...utils.db.postgres import QueryRunner
from ...config import Config

TABLES = ["customers", "products", "interactions"]

TABLE_COUNT_SQL = """SELECT COUNT(*) FROM {table_name}; """

class PostgresStatisticsRepository(statisticsRepository):
    def __init__(self, config: Config):
        self.runner = QueryRunner(config)

    def get_number_of_rows(self, table_name) -> int:
        """
        Return the number of content entries in the database.

        Returns:
            Tuple with the number of content entries.
        """

        result = self.runner.execute_query(TABLE_COUNT_SQL.format(table_name = table_name), return_dict=False)
        return result[0][0]
    
    def check_table_name(self, table_name) -> bool:
        return table_name in TABLES