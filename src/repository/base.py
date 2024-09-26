from abc import ABC, abstractmethod


class statisticsRepository(ABC):
    @abstractmethod
    def get_number_of_rows(self, table_name:str) -> int:
        """Return the number of rows."""


class customerRepository(ABC):
    @abstractmethod
    def get_customer_name(self, customer_id: int) -> str:
        """Return the name of customer."""