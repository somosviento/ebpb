import os
import requests
import base64
from datetime import datetime
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

class GoogleDriveService:
    def __init__(self):
        self.api_url = os.getenv('GOOGLE_SCRIPT_URL')
        self.secure_token = os.getenv('GOOGLE_SCRIPT_TOKEN', '1234')
        self.folder_id = os.getenv('GOOGLE_FOLDER_ID', '')

    def create_folder_and_upload(self, pdf_path, apellido, fecha):
        """Crear carpeta y subir PDF usando Google Apps Script"""
        try:
            if not self.api_url:
                return None, None

            # Leer el archivo PDF y convertirlo a base64
            with open(pdf_path, 'rb') as file:
                pdf_content = base64.b64encode(file.read()).decode('utf-8')

            # Preparar datos para enviar al script
            data = {
                'token': self.secure_token,
                'parentFolderId': self.folder_id,
                'folderName': f"{apellido}_{fecha}",
                'fileName': f"{apellido}_{fecha}_formulario.pdf",
                'pdfContent': pdf_content
            }

            # Hacer la solicitud al script desplegado
            response = requests.post(self.api_url, json=data)
            if response.status_code == 200:
                result = response.json()
                if 'error' in result:
                    print(f"Error del script: {result['error']}")
                    return None, None
                return result.get('folderId'), result.get('folderUrl')
            
            return None, None
        except Exception as e:
            print(f"Error en create_folder_and_upload: {str(e)}")
            return None, None

    def create_spreadsheet(self, name, headers, rows):
        """Crear una hoja de cálculo con los datos exportados"""
        try:
            if not self.api_url:
                return None, None

            data = {
                'token': self.secure_token,
                'action': 'createSpreadsheet',
                'spreadsheetName': name,
                'headers': headers,
                'rows': rows
            }

            response = requests.post(self.api_url, json=data)
            if response.status_code == 200:
                result = response.json()
                if 'error' in result:
                    print(f"Error del script: {result['error']}")
                    return None, None
                return result.get('spreadsheetId'), result.get('spreadsheetUrl')
            
            return None, None
        except Exception as e:
            print(f"Error en create_spreadsheet: {str(e)}")
            return None, None

    def send_email(self, to_email, subject, html_body, sender_name=None, attachment_ids=None, placeholders=None):
        """
        Send an email using Gmail with optional attachments and placeholder replacement.
        
        Args:
            to_email (str): Email address of the recipient
            subject (str): Email subject line (can contain placeholders)
            html_body (str): HTML content of the email (can contain placeholders)
            sender_name (str, optional): Name to display as the sender
            attachment_ids (list, optional): List of Google Drive file IDs to attach to the email
            placeholders (dict, optional): Dictionary of placeholder values to replace in subject and body
                                          Format: {'placeholder_name': 'replacement_value'}
                                          
        Returns:
            dict: Result information about the sent email
        """
        if not self.api_url:
            raise Exception("Google Script URL not configured")

        try:
            response = requests.post(self.api_url, json={
                'action': 'sendEmail',
                'to': to_email,
                'subject': subject,
                'htmlBody': html_body,
                'senderName': sender_name,
                'attachmentIds': attachment_ids or [],
                'placeholders': placeholders or {},
                'token': self.secure_token
            })

            if response.status_code != 200:
                raise Exception(f"Error sending email: {response.text}")

            result = response.json()
            if not result.get('success'):
                raise Exception(f"Error from Google API: {result.get('error')}")

            return result.get('result')

        except Exception as e:
            raise Exception(f"Failed to send email: {str(e)}")