from pathlib import Path
from utils.logger import get_structure_logger
from libs.ms_graph import MicrosoftGraph

def upload_files_to_onedrive(files: list, folder_id: str):
    """
    Upload wszystkich plików na OneDrive
    """
    logger = get_structure_logger()
    graph = MicrosoftGraph()
    uploaded_paths = []
    for f in files:
        graph.upload_file(str(f), folder_id)
        uploaded_paths.append(f)
        logger.info(f"Plik {Path(f).name} wgrany na OneDrive")
    return uploaded_paths