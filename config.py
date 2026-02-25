"""
Centralna konfiguracja aplikacji EF Mystery Hours
"""
import os
from pathlib import Path
from typing import Optional
import tomllib


# Ładowanie zmiennych środowiskowych z pliku .env
def load_env_file():
    """Ładuje zmienne środowiskowe z pliku .env"""
    env_file = Path(__file__).parent / '.env'
    if env_file.exists():
        with open(env_file, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key] = value


# Ładuj zmienne środowiskowe przy importowaniu modułu
load_env_file()


class Config:
    """Centralna konfiguracja aplikacji EF Mystery Hours"""
    
    def __init__(self, validate_env: bool = True):
        # Ścieżki projektu
        self.project_root = Path(__file__).parent
        self.libs_dir = self.project_root / "libs"
        self.logs_dir = self.project_root / 'logs'
        self.modules_dir = self.project_root / 'modules'
        self.temp_dir = self.project_root / 'temp'
        self.utils_dir = self.project_root / 'utils'
        
        # Baza danych
        self.database_url = os.getenv('sql_link')
        
        # Microsoft Graph API
        self.app_id = os.getenv('APP_ID')
        self.client_secret = os.getenv('SECRET_APP_ID')
        self.tenant_id = os.getenv('TENANT_ID')
        self.username = os.getenv('_USER')
        self.password = os.getenv('PASSWORD')
        
        # OneDrive
        self.raporty_automatyczne_folder_id = os.getenv('RAPORTY_AUTOMATYCZNE')
        
        # E-mail
        self.recipients = os.getenv('EMAIL_RECIPIENTS', 'studiocati@efektum.pl').split(',')
        
        # Logowanie
        self.log_level = os.getenv('LOG_LEVEL', 'INFO')
        self.log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        
        # Walidacja wymaganych zmiennych (opcjonalna)
        if validate_env:
            self._validate_required_vars()
    
    def _validate_required_vars(self):
        """Sprawdza czy wszystkie wymagane zmienne są ustawione"""
        required_vars = {
            'sql_link': self.database_url,
            'APP_ID': self.app_id,
            'SECRET_APP_ID': self.client_secret,
            'TENANT_ID': self.tenant_id,
            '_USER': self.username,
            'PASSWORD': self.password,
            'RAPORTY_AUTOMATYCZNE': self.raporty_automatyczne_folder_id,
        }
        
        missing = [var for var, value in required_vars.items() if not value]
        if missing:
            raise ValueError(f"Brakujące zmienne środowiskowe: {', '.join(missing)}")
    
    def get_database_config(self) -> dict:
        """Zwraca konfigurację bazy danych"""
        return {
            'url': self.database_url
        }
    
    def get_microsoft_graph_config(self) -> dict:
        """Zwraca konfigurację dla Microsoft Graph"""
        return {
            'client_id': self.app_id,
            'client_secret': self.client_secret,
            'tenant_id': self.tenant_id,
            'username': self.username,
            'password': self.password
        }
    
    def get_email_config(self) -> dict:
        """Zwraca konfigurację e-mail"""
        return {
            'recipients': self.recipients
        }
    
    def get_logging_config(self) -> dict:
        """Zwraca konfigurację logowania"""
        return {
            'level': self.log_level,
            'format': self.log_format,
            'file_app': str(self.logs_dir / "app.log"),
            'file_mail': str(self.logs_dir / "mail.log"),
            'file_structure': str(self.logs_dir / "structure.log"),
            'file_error': str(self.logs_dir / "err.log")
        }
    
    def get_paths_config(self) -> dict:
        """Zwraca konfigurację ścieżek"""
        return {
            'temp': str(self.temp_dir),
            'logs': str(self.logs_dir),
            'program_dir': str(self.project_root),
            'raporty_automatyczne': self.raporty_automatyczne_folder_id
        }
    
    def ensure_directories(self):
        """Tworzy niezbędne katalogi"""
        self.libs_dir.mkdir(parents=True, exist_ok=True)
        self.logs_dir.mkdir(parents=True, exist_ok=True)
        self.modules_dir.mkdir(parents=True, exist_ok=True)
        self.temp_dir.mkdir(parents=True, exist_ok=True)
        self.utils_dir.mkdir(parents=True, exist_ok=True)
    
    def get_temp_file_path(self, filename: str) -> Path:
        """Zwraca ścieżkę do pliku tymczasowego"""
        return self.temp_dir / filename
    
    def get_log_file_path(self, filename: str) -> Path:
        """Zwraca ścieżkę do pliku logów"""
        return self.logs_dir / filename
    
    def get_info_log_path(self) -> Path:
        """Zwraca ścieżkę do pliku logów informacji"""
        return self.logs_dir / 'info.log'
    
    def get_error_log_path(self) -> Path:
        """Zwraca ścieżkę do pliku logów błędów"""
        return self.logs_dir / 'err.log'
    
    def get_project_info(self) -> dict:
        """Zwraca informacje o projekcie z pyproject.toml"""
        try:
            pyproject_path = self.project_root / 'pyproject.toml'
            with open(pyproject_path, 'rb') as f:
                project_data = tomllib.load(f)
            
            # Zwracamy bezpośrednio dane z pliku TOML
            project_info = project_data.get('project', {})
            
            # Dodajemy tylko dodatkowe informacje o ścieżkach
            project_info.update({
                'project_root': str(self.project_root),
                'temp_dir': str(self.temp_dir),
                'logs_dir': str(self.logs_dir),
                'info_log_path': str(self.get_info_log_path()),
                'error_log_path': str(self.get_error_log_path())
            })
            
            return project_info
            
        except (FileNotFoundError, KeyError, tomllib.TOMLDecodeError) as e:
            # W przypadku błędu zwracamy podstawowe informacje
            return {
                'name': 'ef-mystery-hours-raport',
                'version': '0.1.0',
                'description': 'System generowania raportów Mystery Hours',
                'project_root': str(self.project_root),
                'temp_dir': str(self.temp_dir),
                'logs_dir': str(self.logs_dir),
                'info_log_path': str(self.get_info_log_path()),
                'error_log_path': str(self.get_error_log_path()),
                'error': f'Błąd odczytu pyproject.toml: {str(e)}'
            }


