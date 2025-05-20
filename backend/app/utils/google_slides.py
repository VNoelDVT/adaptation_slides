from googleapiclient.discovery import build
from google.oauth2 import service_account

import os
import uuid

# --- Configuration ---
SCOPES = ['https://www.googleapis.com/auth/presentations', 'https://www.googleapis.com/auth/drive']
SERVICE_ACCOUNT_FILE = os.path.join(os.path.dirname(__file__), 'agent-slides-credentials.json')
TEMPLATE_PRESENTATION_ID = '1heBkHt9IVFKTaS2NxC2xycfnrb8u_9TL6zlM1T1HfHg'

# --- Initialisation du service Google Slides & Drive ---
def get_google_services():
    creds = service_account.Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
    slides_service = build('slides', 'v1', credentials=creds)
    drive_service = build('drive', 'v3', credentials=creds)
    return slides_service, drive_service

# --- Dupliquer le modèle de présentation ---
def duplicate_template_presentation(user_id="user") -> str:
    slides_service, drive_service = get_google_services()
    new_title = f"Présentation adaptée - {user_id} - {uuid.uuid4().hex[:6]}"

    body = {
        'name': new_title
    }

    copied_file = drive_service.files().copy(
        fileId=TEMPLATE_PRESENTATION_ID,
        body=body
    ).execute()

    return copied_file['id']

# --- Extraire les zones de texte par slide ---
def get_presentation_structure(presentation_id: str) -> dict:
    slides_service, _ = get_google_services()
    presentation = slides_service.presentations().get(presentationId=presentation_id).execute()

    structure = {}
    for slide in presentation.get("slides", []):
        slide_id = slide.get("objectId")
        structure[slide_id] = []

        for element in slide.get("pageElements", []):
            shape = element.get("shape")
            if not shape:
                continue

            text_elements = shape.get("text", {}).get("textElements", [])
            raw_text = ''.join([
                te.get("textRun", {}).get("content", "")
                for te in text_elements if "textRun" in te
            ]).strip()

            if not raw_text:
                continue

            shape_type = shape.get("shapeType", "")
            element_type = "TITLE" if "TITLE" in shape_type else "BODY"

            structure[slide_id].append({
                "objectId": element["objectId"],
                "text": raw_text,
                "type": element_type
            })

    return structure

# --- Mettre à jour le contenu des zones de texte ---
def update_slide_text_elements(presentation_id: str, updates: dict):
    slides_service, _ = get_google_services()
    requests = []

    for slide_id, elements in updates.items():
        for element in elements:
            if "objectId" not in element or "text" not in element:
                continue
            requests.append({
                "deleteText": {
                    "objectId": element["objectId"],
                    "textRange": {
                        "type": "ALL"
                    }
                }
            })
            requests.append({
                "insertText": {
                    "objectId": element["objectId"],
                    "text": element["text"]
                }
            })

    if requests:
        slides_service.presentations().batchUpdate(
            presentationId=presentation_id,
            body={"requests": requests}
        ).execute()

# --- Générer un lien partageable public ---
def get_shareable_url(file_id: str) -> str:
    _, drive_service = get_google_services()

    # Modifier les permissions
    drive_service.permissions().create(
        fileId=file_id,
        body={
            'type': 'anyone',
            'role': 'reader'
        }
    ).execute()

    return f"https://docs.google.com/presentation/d/{file_id}/edit"
