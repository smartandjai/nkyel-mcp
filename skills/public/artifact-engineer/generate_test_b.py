"""Acceptance Test B: 5-Slide True-Editable PPTX Presentation with Native Objects."""

import json
from pathlib import Path
import sys

sys.path.append(str(Path(__file__).resolve().parent / "scripts"))

from document_spec import (
    DocumentSpec,
    SlideContent,
    TableData,
    TableColumn
)
from artifact_pipeline import run_pipeline

OUTPUT_DIR = Path(__file__).resolve().parents[3] / "artifacts_demo/test_b_presentation"


def create_spec_b() -> DocumentSpec:
    return DocumentSpec(
        document_id="presentation_strategique_nkyel_2026",
        document_type="presentation",
        title="Plateforme Agentique Ñkyel 2.0 : Rendu Souverain & Vision QA",
        subtitle="Architecture Haute Performance & Délivrables Métier Éditables",
        author="Direction Technique & Architecture IA",
        organization="Ñkyel Studio · SmartANDJ AI Technologies",
        date="27 Octobre 2026",
        language="fr",
        style_preset="consulting_presentation",
        slides=[
            # Slide 1 : Titre
            SlideContent(
                slide_number=1,
                layout="title",
                title="Plateforme Agentique Ñkyel 2.0",
                subtitle="Rendu Souverain Haute Performance & Délivrables Professionnels 100% Éditables",
                speaker_notes="Bienvenue à tous. Cette présentation introduit la rupture technologique apportée par le module d'ingénierie d'artéfacts de Ñkyel."
            ),
            
            # Slide 2 : Métriques Clés
            SlideContent(
                slide_number=2,
                layout="metric_highlight",
                title="Indicateurs Clés de Performance Documentaire",
                subtitle="Mesures issues du banc d'essai comparatif en conditions réelles de production (Q4 2026)",
                metrics=[
                    {"label": "Gain Vitesse Rendu", "value": "+840 %"},
                    {"label": "Score Qualité Visuelle", "value": "99.4 %"},
                    {"label": "Frais Egress R2", "value": "0.00 $"},
                    {"label": "Réduction TCO Global", "value": "-62 %"}
                ],
                speaker_notes="Ces 4 métriques fondamentales valident le remplacement des solutions traditionnelles Chromium par le moteur Typst vectoriel."
            ),

            # Slide 3 : Piliers Architecturaux
            SlideContent(
                slide_number=3,
                layout="content",
                title="Piliers Fondamentaux de la Souveraineté Numérique",
                subtitle="Garanties d'intégrité, d'isolation stricte et de contrôle qualité en boucle fermée",
                bullets=[
                    "Isolation étanche de chaque tâche au sein de bacs à sable d'exécution E2B Cloud éphémères.",
                    "Persistance immuable des artéfacts validés sur compartiments Cloudflare R2 chiffrés de bout en bout.",
                    "Contrôle qualité automatique en boucle fermée par inspection visuelle multimodale DeepSeek Flash.",
                    "Garantie absolue d'éditabilité : aucun fichier n'est aplati en capture d'écran, chaque forme reste modifiable."
                ],
                speaker_notes="L'éditabilité réelle est un impératif non négociable. Nos diapositives sont composées de vraies zones de texte et de formes vectorielles."
            ),

            # Slide 4 : Tableau Comparatif
            SlideContent(
                slide_number=4,
                layout="table",
                title="Banc d'Essai Comparatif des Moteurs de Rendu",
                subtitle="Analyse multicritère : latence de compilation, empreinte mémoire et fidélité",
                table=TableData(
                    id="tbl_slides_benchmark",
                    title="Matrice Comparative de Production",
                    columns=[
                        TableColumn(header="Moteur Documentaire", key="engine", width_ratio=1.4, alignment="left"),
                        TableColumn(header="Latence Moyenne", key="latency", width_ratio=1.0, alignment="right"),
                        TableColumn(header="RAM Résidente", key="ram", width_ratio=1.0, alignment="right"),
                        TableColumn(header="Score Visuel", key="score", width_ratio=1.0, alignment="center"),
                        TableColumn(header="Format Produit", key="format", width_ratio=1.1, alignment="center")
                    ],
                    rows=[
                        {"engine": "Typst 0.15 Native (Ñkyel)", "latency": "62 ms", "ram": "28 Mo", "score": "98.5 / 100", "format": "PDF Vectoriel"},
                        {"engine": "python-pptx Native", "latency": "95 ms", "ram": "32 Mo", "score": "96.0 / 100", "format": "PPTX Éditable"},
                        {"engine": "python-docx Native", "latency": "84 ms", "ram": "35 Mo", "score": "94.0 / 100", "format": "DOCX Éditable"},
                        {"engine": "Chromium Headless Mode", "latency": "520 ms", "ram": "340 Mo", "score": "88.0 / 100", "format": "Image Aplatie"}
                    ]
                ),
                speaker_notes="Le tableau démontre la supériorité des bibliothèques natives sur les convertisseurs basés sur navigateurs."
            ),

            # Slide 5 : Feuille de Route
            SlideContent(
                slide_number=5,
                layout="content",
                title="Feuille de Route & Déploiement Opérationnel",
                subtitle="Plan d'action et étapes de déploiement pour les comités exécutifs et les équipes métier",
                bullets=[
                    "Phase 1 : Intégration du skill artifact-engineer comme compétence native dans le catalogue DeerFlow.",
                    "Phase 2 : Activation de l'inspection visuelle en production avec seuil de certification automatique.",
                    "Phase 3 : Déploiement de la bibliothèque complète de templates (Finance, Juridique, Stratégie).",
                    "Phase 4 : Synchronisation continue avec le portail client Ñkyel Studio et téléchargement sécurisé."
                ],
                speaker_notes="En conclusion, Ñkyel Studio offre désormais une chaîne de production documentaire digne des meilleurs cabinets de conseil."
            )
        ]
    )


def main():
    print("=== DÉBUT TEST B : PRÉSENTATION 5 DIAPOSITIVES ÉDITABLE PPTX ===")
    spec = create_spec_b()
    
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    spec_file = OUTPUT_DIR / "spec_test_b.json"
    with open(spec_file, "w", encoding="utf-8") as f:
        f.write(spec.model_dump_json(indent=2))
    
    print(f"Spécification enregistrée : {spec_file}")
    
    result = run_pipeline(
        doc=spec,
        output_dir=OUTPUT_DIR,
        requested_formats=["pptx"],
        perform_vision_qa=False,
        sync_to_r2=True
    )

    print("\n=== RÉSULTATS DU PIPELINE TEST B ===")
    print(f"Document ID : {result['document_id']}")
    print(f"Fichier PPTX généré : {result['deliverables'].get('pptx')}")
    print(f"Nombre de diapositives : {result.get('slide_count')}")
    print(f"Validation déterministe : {result['deterministic_validation']}")
    print(f"Synchronisation R2 : {result['r2_storage']}")


if __name__ == "__main__":
    main()
