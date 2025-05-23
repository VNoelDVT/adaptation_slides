from googleapiclient.discovery import build
from google.oauth2 import service_account

import os
import uuid

# --- Configuration ---
SCOPES = ['https://www.googleapis.com/auth/presentations', 'https://www.googleapis.com/auth/drive']
SERVICE_ACCOUNT_FILE = os.path.join(os.path.dirname(__file__), 'agent-slides-credentials.json')
TEMPLATE_PRESENTATION_ID = '1NEgpbaGMkGuF1VQCpjpS1Vwxq3W1C-EO1IQgFlnVjJ4'

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

# # --- Extraire les zones de texte par slide ---
# def get_presentation_structure(presentation_id: str) -> dict:
#     slides_service, _ = get_google_services()
#     presentation = slides_service.presentations().get(presentationId=presentation_id).execute()

#     structure = {}
#     for slide in presentation.get("slides", []):
#         slide_id = slide.get("objectId")
#         structure[slide_id] = []

#         for element in slide.get("pageElements", []):
#             shape = element.get("shape")
#             if not shape:
#                 continue

#             text_elements = shape.get("text", {}).get("textElements", [])
#             raw_text = ''.join([
#                 te.get("textRun", {}).get("content", "")
#                 for te in text_elements if "textRun" in te
#             ]).strip()

#             if not raw_text:
#                 continue

#             shape_type = shape.get("shapeType", "")
#             #element_type = "TITLE" if "TITLE" in shape_type else "BODY"
            
#             if shape_type == "TITLE":
#                 element_type = "TITLE"
#             elif shape_type == "BODY":
#                  element_type = "BODY"
#             else:
#                 element_type = "OTHER"


#             structure[slide_id].append({
#                 "objectId": element["objectId"],
#                 "text": raw_text,
#                 "type": element_type
#             })

#     return structure


#def get_presentation_structure(presentation_id: str) -> dict:
    # slides_service, _ = get_google_services()
    # presentation = slides_service.presentations().get(presentationId=presentation_id).execute()

    # structure = {}
    # for slide in presentation.get("slides", []):
    #     slide_id = slide.get("objectId")
    #     structure[slide_id] = []

    #     for element in slide.get("pageElements", []):
    #         shape = element.get("shape")
    #         if not shape:
    #             continue

    #         text_elements = shape.get("text", {}).get("textElements", [])
    #         raw_text = ''.join([
    #             te.get("textRun", {}).get("content", "")
    #             for te in text_elements if "textRun" in te
    #         ]).strip()

    #         if not raw_text:
    #             continue

    #         # Détection fine du type
    #         shape_type = shape.get("shapeType", "")
    #         if shape_type == "TITLE":
    #             element_type = "TITLE"
    #         elif shape_type == "BODY":
    #             element_type = "BODY"
    #         elif shape_type == "SUBTITLE":
    #             element_type = "SUBTITLE"
    #         elif shape_type == "TEXT_BOX":
    #             element_type = "TEXT_BOX"
    #         elif shape_type == "CAPTION":
    #             element_type = "CAPTION"
    #         else:
    #             element_type = f"OTHER_{shape_type}"

    #         structure[slide_id].append({
    #             "objectId": element["objectId"],
    #             "text": raw_text,
    #             "type": element_type
    #         })

    # return structure


# def get_presentation_structure(presentation_id: str) -> dict:
#     slides_service, _ = get_google_services()
#     presentation = slides_service.presentations().get(presentationId=presentation_id).execute()

#     structure = {}
#     for slide in presentation.get("slides", []):
#         slide_id = slide.get("objectId")
#         structure[slide_id] = []

#         for element in slide.get("pageElements", []):
#             shape = element.get("shape")
#             if not shape:
#                 continue

#             text_elements = shape.get("text", {}).get("textElements", [])
#             raw_text = ''.join([
#                 te.get("textRun", {}).get("content", "")
#                 for te in text_elements if "textRun" in te
#             ]).strip()

#             if not raw_text:
#                 continue

#             shape_type = shape.get("shapeType", "TEXT_BOX")
#             transform = element.get("transform", {})
#             translate_y = transform.get("translateY", 9999)

#             # Heuristique basée sur la position verticale
#             if translate_y < 150:
#                 element_type = "TITLE_LIKE"
#             else:
#                 element_type = "BODY_LIKE"

#             structure[slide_id].append({
#                 "objectId": element["objectId"],
#                 "text": raw_text,
#                 "type": element_type,
#                 "positionY": translate_y
#             })

#     return structure

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

            # Utiliser le placeholderType au lieu du shapeType
            placeholder_info = shape.get("placeholder")
            if placeholder_info:
                placeholder_type = placeholder_info.get("type", "UNKNOWN")
                element_type = placeholder_type  # direct, ex: TITLE, BODY, SUBTITLE, etc.
            else:
                element_type = "TITLE"

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
