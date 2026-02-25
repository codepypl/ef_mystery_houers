"""
Moduł do zarządzania strukturą folderów na OneDrive
"""
from datetime import datetime
from pathlib import Path
from utils.logger import get_structure_logger
from libs.ms_graph import MicrosoftGraph
from config import get_paths_config


def setup_folder_structure() -> dict:
    """
    Tworzy strukturę folderów na OneDrive dla raportów
    
    Returns:
        dict: Słownik z ID folderów
    """
    logger = get_structure_logger()
    
    try:
        logger.info("Inicjalizacja struktury folderów na OneDrive...")
        
        # Inicjalizacja Microsoft Graph
        graph = MicrosoftGraph()
        
        # Pobierz aktualną datę
        year = datetime.now().strftime('%Y')
        month = datetime.now().strftime('%m')
        day = datetime.now().strftime('%d')
        
        # Pobierz konfigurację ścieżek
        paths_config = get_paths_config()
        raporty_automatyczne_id = paths_config["raporty_automatyczne"]
        
        # Utwórz strukturę folderów
        logger.info("Tworzenie struktury folderów...")
        
        # Folder roku
        year_dir = graph.create_folder(year, raporty_automatyczne_id)
        y_id = graph.get_folder_id(year, raporty_automatyczne_id)
        
        # Folder miesiąca
        month_dir = graph.create_folder(month, y_id)
        m_id = graph.get_folder_id(month, y_id)
        
        # Folder dodatkowe
        additional = graph.create_folder('Dodatkowe', m_id)
        additional_id = graph.get_folder_id('Dodatkowe', m_id)
        houers = graph.create_folder('MS_Godziny', additional_id)
        houers_id = graph.get_folder_id('MS_Godziny', additional_id)
        
        folder_structure = {
            "year": year,
            "month": month,
            "day": day,
            "year_id": y_id,
            "month_id": m_id,
            "additional_id": additional_id,
            "houers": houers_id,
        }
        
        logger.info("Struktura folderów została utworzona pomyślnie")
        return folder_structure
        
    except Exception as e:
        logger.error(f"Błąd podczas tworzenia struktury folderów: {str(e)}")
        raise


def get_godziny_folder_id() -> str:
    """
    Pobiera ID folderu 'Dodatkowe' dla aktualnego miesiąca
    
    Returns:
        str: ID folderu 'Dodatkowe'
    """
    logger = get_structure_logger()
    
    try:
        graph = MicrosoftGraph()
        
        year = datetime.now().strftime('%Y')
        month = datetime.now().strftime('%m')
        
        # Pobierz konfigurację ścieżek
        paths_config = get_paths_config()
        raporty_automatyczne_id = paths_config["raporty_automatyczne"]
        
        # Pobierz ID folderu roku
        y_id = graph.get_folder_id(year, raporty_automatyczne_id)
        if not y_id:
            raise ValueError(f"Folder roku {year} nie istnieje")
        
        # Pobierz ID folderu miesiąca
        m_id = graph.get_folder_id(month, y_id)
        if not m_id:
            raise ValueError(f"Folder miesiąca {month} nie istnieje")
        
        # Pobierz ID folderu dodatkowe
        additional_id = graph.get_folder_id('Dodatkowe', m_id)
        if not additional_id:
            raise ValueError("Folder 'Dodatkowe' nie istnieje")

        houers = graph.get_folder_id('MS_Godziny', additional_id)
        if not houers:
            raise ValueError("Folder 'MS_Godziny' nie istnieje")
        logger.info(f"ID folderu 'MS_Godziny': {str(m_id)}")
        return houers

        
    except Exception as e:
        logger.error(f"Błąd podczas pobierania ID folderu 'MS-Godziny': {str(e)}")
        raise


# Inicjalizacja struktury przy imporcie modułu
try:
    folder_structure = setup_folder_structure()
    h = folder_structure["houers_id"]
except Exception as e:
    # Jeśli nie udało się utworzyć struktury, spróbuj pobrać tylko ID folderu dodatkowe
    try:
        h = get_godziny_folder_id()
    except Exception:
        h = None