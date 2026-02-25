"""
Klasa do obsługi Microsoft Graph API z centralnym loggerem
"""
import os
import base64
import json
import requests
from pathlib import Path
from msal import ConfidentialClientApplication
from utils.logger import get_logger
from config import get_microsoft_graph_config


class MicrosoftGraph:
    """Klasa do obsługi Microsoft Graph API"""
    
    def __init__(self, client_id=None, client_secret=None, tenant_id=None, 
                 username=None, password=None):
        """
        Inicjalizacja klasy MicrosoftGraph
        
        Args:
            client_id: ID aplikacji
            client_secret: Sekret aplikacji
            tenant_id: ID tenanta
            username: Nazwa użytkownika
            password: Hasło
        """
        ms_graph_config = get_microsoft_graph_config()
        self.client_id = client_id or ms_graph_config["client_id"]
        self.client_secret = client_secret or ms_graph_config["client_secret"]
        self.tenant_id = tenant_id or ms_graph_config["tenant_id"]
        self.username = username or ms_graph_config["username"]
        self.password = password or ms_graph_config["password"]
        
        self.scope = ["https://graph.microsoft.com/.default"]
        self.authority = f"https://login.microsoftonline.com/{self.tenant_id}"
        self.logger = get_logger("ms_graph")
        
        # Sprawdź czy wszystkie wymagane parametry są dostępne
        if not all([self.client_id, self.client_secret, self.tenant_id, 
                   self.username, self.password]):
            raise ValueError("Wszystkie parametry Microsoft Graph są wymagane")
        
        self.token = self._generate_access_token()
    
    def _generate_access_token(self) -> str:
        """
        Generuje token dostępu do Microsoft Graph
        
        Returns:
            str: Token dostępu
        """
        try:
            self.logger.info("Generowanie tokenu dostępu do Microsoft Graph...")
            
            client = ConfidentialClientApplication(
                client_id=self.client_id,
                client_credential=self.client_secret,
                authority=self.authority,
            )
            
            result = client.acquire_token_by_username_password(
                username=self.username,
                password=self.password,
                scopes=self.scope
            )
            
            if 'access_token' in result:
                self.logger.info("Token dostępu wygenerowany pomyślnie")
                return result['access_token']
            else:
                error_msg = f"Nie udało się wygenerować tokenu: {result.get('error_description', 'Nieznany błąd')}"
                self.logger.error(error_msg)
                raise Exception(error_msg)
                
        except Exception as e:
            self.logger.error(f"Błąd podczas generowania tokenu: {str(e)}")
            raise
    
    def _make_request(self, method: str, url: str, headers: dict = None, 
                     data: str = None, files: dict = None) -> dict:
        """
        Wykonuje żądanie HTTP do Microsoft Graph API
        
        Args:
            method: Metoda HTTP
            url: URL żądania
            headers: Nagłówki HTTP
            data: Dane do wysłania
            files: Pliki do wysłania
            
        Returns:
            dict: Odpowiedź z API
        """
        if headers is None:
            headers = {}
        
        headers["Authorization"] = f"Bearer {self.token}"
        headers["Content-Type"] = "application/json"
        
        try:
            response = requests.request(method, url, headers=headers, data=data, files=files)
            response.raise_for_status()
            
            if response.status_code == 202:  # Accepted, no content
                return {"message": "Request accepted, processing."}
            
            if response.status_code >= 400:
                error_msg = f"Żądanie nie powiodło się: {response.status_code}, {response.text}"
                self.logger.error(error_msg)
                raise Exception(error_msg)
            
            return response.json()
            
        except requests.exceptions.HTTPError as http_err:
            self.logger.error(f"Błąd HTTP: {http_err}")
            self.logger.error(f"Treść odpowiedzi: {response.text}")
            raise
        except json.JSONDecodeError as e:
            self.logger.error(f"Błąd dekodowania JSON: {e}")
            raise
        except Exception as e:
            self.logger.error(f"Błąd podczas wykonywania żądania: {str(e)}")
            raise
    
    def create_folder(self, folder_name: str, parent_folder_id: str = None) -> dict:
        """
        Tworzy folder na OneDrive
        
        Args:
            folder_name: Nazwa folderu
            parent_folder_id: ID folderu nadrzędnego
            
        Returns:
            dict: Odpowiedź z API
        """
        try:
            folder_id = self.get_folder_id(folder_name, parent_folder_id)
            if folder_id:
                self.logger.info(f"Folder '{folder_name}' już istnieje")
                return {"message": f"Folder '{folder_name}' już istnieje.", "folder_id": folder_id}
            
            url = (f"https://graph.microsoft.com/v1.0/me/drive/root/children"
                   if not parent_folder_id 
                   else f"https://graph.microsoft.com/v1.0/me/drive/items/{parent_folder_id}/children")
            
            data = json.dumps({
                "name": folder_name,
                "folder": {},
            })
            
            result = self._make_request("POST", url, data=data)
            self.logger.info(f"Utworzono folder '{folder_name}'")
            return result
            
        except Exception as e:
            self.logger.error(f"Błąd podczas tworzenia folderu '{folder_name}': {str(e)}")
            raise
    
    def get_folder_id(self, folder_name: str, parent_folder_id: str = None) -> str:
        """
        Pobiera ID folderu
        
        Args:
            folder_name: Nazwa folderu
            parent_folder_id: ID folderu nadrzędnego
            
        Returns:
            str: ID folderu lub None
        """
        try:
            url = (f"https://graph.microsoft.com/v1.0/me/drive/root/children"
                   if not parent_folder_id 
                   else f"https://graph.microsoft.com/v1.0/me/drive/items/{parent_folder_id}/children")
            
            children = self._make_request("GET", url)
            
            for child in children.get('value', []):
                if child.get('name') == folder_name and child.get('folder'):
                    return child.get('id')
            
            return None
            
        except Exception as e:
            self.logger.error(f"Błąd podczas pobierania ID folderu '{folder_name}': {str(e)}")
            raise
    
    def upload_file(self, file_path: str, parent_folder_id: str = None) -> dict:
        """
        Uploaduje plik na OneDrive
        
        Args:
            file_path: Ścieżka do pliku lokalnego
            parent_folder_id: ID folderu docelowego
            
        Returns:
            dict: Odpowiedź z API
        """
        try:
            file_path = Path(file_path)
            if not file_path.exists():
                raise FileNotFoundError(f"Plik nie istnieje: {file_path}")
            
            file_name = file_path.name
            self.logger.info(f"Uploaduję plik '{file_name}' na OneDrive...")
            
            if parent_folder_id:
                url = f"https://graph.microsoft.com/v1.0/me/drive/items/{parent_folder_id}:/{file_name}:/content"
            else:
                url = f"https://graph.microsoft.com/v1.0/me/drive/root:/{file_name}:/content"
            
            headers = {
                "Authorization": f"Bearer {self.token}", 
                "Content-Type": "application/octet-stream"
            }
            
            with open(file_path, "rb") as file:
                response = requests.put(url, headers=headers, data=file)
                response.raise_for_status()
                
            self.logger.info(f"Plik '{file_name}' został uploadowany pomyślnie")
            return response.json()
            
        except Exception as e:
            self.logger.error(f"Błąd podczas uploadu pliku '{file_path}': {str(e)}")
            raise
    
    def send_email(self, subject: str, body: str, recipients: list, 
                  attachment_paths: list = None, sender: str = None, 
                  require_read_receipt: bool = False, 
                  require_delivery_receipt: bool = False) -> dict:
        """
        Wysyła email przez Microsoft Graph
        
        Args:
            subject: Temat wiadomości
            body: Treść wiadomości
            recipients: Lista adresów email odbiorców
            attachment_paths: Lista ścieżek do załączników
            sender: Adres email nadawcy
            require_read_receipt: Czy wymagać potwierdzenia przeczytania
            require_delivery_receipt: Czy wymagać potwierdzenia dostarczenia
            
        Returns:
            dict: Odpowiedź z API
        """
        try:
            self.logger.info(f"Wysyłam email do {len(recipients)} odbiorców...")
            
            url = "https://graph.microsoft.com/v1.0/me/sendMail"
            message = {
                "message": {
                    "subject": subject,
                    "body": {
                        "contentType": "HTML",
                        "content": body
                    },
                    "toRecipients": [{"emailAddress": {"address": recipient}} for recipient in recipients],
                    "attachments": [],
                    "isReadReceiptRequested": require_read_receipt,
                    "isDeliveryReceiptRequested": require_delivery_receipt
                }
            }
            
            if sender:
                message["message"]["from"] = {"emailAddress": {"address": sender}}
            
            # Dodaj załączniki
            if attachment_paths:
                for attachment_path in attachment_paths:
                    attachment_path = Path(attachment_path)
                    if attachment_path.exists():
                        with open(attachment_path, "rb") as file:
                            content_bytes = base64.b64encode(file.read()).decode('utf-8')
                        
                        attachment = {
                            "@odata.type": "#microsoft.graph.fileAttachment",
                            "name": attachment_path.name,
                            "contentBytes": content_bytes
                        }
                        message["message"]["attachments"].append(attachment)
                        self.logger.info(f"Dodano załącznik: {attachment_path.name}")
                    else:
                        self.logger.warning(f"Załącznik nie istnieje: {attachment_path}")
            
            data = json.dumps(message)
            result = self._make_request("POST", url, data=data)
            
            self.logger.info("Email został wysłany pomyślnie")
            return result
            
        except Exception as e:
            self.logger.error(f"Błąd podczas wysyłania emaila: {str(e)}")
            raise
    
    def list_folder_contents(self, folder_id: str = None) -> dict:
        """
        Listuje zawartość folderu na OneDrive
        
        Args:
            folder_id: ID folderu (None dla głównego folderu)
            
        Returns:
            dict: Zawartość folderu
        """
        try:
            url = (f"https://graph.microsoft.com/v1.0/me/drive/root/children"
                   if not folder_id 
                   else f"https://graph.microsoft.com/v1.0/me/drive/items/{folder_id}/children")
            
            return self._make_request("GET", url)
            
        except Exception as e:
            self.logger.error(f"Błąd podczas listowania zawartości folderu: {str(e)}")
            raise
    
    def delete_file_by_name(self, file_name: str, parent_folder_id: str = None) -> dict:
        """
        Usuwa plik do kosza na OneDrive
        
        Args:
            file_name: Nazwa pliku do usunięcia
            parent_folder_id: ID folderu nadrzędnego
            
        Returns:
            dict: Odpowiedź z API
        """
        try:
            url = (f"https://graph.microsoft.com/v1.0/me/drive/root/children"
                   if not parent_folder_id 
                   else f"https://graph.microsoft.com/v1.0/me/drive/items/{parent_folder_id}/children")
            
            items = self._make_request("GET", url)
            
            for item in items.get('value', []):
                if item.get('name') == file_name and not item.get('folder'):
                    file_id = item.get('id')
                    delete_url = f"https://graph.microsoft.com/v1.0/me/drive/items/{file_id}"
                    result = self._make_request("DELETE", delete_url)
                    self.logger.info(f"Usunięto plik '{file_name}'")
                    return result
            
            self.logger.warning(f"Plik '{file_name}' nie został znaleziony")
            return {"message": f"Plik '{file_name}' nie został znaleziony."}
            
        except Exception as e:
            self.logger.error(f"Błąd podczas usuwania pliku '{file_name}': {str(e)}")
            raise 