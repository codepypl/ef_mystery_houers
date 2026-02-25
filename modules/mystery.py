"""
Główny moduł do generowania raportów Mystery Hours
"""
from datetime import datetime
from pathlib import Path
import pandas as pd

from utils.logger import get_logger, setup_logger
from libs.database import Database
from modules.send_email import send_email
from config import get_database_config, get_config


# =========================================================
# GENEROWANIE RAPORTU
# =========================================================
def generate_report(db, report_name, report_definition):
    """
    Generuje pojedynczy raport na podstawie definicji SQL
    """
    logger = get_logger("ef_mystery_hours")

    try:
        logger.info(f"Generuję raport: {report_name}")
        query = db.remove_tags(report_definition)

        df = db.execute_sql(query, params={
            'dates_rangefrom': datetime.now().strftime('%Y-%m-01'),
            'dates_rangeto': datetime.now().strftime('%Y-%m-%d 23:59:59')
        })

        if df is not None and not df.empty:
            return df
        else:
            logger.warning(f"Pusty raport: {report_name}")
            return None

    except Exception as e:
        logger.error(f"Błąd raportu {report_name}: {e}")
        return None


# =========================================================
# POBIERANIE DEFINICJI RAPORTÓW
# =========================================================
def get_reports_data(db):
    """
    Pobiera wszystkie raporty assign_id=30
    """
    query = '''
        SELECT "Name", "Definition" 
        FROM "Reports"."ReportDefinitions"
        WHERE "State" = 0 AND "AssignId" = 30
    '''
    return db.execute_sql(query)


# =========================================================
# ZAPIS DO EXCEL
# =========================================================
def save_report_to_excel(df: pd.DataFrame, report_name: str) -> str:
    """
    Zapisuje df do pliku Excel w katalogu temp
    """
    config = get_config()
    config.ensure_directories()

    now = datetime.now()
    filename = f"{report_name}_{now.strftime('%Y_%m_%d_%H_%M_%S')}.xlsx"
    path = config.get_temp_file_path(filename)

    df.to_excel(path, index=False)
    return str(path)


# =========================================================
# MAIN
# =========================================================
def main():
    setup_logger()
    logger = get_logger("ef_mystery_hours")

    db_config = get_database_config()
    db = Database(db_config['url'])
    if not db.connect():
        logger.error("Brak połączenia z DB")
        return False

    temp_files = []

    try:
        reports = get_reports_data(db)
        if reports is None or reports.empty:
            logger.warning("Brak raportów do wygenerowania")
            return False

        for _, r in reports.iterrows():
            df = generate_report(db, r['Name'], r['Definition'])
            if df is not None:
                path = save_report_to_excel(df, r['Name'])
                temp_files.append(path)
                logger.info(f"Zapisano raport: {path}")

        if temp_files:
            # wysyłamy jeden email z wszystkimi raportami
            subject = f"Podsumowanie MS_Godziny - {datetime.now().strftime('%Y-%m-%d')}"
            body = f"Załączone raporty z kampanii MS_Godziny wygenerowane dnia {datetime.now().strftime('%Y-%m-%d %H:%M')}."
            if send_email(temp_files, subject=subject, body=body):
                logger.info("Email z wszystkimi raportami wysłany pomyślnie")
            else:
                logger.error("Nie udało się wysłać emaila z raportami")

        # usuwamy wszystkie pliki tymczasowe
        for f in temp_files:
            try:
                Path(f).unlink()
                logger.info(f"Usunięto plik tymczasowy: {f}")
            except Exception as e:
                logger.warning(f"Nie udało się usunąć pliku {f}: {e}")

        return True

    finally:
        db.disconnect()


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)