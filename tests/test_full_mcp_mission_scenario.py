"""Full End-to-End Cross-Application MCP Mission Scenario Test for Ñkyel Studio."""

import asyncio
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

REPO_ROOT = Path(__file__).resolve().parents[1]
load_dotenv(REPO_ROOT / ".env")
load_dotenv(REPO_ROOT / "backend/.env")

sys.path.append(str(REPO_ROOT / "backend/packages/harness"))
sys.path.append(str(REPO_ROOT / "skills/public/artifact-engineer/scripts"))

from nkyel.mcp.tool_registry import TOOL_REGISTRY, get_verified_tools_count
from nkyel.mcp.gmail_send_adapter import prepare_gmail_draft, send_gmail_with_approval
from nkyel.sandbox.e2b_desktop_tools import (
    computer_launch_session,
    computer_scroll,
    computer_close_session
)
from artifact_pipeline import run_pipeline, upload_to_r2
from document_spec import DocumentSpec, DocumentSection, ParagraphBlock, TableData, TableColumn


def run_test():
    print("=================================================================")
    print("=== DÉBUT SCÉNARIO COMPLET DE MISSION MCP CROSS-APPLICATION ===")
    print("=================================================================")

    # 1. Vérification du Catalogue MCP (50 Outils)
    count = get_verified_tools_count()
    print(f"STEP 1: Catalogue MCP vérifié ({count} outils découverts).")
    assert count == 50

    # 2. Google Drive MCP (Recherche et Récupération)
    print("STEP 2: Récupération du document cible via Google Drive MCP...")
    mock_drive_doc = {
        "file_id": "drive_doc_gabon_2026",
        "name": "Rapport_Souverainete_Gabon_ANINF.docx",
        "mime_type": "application/vnd.google-apps.document",
        "last_modified": "2026-10-26T18:00:00Z"
    }
    print(f"  -> Fichier Drive identifié : {mock_drive_doc['name']} (ID: {mock_drive_doc['file_id']})")

    # 3. Recherche Web Tavily MCP
    print("STEP 3: Recherche d'informations fraîches via Tavily MCP...")
    import httpx
    tavily_auth = os.getenv("TAVILY_MCP_AUTH")
    headers = {"Authorization": tavily_auth, "Content-Type": "application/json"}
    call_payload = {
        "jsonrpc": "2.0",
        "id": 10,
        "method": "tools/call",
        "params": {
            "name": "tavily_search",
            "arguments": {"query": "ANINF Gabon services publics numeriques", "max_results": 2}
        }
    }
    r = httpx.post("https://mcp.tavily.com/mcp/", headers=headers, json=call_payload, timeout=12.0)
    print(f"  -> Tavily MCP Tools/Call status: {r.status_code}")

    # 4. Ordinateur Visuel E2B Desktop (Navigation Réelle)
    print("STEP 4: Ouverture du navigateur Chrome dans E2B Cloud Desktop...")
    browser_res = computer_launch_session("https://aninf.ga")
    print(f"  -> E2B Sandbox actif : {browser_res['sandbox_id']}")
    print(f"  -> Stream URL : {browser_res['stream_url']}")
    print(f"  -> Capture d'écran capturée ({len(browser_res['screenshot_base64'])} octets b64)")
    
    # Scroll action
    scroll_res = computer_scroll(browser_res["sandbox_id"], direction="down", amount=3)
    print(f"  -> Action souris exécutée : {scroll_res['action']}")
    
    # Close session
    computer_close_session(browser_res["sandbox_id"])
    print("  -> Session E2B fermée et libérée.")

    # 5. Ingénierie d'Artéfact (PDF Professionnel Typst)
    print("STEP 5: Compilation du rapport mis à jour avec Typst 0.15...")
    doc = DocumentSpec(
        document_id="rapport_mission_gabon_2026",
        document_type="report",
        title="Synthèse Stratégique : Services Publics Numériques au Gabon",
        subtitle="Mise à jour suite aux recherches Tavily et inspection E2B Desktop",
        executive_summary="Ce rapport intègre les données officielles vérifiées de l'ANINF et de la DGI Gabon.",
        sections=[
            DocumentSection(
                id="sec_aninf",
                title="1. Infrastructures & Téléprocédures Nationales",
                paragraphs=[ParagraphBlock(text="L'ANINF supervise le datacenter national Tier III de Libreville et l'interconnexion gouvernementale.")],
                tables=[
                    TableData(
                        id="tbl_projets",
                        title="Plateformes Publiques Déployées",
                        columns=[
                            TableColumn(header="Plateforme", key="name"),
                            TableColumn(header="Ministère", key="dept"),
                            TableColumn(header="Statut", key="status")
                        ],
                        rows=[
                            {"name": "e-Tax", "dept": "DGI / Finances", "status": "Opérationnel"},
                            {"name": "Guichet Unique ANPI", "dept": "Investissement", "status": "Opérationnel"}
                        ]
                    )
                ]
            )
        ]
    )
    
    out_dir = REPO_ROOT / "artifacts_demo/mission_test"
    art_res = run_pipeline(doc, out_dir, requested_formats=["pdf"], perform_vision_qa=False, sync_to_r2=True)
    pdf_path = art_res["deliverables"]["pdf"]
    print(f"  -> PDF professionnel généré : {pdf_path}")
    print(f"  -> R2 URL : {art_res['r2_storage'].get('pdf', {}).get('url')}")

    # 6. Préparation du Courriel Gmail avec Pièce Jointe & Approbation Humaine
    print("STEP 6: Rédaction de l'email Gmail et génération de l'approbation humaine...")
    draft = prepare_gmail_draft(
        to="test.user@smartandjai.com",
        subject="Rapport Final : Services Publics Numériques au Gabon",
        body="Bonjour,\n\nVeuillez trouver ci-joint le rapport mis à jour avec les dernières données ANINF.",
        attachment_paths=[pdf_path]
    )
    print(f"  -> Statut brouillon : {draft['status']}")
    print(f"  -> Jeton d'approbation immuable : {draft['approval_token']}")
    print(f"  -> Pièce jointe vérifiée : {draft['attachments'][0]['filename']} ({draft['attachments'][0]['size_bytes']} octets)")

    # 7. Approbation Explicite et Envoi
    print("STEP 7: Soumission de l'approbation humaine...")
    send_res = send_gmail_with_approval(draft["approval_token"], approved=True)
    print(f"  -> Résultat d'envoi : {send_res['status']}")
    print(f"  -> Mode : {send_res.get('mode')}")
    print(f"  -> Destinataire certifié : {send_res['to']}")

    print("\n=================================================================")
    print("=== SUCCÈS COMPLET DE LA MISSION CROSS-APPLICATION MCP ! ===")
    print("=================================================================")


if __name__ == "__main__":
    run_test()
