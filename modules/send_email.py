"""
Moduł do wysyłania emaili z wieloma załącznikami
"""
from pathlib import Path
from utils.logger import get_mail_logger
from libs.ms_graph import MicrosoftGraph
from config import get_email_config, get_config
from datetime import datetime

def send_email_with_zip(zip_path: str, subject: str = None, body: str = None,
                        recipients: list = None):
    """
    Wysyła email z jednym załącznikiem ZIP
    """

    logger = get_mail_logger()
    graph = MicrosoftGraph()
    email_config = get_email_config()
    try:
        if not zip_path:
            logger.error("Brak plików do wysłania")
            return False
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
            logger.info(f"Wysyłam email z ZIP: {Path(zip_path).name}")
            graph.send_email(subject, body, recipients, [str(zip_path)])
            logger.info("Email wysłany pomyślnie")
    except Exception as e:
        logger.error(f"Błąd podczas wysyłania emaila: {str(e)}")
        return False