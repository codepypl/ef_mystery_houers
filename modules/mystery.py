import shutil

from modules.send_email import send_email_with_zip
from modules.onedrive_upload import upload_files_to_onedrive
from modules.generate_zip import create_password_protected_zip
from modules.structure import get_godziny_folder_id
from libs.database import Database
from config import get_database_config, get_config
from datetime import datetime
from utils.logger import setup_logger, get_logger
from pathlib import Path

def main():
    setup_logger()
    logger = get_logger("ef_mystery_hours")
    db = Database(get_database_config()['url'])
    config = get_config()
    if not db.connect():
        logger.error("Brak połączenia z DB")
        return False

    try:
        # pobranie raportów assign_id=30
        reports = db.execute_sql("""
            SELECT "Name", "Definition"
            FROM "Reports"."ReportDefinitions"
            WHERE "State" = 0 AND "AssignId" = 30
        """)
        if reports.empty:
            logger.warning("Brak raportów do wygenerowania")
            return False

        # folder docelowy na OneDrive
        godziny_folder_id = get_godziny_folder_id()

        temp_files = []
        for _, r in reports.iterrows():
            df = db.execute_sql(db.remove_tags(r["Definition"]), params={
                'dates_rangefrom': datetime.now().strftime("%Y-%m-01"),
                'dates_rangeto': datetime.now().strftime("%Y-%m-%d 23:59:59")
            })
            if df.empty:
                logger.warning(f"Pusty raport: {r['Name']}")
                continue
            config = get_config()
            path = config.get_temp_file_path(f"{r['Name']}_{datetime.now().strftime('%Y_%m_%d_%H_%M_%S')}.xlsx")
            df.to_excel(path, index=False)
            try:
                temp_files.append(str(path))
                logger.info(f"Zapisano raport: {path}")
            except Exception as e:
                error_msg = f"""Problem z wygenerowaniem raportu:\r\n Plik: {path}\r\n Błąd: {e}"""
                logger.error(error_msg)
                return False
        if not temp_files:
            logger.warning("Brak wygenerowanych raportów")
            return False

        # upload XLSX na OneDrive
        try:
            upload_files_to_onedrive(temp_files, godziny_folder_id)
        except Exception as e:
            logger.error(f"""Nie udało się wgrać pliku {temp_files[0]} na OneDrive\r\n z powodu błędu: {e}""")

        # ZIP z hasłem TMPL{rok}
        try:
            zip_path = create_password_protected_zip(temp_files, password=f"TMPL{datetime.now().strftime('%Y').replace('2','@')}")
            send_email_with_zip(zip_path)
        except Exception as e:
            logger.error(f"""Nie udało się wysłać wiadomości e-mail z powodu błędu {e}""")
    finally:
        db.disconnect()
        if config.temp_dir.exists():
            shutil.rmtree(config.temp_dir)
            config.temp_dir.mkdir(exist_ok=True)
            logger.info("Wyczyszczono katalog tymczasowy")