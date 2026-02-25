"""
Moduł debugowania z użyciem icecream
"""
from icecream import ic
from typing import Any, Dict, List, Optional
from config import get_config, validate_environment, get_missing_variables


def debug_config() -> None:
    """
    Debuguje konfigurację aplikacji
    """
    ic("=== Debugowanie konfiguracji ===")
    
    # Sprawdź walidację środowiska
    is_valid = validate_environment()
    ic("Walidacja środowiska:", is_valid)
    
    if not is_valid:
        missing = get_missing_variables()
        ic("Brakujące zmienne:", missing)
    
    # Pobierz konfigurację
    config = get_config()
    ic("Ścieżka projektu:", config.project_root)
    ic("Katalog temp:", config.temp_dir)
    ic("Katalog logów:", config.logs_dir)
    
    # Sprawdź czy katalogi istnieją
    ic("Temp istnieje:", config.temp_dir.exists())
    ic("Logs istnieje:", config.logs_dir.exists())
    
    # Informacje o projekcie
    project_info = config.get_project_info()
    ic("Nazwa projektu:", project_info.get('name'))
    ic("Wersja:", project_info.get('version'))
    ic("Opis:", project_info.get('description'))


def debug_database_config() -> None:
    """
    Debuguje konfigurację bazy danych
    """
    ic("=== Debugowanie konfiguracji bazy danych ===")
    
    from config import get_database_config
    db_config = get_database_config()
    ic("URL bazy danych:", db_config.get('url'))


def debug_ms_graph_config() -> None:
    """
    Debuguje konfigurację Microsoft Graph
    """
    ic("=== Debugowanie konfiguracji Microsoft Graph ===")
    
    from config import get_microsoft_graph_config
    ms_config = get_microsoft_graph_config()
    
    # Ukryj wrażliwe dane
    safe_config = {
        'client_id': ms_config.get('client_id', '')[:8] + '...' if ms_config.get('client_id') else None,
        'tenant_id': ms_config.get('tenant_id', '')[:8] + '...' if ms_config.get('tenant_id') else None,
        'username': ms_config.get('username', '')[:8] + '...' if ms_config.get('username') else None,
        'client_secret': '***HIDDEN***' if ms_config.get('client_secret') else None,
        'password': '***HIDDEN***' if ms_config.get('password') else None,
    }
    
    ic("Konfiguracja MS Graph:", safe_config)


def debug_email_config() -> None:
    """
    Debuguje konfigurację email
    """
    ic("=== Debugowanie konfiguracji email ===")
    
    from config import get_email_config
    email_config = get_email_config()
    ic("Odbiorcy:", email_config.get('recipients'))


def debug_logging_config() -> None:
    """
    Debuguje konfigurację logowania
    """
    ic("=== Debugowanie konfiguracji logowania ===")
    
    from config import get_logging_config
    logging_config = get_logging_config()
    ic("Poziom logowania:", logging_config.get('level'))
    ic("Format:", logging_config.get('format'))
    ic("Plik app:", logging_config.get('file_app'))
    ic("Plik mail:", logging_config.get('file_mail'))
    ic("Plik structure:", logging_config.get('file_structure'))
    ic("Plik error:", logging_config.get('file_error'))


def debug_log_files() -> None:
    """
    Debuguje pliki logów
    """
    ic("=== Debugowanie plików logów ===")
    
    from config import get_config
    config = get_config()
    
    # Sprawdź czy pliki logów istnieją
    log_files = [
        config.logs_dir / "app.log",
        config.logs_dir / "mail.log", 
        config.logs_dir / "structure.log",
        config.logs_dir / "err.log"
    ]
    
    for log_file in log_files:
        if log_file.exists():
            size = log_file.stat().st_size
            ic(f"Plik {log_file.name} istnieje, rozmiar: {size} bajtów")
        else:
            ic(f"Plik {log_file.name} nie istnieje")


def debug_all() -> None:
    """
    Debuguje całą konfigurację
    """
    ic("🚀 Rozpoczęcie debugowania konfiguracji EF Produce Raport")
    
    debug_config()
    debug_database_config()
    debug_ms_graph_config()
    debug_email_config()
    debug_logging_config()
    debug_log_files()
    
    ic("✅ Debugowanie zakończone")


if __name__ == "__main__":
    debug_all() 