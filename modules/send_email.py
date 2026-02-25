"""
Moduł do wysyłania emaili z wieloma załącznikami
"""
from pathlib import Path
from utils.logger import get_mail_logger
from libs.ms_graph import MicrosoftGraph
from config import get_email_config, get_config
from datetime import datetime


def send_email(file_paths: list, subject: str = None, body: str = None,
                                recipients: list = None) -> bool:
    """
    Wysyła jeden email z wieloma załącznikami

    Args:
        file_paths: lista ścieżek do plików (str lub Path)
        subject: temat wiadomości (opcjonalny)
        body: treść wiadomości (opcjonalny)
        recipients: lista odbiorców (opcjonalna)

    Returns:
        bool: True jeśli email został wysłany pomyślnie
    """
    logger = get_mail_logger()

    try:
        if not file_paths:
            logger.error("Brak plików do wysłania")
            return False

        # Konwersja Path/str
        files = [str(Path(f)) for f in file_paths]

        # Sprawdzenie, czy pliki istnieją
        for f in files:
            if not Path(f).exists():
                logger.error(f"Plik nie istnieje: {f}")
                return False

        # Konfiguracja
        email_config = get_email_config()
        if recipients is None:
            recipients = email_config["recipients"]

        if subject is None:
            subject = f"Raporty MS_Godziny - {datetime.now().strftime('%Y-%m-%d')}"
        if body is None:
            body = f"""
            <html><body>
            <b>Witaj!</b><br/>
            W załączeniu przesyłamy raporty MS_Godziny wygenerowane dnia: {datetime.now().strftime('%Y-%m-%d %H:%M')}<br/>
            Pozdrawiamy Efektum IT<br/>
            <b>Ta wiadomość jest generowana automatycznie, nie odpowiadaj na nią!</b>
            </body></html>"""

        # Inicjalizacja Microsoft Graph
        graph = MicrosoftGraph()

        # Wysyłka emaila
        logger.info(f"Wysyłam email z {len(files)} załącznikami")
        graph.send_email(subject, body, recipients, files)
        logger.info("Email został wysłany pomyślnie")
        return True

    except Exception as e:
        logger.error(f"Błąd podczas wysyłania emaila: {str(e)}")
        return False