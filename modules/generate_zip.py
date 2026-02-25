from pathlib import Path
import pyzipper
from datetime import datetime
from config import get_config
from utils.logger import get_logger

def create_password_protected_zip(file_paths: list, password: str = None) -> str:
    """
    Tworzy ZIP z plikami i hasłem AES
    """
    logger = get_logger()
    config = get_config()
    temp_dir = Path(config.temp_dir)
    now = datetime.now()
    zip_name = f"MS_Godziny_{now.strftime('%Y_%m_%d_%H_%M_%S')}.zip"
    zip_path = temp_dir / zip_name
    password_bytes = password.encode('utf-8') if password else None

    with pyzipper.AESZipFile(zip_path, 'w', compression=pyzipper.ZIP_DEFLATED,
                             encryption=pyzipper.WZ_AES) as zf:
        if password_bytes:
            zf.setpassword(password_bytes)
        for f in file_paths:
            zf.write(f, arcname=Path(f).name)
    logger.info(f"Utworzono ZIP: {zip_path} (hasło: {password})")
    return str(zip_path)
