import re
import json
from backend.app.utils.llm import generate_content
from backend.app.utils.google_slides import (
    duplicate_template_presentation,
    get_presentation_structure,
    update_slide_text_elements,
    get_shareable_url,
)
from backend.app.utils.language import detect_language

def slides_adaptation_agent(state: dict) -> dict:
    print("🖼️ Google Slides adaptation agent launched.")

    user_message = state.get("user_message") or state.get("message")
    attached_text = state.get("attached_text", "")
    full_source_text = attached_text.strip() or user_message.strip()

    if not full_source_text:
        state["agent_response"] = "Aucun contenu à intégrer n’a été fourni. Merci d’envoyer un texte ou document."
        state["switch"] = "default"
        return state

    print("🧾 Texte source détecté :", repr(full_source_text[:300]))

    # Étape 1 : Dupliquer le modèle Slides
    try:
        user_id = state.get("user_id", "anonymous")
        new_presentation_id = duplicate_template_presentation(user_id=user_id)
        print(f"📄 Présentation dupliquée : {new_presentation_id}")
    except Exception as e:
        print("❌ Erreur lors de la duplication du modèle :", e)
        state["agent_response"] = "Impossible de dupliquer la présentation modèle."
        return state

    # Étape 2 : Extraire les zones de texte
    slides_structure = get_presentation_structure(new_presentation_id)
    print("🧱 Slides analysées :", len(slides_structure))

    # 🔍 Affichage de la structure pour debug
    from pprint import pprint
    for slide_index, (slide_id, elements) in enumerate(slides_structure.items()):
        print(f"\n--- 🖼️ Slide {slide_index + 1} (ID: {slide_id}) ---")
        for element in elements:
            print(f"🔹 Type: {element['type']}")
            print(f"🔹 Texte: {repr(element['text'][:100])}")
            print(f"🔹 Object ID: {element['objectId']}")
            print("---")

    # Étape 3 : Détection automatique de langue
    lang_code = detect_language(full_source_text)
    print("🌍 Langue détectée :", lang_code)

    # Étape 4 : Générer le texte réécrit pour chaque zone (hors titres)
    rewritten = {}
    for slide_id, elements in slides_structure.items():
        rewritten[slide_id] = []
        for element in elements:
            #if element["type"] != "BODY":
            # if element["type"] == "TITLE":
            #     rewritten[slide_id].append(element)  # Conserve titres intacts
            #     continue
            if element["type"] in ["TITLE", "SUBTITLE"]:
                rewritten[slide_id].append(element)
                continue

#             prompt = f"""
# Tu es un assistant intelligent et expert dans l'adaptation de slides. Tu sais qu'il ne faut pas ajouter de mots, juste 
# les changer et les adapter, ici dans ce cas tu dois adapter chacun des contenus qui sont selon toi pas des titres
# suivant ces informations: {full_source_text}. Tu n'ajouteras aucun commentaire ni aucun mot, tu ne feras qu'adapter les 
# textes que tu recevras en gardant le même nombre de mots ou alors même un peu moins de mots.
# Pour rappel, voici le contenu cible, qui doit guider ton adaptation:
# ---
# {full_source_text}
# ---
# Tu sais aussi que des bouts de texte comme "Enjeux clients
# Clients prioritaires cibles
# Etat des lieux des offres actuelles (solutions et concurrents)
# Perspectives et évolution du marché
# " n'ont pas besoin d'être adaptés car déjà génériques, ainsi que les bouts de texte où l'on parle des membres clés. 
# De même, tu n'as pas besoin d'adapter les slides avec une table des matières, et les zones de texte comme celle-ci "Sommaire exécutif
# Analyse du marché 
# Présentation de l’offre 
# Porteur et équipes 
# Business Plan et prévisionnel
# Supports Marketing  
# ".
# Tu es maintenant aligné avec ce texte: {full_source_text}, tu respectes le ton et la langue d’origine ({lang_code}). Tu vas maintenant adapter 
# ce texte:

# Texte original :
# {element['text']}

# Texte réécrit :
# """

            prompt = f"""
Tu es un assistant expert en adaptation de contenus pour des slides Google. 
Tu dois adapter le texte ci-dessous pour l’aligner avec les informations fournies, 
en respectant la même langue ({lang_code}) et le même ton.

Règles :
- Ne change pas les titres ou sous-titres (ils sont déjà exclus automatiquement).
- Ne commente pas. Ne justifie pas. Ne dépasse pas la longueur originale.

Contexte cible :
---
{full_source_text}
---

Texte à adapter :
---
{element['text']}
---

Texte adapté :
"""



            try:
                new_text = generate_content(prompt).strip()
                rewritten[slide_id].append({**element, "text": new_text})
            except Exception as e:
                print("⚠️ Erreur LLM :", e)
                rewritten[slide_id].append(element)

    # Étape 5 : Appliquer les changements
    update_slide_text_elements(new_presentation_id, rewritten)

    # Étape 6 : Rendre la présentation accessible et renvoyer le lien
    presentation_url = get_shareable_url(new_presentation_id)
    state["agent_response"] = f"La présentation a été générée et adaptée : {presentation_url}"
    state["presentation_url"] = presentation_url
    state["action_taken"] = "slides_adapted"
    return state
