from .config import Config
from .repository.statistics.postgres import PostgresStatisticsRepository

def get_statistics_repository(config: Config) -> PostgresStatisticsRepository:
    return PostgresStatisticsRepository(config)