# Instancja globalna konfiguracji (bez walidacji zmiennych środowiskowych)
config = Config(validate_env=False)


# Funkcje pomocnicze
def get_config() -> Config:
    """Zwraca instancję konfiguracji"""
    return config


def get_database_config() -> dict:
    """Zwraca konfigurację bazy danych"""
    return config.get_database_config()


def get_microsoft_graph_config() -> dict:
    """Zwraca konfigurację Microsoft Graph"""
    return config.get_microsoft_graph_config()


def get_email_config() -> dict:
    """Zwraca konfigurację e-mail"""
    return config.get_email_config()


def get_logging_config() -> dict:
    """Zwraca konfigurację logowania"""
    return config.get_logging_config()


def get_paths_config() -> dict:
    """Zwraca konfigurację ścieżek"""
    return config.get_paths_config()


def get_info_log_path() -> Path:
    """Zwraca ścieżkę do pliku logów informacji"""
    return config.get_info_log_path()


def get_error_log_path() -> Path:
    """Zwraca ścieżkę do pliku logów błędów"""
    return config.get_error_log_path()


def validate_environment() -> bool:
    """Sprawdza czy wszystkie wymagane zmienne środowiskowe są ustawione"""
    try:
        temp_config = Config(validate_env=True)
        return True
    except ValueError:
        return False


def get_missing_variables() -> list:
    """Zwraca listę brakujących zmiennych środowiskowych"""
    try:
        temp_config = Config(validate_env=True)
        return []
    except ValueError as e:
        # Wyciągnij nazwy zmiennych z komunikatu błędu
        error_msg = str(e)
        if "Brakujące zmienne środowiskowe:" in error_msg:
            missing_vars = error_msg.split("Brakujące zmienne środowiskowe: ")[1]
            return [var.strip() for var in missing_vars.split(", ")]
        return []


# Kompatybilność wsteczna - eksportujemy stare nazwy
DATABASE_URL = config.database_url
MS_GRAPH_CONFIG = config.get_microsoft_graph_config()
EMAIL_CONFIG = config.get_email_config()
LOGGING_CONFIG = config.get_logging_config()
PATHS = config.get_paths_config()

# Dodatkowe funkcje eksportowane
get_project_info = config.get_project_info
