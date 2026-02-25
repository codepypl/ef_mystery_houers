import os
import logging
from datetime import datetime
from typing import List, Dict, Any
from libs.ms_graph import MicrosoftGraph
from utils.date_manager import DateManager

class ErrorHandler:
    """Obsługuje błędy i wysyłanie raportów e-mail"""
    
    def __init__(self, graph: MicrosoftGraph, date_manager: DateManager):
        self.graph = graph
        self.date_manager = date_manager
        self.errors = []
        
    def add_error(self, file_name: str, error_message: str, missing_columns: List[str] = None):
        """Dodaje błąd do listy"""
        error_info = {
            'file_name': file_name,
            'error_message': error_message,
            'missing_columns': missing_columns or [],
            'timestamp': datetime.now()
        }
        self.errors.append(error_info)
        logging.error(f"Błąd w pliku {file_name}: {error_message}")
    
    def send_error_report(self, recipients: List[str]):
        """Wysyła raport błędów e-mailem"""
        if not self.errors:
            return
            
        date_info = self.date_manager.get_date_info()
        
        subject = f"Raport błędów - przetwarzanie danych Azure {date_info['formatted_date']}"
        
        # Tworzenie treści e-maila
        body = f"""
        <html>
            <body>
                <h2>Raport błędów z przetwarzania danych Azure</h2>
                <p><strong>Data przetwarzania:</strong> {date_info['formatted_date']}</p>
                <p><strong>Liczba błędów:</strong> {len(self.errors)}</p>
                
                <h3>Szczegóły błędów:</h3>
                <table border="1" style="border-collapse: collapse; width: 100%;">
                    <tr style="background-color: #f2f2f2;">
                        <th style="padding: 8px;">Plik</th>
                        <th style="padding: 8px;">Błąd</th>
                        <th style="padding: 8px;">Brakujące kolumny</th>
                        <th style="padding: 8px;">Czas</th>
                    </tr>
        """
        
        for error in self.errors:
            missing_cols = ", ".join(error['missing_columns']) if error['missing_columns'] else "Brak"
            body += f"""
                    <tr>
                        <td style="padding: 8px;">{error['file_name']}</td>
                        <td style="padding: 8px;">{error['error_message']}</td>
                        <td style="padding: 8px;">{missing_cols}</td>
                        <td style="padding: 8px;">{error['timestamp'].strftime('%H:%M:%S')}</td>
                    </tr>
            """
        
        body += """
                </table>
                
                <p><strong>Uwaga:</strong> Pliki z błędami zostały pominięte w przetwarzaniu.</p>
                <p>Pozdrawiamy Efektum IT</p>
                <p><em>Ta wiadomość jest generowana automatycznie.</em></p>
            </body>
        </html>
        """
        
        try:
            self.graph.send_email(
                subject=subject,
                body=body,
                recipients=recipients,
                attachment_paths=[]
            )
            logging.info(f"Wysłano raport błędów do {len(recipients)} odbiorców")
        except Exception as e:
            logging.error(f"Błąd wysyłania raportu błędów: {e}")
    
    def get_error_summary(self) -> Dict[str, Any]:
        """Zwraca podsumowanie błędów"""
        return {
            'total_errors': len(self.errors),
            'files_with_errors': len(set(error['file_name'] for error in self.errors)),
            'errors_by_type': self._group_errors_by_type(),
            'missing_columns': self._get_all_missing_columns()
        }
    
    def _group_errors_by_type(self) -> Dict[str, int]:
        """Grupuje błędy według typu"""
        error_types = {}
        for error in self.errors:
            error_type = type(error['error_message']).__name__
            error_types[error_type] = error_types.get(error_type, 0) + 1
        return error_types
    
    def _get_all_missing_columns(self) -> List[str]:
        """Zwraca wszystkie brakujące kolumny"""
        all_columns = set()
        for error in self.errors:
            all_columns.update(error['missing_columns'])
        return list(all_columns)
    
    def clear_errors(self):
        """Czyści listę błędów"""
        self.errors = []

def create_error_handler(graph: MicrosoftGraph, date_manager: DateManager) -> ErrorHandler:
    """Tworzy instancję ErrorHandler"""
    return ErrorHandler(graph, date_manager) 