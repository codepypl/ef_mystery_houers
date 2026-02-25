"""
Centralny logger dla aplikacji
"""
import logging
import logging.handlers
from pathlib import Path
from config import get_logging_config, get_paths_config, get_config


def setup_logger(name: str = "ef_produce") -> logging.Logger:
    """
    Konfiguruje i zwraca logger dla aplikacji
    
    Args:
        name: Nazwa loggera
        
    Returns:
        logging.Logger: Skonfigurowany logger
    """
    config = get_config()
    logging_config = get_logging_config()
    
    # Utwórz katalog logów jeśli nie istnieje
    config.ensure_directories()
    
    # Pobierz logger
    logger = logging.getLogger(name)
    
    # Sprawdź czy logger już ma handlery (nie duplikuj)
    if logger.handlers:
        return logger
    
    # Ustaw poziom logowania
    logger.setLevel(getattr(logging, logging_config["level"]))
    
    # Formatter
    formatter = logging.Formatter(logging_config["format"])
    
    # Handler dla pliku app.log (główne logi aplikacji)
    app_handler = logging.handlers.RotatingFileHandler(
        logging_config["file_app"],
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5
    )
    app_handler.setLevel(logging.INFO)
    app_handler.setFormatter(formatter)
    
    # Handler dla pliku err.log (błędy)
    error_handler = logging.handlers.RotatingFileHandler(
        logging_config["file_error"],
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(formatter)
    
    # Handler dla konsoli
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    
    # Dodaj handlery do loggera
    logger.addHandler(app_handler)
    logger.addHandler(error_handler)
    logger.addHandler(console_handler)
    
    return logger


def get_logger(name: str = "ef_produce") -> logging.Logger:
    """
    Zwraca logger dla podanej nazwy
    
    Args:
        name: Nazwa loggera
        
    Returns:
        logging.Logger: Logger
    """
    return logging.getLogger(name)


def get_mail_logger() -> logging.Logger:
    """
    Zwraca logger specjalnie dla operacji email
    
    Returns:
        logging.Logger: Logger dla email
    """
    config = get_config()
    logging_config = get_logging_config()
    
    # Utwórz katalog logów jeśli nie istnieje
    config.ensure_directories()
    
    # Pobierz logger
    logger = logging.getLogger("mail")
    
    # Sprawdź czy logger już ma handlery (nie duplikuj)
    if logger.handlers:
        return logger
    
    # Ustaw poziom logowania
    logger.setLevel(getattr(logging, logging_config["level"]))
    
    # Formatter
    formatter = logging.Formatter(logging_config["format"])
    
    # Handler dla pliku mail.log
    mail_handler = logging.handlers.RotatingFileHandler(
        logging_config["file_mail"],
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5
    )
    mail_handler.setLevel(logging.INFO)
    mail_handler.setFormatter(formatter)
    
    # Handler dla pliku err.log (błędy email)
    error_handler = logging.handlers.RotatingFileHandler(
        logging_config["file_error"],
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(formatter)
    
    # Handler dla konsoli
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    
    # Dodaj handlery do loggera
    logger.addHandler(mail_handler)
    logger.addHandler(error_handler)
    logger.addHandler(console_handler)
    
    return logger


def get_structure_logger() -> logging.Logger:
    """
    Zwraca logger specjalnie dla operacji struktury OneDrive
    
    Returns:
        logging.Logger: Logger dla struktury
    """
    config = get_config()
    logging_config = get_logging_config()
    
    # Utwórz katalog logów jeśli nie istnieje
    config.ensure_directories()
    
    # Pobierz logger
    logger = logging.getLogger("structure")
    
    # Sprawdź czy logger już ma handlery (nie duplikuj)
    if logger.handlers:
        return logger
    
    # Ustaw poziom logowania
    logger.setLevel(getattr(logging, logging_config["level"]))
    
    # Formatter
    formatter = logging.Formatter(logging_config["format"])
    
    # Handler dla pliku structure.log
    structure_handler = logging.handlers.RotatingFileHandler(
        logging_config["file_structure"],
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5
    )
    structure_handler.setLevel(logging.INFO)
    structure_handler.setFormatter(formatter)
    
    # Handler dla pliku err.log (błędy struktury)
    error_handler = logging.handlers.RotatingFileHandler(
        logging_config["file_error"],
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(formatter)
    
    # Handler dla konsoli
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    
    # Dodaj handlery do loggera
    logger.addHandler(structure_handler)
    logger.addHandler(error_handler)
    logger.addHandler(console_handler)
    
    return logger


def get_database_logger() -> logging.Logger:
    """
    Zwraca logger specjalnie dla operacji bazy danych
    
    Returns:
        logging.Logger: Logger dla bazy danych
    """
    config = get_config()
    logging_config = get_logging_config()
    
    # Utwórz katalog logów jeśli nie istnieje
    config.ensure_directories()
    
    # Pobierz logger
    logger = logging.getLogger("database")
    
    # Sprawdź czy logger już ma handlery (nie duplikuj)
    if logger.handlers:
        return logger
    
    # Ustaw poziom logowania
    logger.setLevel(getattr(logging, logging_config["level"]))
    
    # Formatter
    formatter = logging.Formatter(logging_config["format"])
    
    # Handler dla pliku app.log (logi bazy danych idą do głównego pliku)
    app_handler = logging.handlers.RotatingFileHandler(
        logging_config["file_app"],
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5
    )
    app_handler.setLevel(logging.INFO)
    app_handler.setFormatter(formatter)
    
    # Handler dla pliku err.log (błędy bazy danych)
    error_handler = logging.handlers.RotatingFileHandler(
        logging_config["file_error"],
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(formatter)
    
    # Handler dla konsoli
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    
    # Dodaj handlery do loggera
    logger.addHandler(app_handler)
    logger.addHandler(error_handler)
    logger.addHandler(console_handler)
    
    return logger 