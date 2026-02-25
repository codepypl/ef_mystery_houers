"""
Klasa do obsługi bazy danych z centralnym loggerem
"""
import time
import pandas as pd
from bs4 import BeautifulSoup
from sqlalchemy import create_engine, text
from pathlib import Path
from utils.logger import get_database_logger
from config import get_database_config


class Database:
    """Klasa do obsługi bazy danych PostgreSQL"""
    
    def __init__(self, url_link: str = None):
        """
        Inicjalizacja klasy Database
        
        Args:
            url_link: URL połączenia z bazą danych
        """
        database_config = get_database_config()
        self.url_link = url_link or database_config['url']
        self.engine = None
        self.connection = None
        self.logger = get_database_logger()
        
        if not self.url_link:
            raise ValueError("URL bazy danych jest wymagany")
    
    def connect(self) -> bool:
        """
        Łączy z bazą danych
        
        Returns:
            bool: True jeśli połączenie udane, False w przeciwnym razie
        """
        try:
            self.logger.info("Łączenie z bazą danych...")
            self.engine = create_engine(self.url_link)
            self.connection = self.engine.connect()
            self.logger.info("Połączono z bazą danych")
            return True
        except Exception as e:
            self.logger.error(f"Nie udało się połączyć z bazą danych: {str(e)}")
            return False
    
    def disconnect(self) -> None:
        """Rozłącza z bazą danych"""
        try:
            if self.connection:
                self.connection.close()
            if self.engine:
                self.engine.dispose()
            self.logger.info("Rozłączono z bazą danych")
        except Exception as e:
            self.logger.error(f"Błąd podczas rozłączania z bazą danych: {str(e)}")
    
    def execute_sql(self, sql_query: str, params: dict = None) -> pd.DataFrame:
        """
        Wykonuje zapytanie SQL
        
        Args:
            sql_query: Zapytanie SQL
            params: Parametry zapytania
            
        Returns:
            pd.DataFrame: Wynik zapytania
        """
        try:
            start_time = time.time()
            query = text(sql_query)
            result = pd.read_sql(query, self.connection, params=params)
            elapsed_time = time.time() - start_time
            
            self.logger.info(f"Zapytanie wykonano w {elapsed_time:.2f} sekund")
            return result
        except Exception as e:
            self.logger.error(f"Błąd wykonania zapytania SQL: {str(e)}")
            self.logger.error(f"Zapytanie: {sql_query}")
            raise
    
    def execute_sql_from_file(self, file_path: str, params: dict = None) -> pd.DataFrame:
        """
        Wykonuje zapytanie SQL z pliku
        
        Args:
            file_path: Ścieżka do pliku SQL
            params: Parametry zapytania
            
        Returns:
            pd.DataFrame: Wynik zapytania
        """
        try:
            file_path = Path(file_path)
            if not file_path.exists():
                raise FileNotFoundError(f"Plik SQL nie istnieje: {file_path}")
                
            with open(file_path, 'r', encoding='utf-8') as file:
                sql_query = file.read()
            
            return self.execute_sql(sql_query, params)
        except Exception as e:
            self.logger.error(f"Błąd wykonania zapytania z pliku {file_path}: {str(e)}")
            raise
    
    def save_to_excel(self, data_frame: pd.DataFrame, file_path: str) -> None:
        """
        Zapisuje DataFrame do pliku Excel
        
        Args:
            data_frame: DataFrame do zapisania
            file_path: Ścieżka do pliku Excel
        """
        try:
            start_time = time.time()
            
            # Utwórz katalog jeśli nie istnieje
            file_path = Path(file_path)
            file_path.parent.mkdir(parents=True, exist_ok=True)
            
            data_frame.to_excel(file_path, index=False)
            elapsed_time = time.time() - start_time
            
            self.logger.info(f"Zapisano do Excel {file_path} w {elapsed_time:.2f} sekund")
        except Exception as e:
            self.logger.error(f"Błąd zapisu do Excel {file_path}: {str(e)}")
            raise
    
    def remove_tags(self, text: str) -> str:
        """
        Usuwa tagi HTML z tekstu zapytania SQL
        
        Args:
            text: Tekst z tagami HTML
            
        Returns:
            str: Tekst bez tagów HTML
        """
        try:
            soup = BeautifulSoup(text, 'html.parser')
            query_elem = soup.find('query')
            
            if query_elem is not None and 'value' in query_elem.attrs:
                result = query_elem['value']
                self.logger.debug("Usunięto tagi HTML z zapytania SQL")
                return result
            else:
                self.logger.warning("Nie znaleziono elementu Query lub element nie ma wartości")
                return text
        except Exception as e:
            self.logger.error(f"Błąd podczas usuwania tagów HTML: {str(e)}")
            return text
    
    def __enter__(self):
        """Context manager entry"""
        self.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.disconnect() 