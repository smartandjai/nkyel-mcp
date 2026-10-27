"""Acceptance Test A: Professional 4-6 Page PDF and DOCX Sovereign Report with DeepSeek Vision QA."""

import json
from pathlib import Path
import sys

sys.path.append(str(Path(__file__).resolve().parent / "scripts"))

from document_spec import (
    DocumentSpec,
    DocumentSection,
    ParagraphBlock,
    TableData,
    TableColumn,
    Citation
)
from artifact_pipeline import run_pipeline

OUTPUT_DIR = Path(__file__).resolve().parents[3] / "artifacts_demo/test_a_report"


def create_spec_a() -> DocumentSpec:
    return DocumentSpec(
        document_id="rapport_strategique_nkyel_2026",
        document_type="report",
        title="Rapport d'Évaluation Stratégique : Infrastructure Agentique Souveraine Ñkyel",
        subtitle="Performances, Résilience Hybride Cloud-Edge et Banc d'Essai Comparatif 2026",
        author="Direction de l'Ingénierie Documentaire",
        organization="Ñkyel Studio · SmartANDJ AI Technologies",
        date="27 Octobre 2026",
        language="fr",
        audience="Comité de Direction et Architectes Systèmes",
        purpose="Démonstration de conformité et validation de délivrables haute fidélité",
        style_preset="executive_report",
        executive_summary=(
            "Ce rapport présente l'évaluation technique et financière exhaustive de la plateforme Ñkyel Studio, "
            "articulée autour du runtime agentique DeerFlow 2.0, de l'inspection visuelle multimodale DeepSeek Flash, "
            "du stockage persistant Cloudflare R2 et de la base Neon PostgreSQL. Les mesures de banc d'essai confirment "
            "un gain de débit de rendu de 8,4x grâce au compilateur natif Typst par rapport aux solutions Chromium "
            "headless, une conformité stricte aux exigences de souveraineté documentaire et une réduction du coût par "
            "délivrable professionnel de 62 %."
        ),
        sections=[
            # Page 1-2: Contexte & Souveraineté
            DocumentSection(
                id="sec_contexte",
                title="1. Contexte Stratégique et Impératifs de Souveraineté",
                level=1,
                page_break_before=False,
                key_metrics=[
                    {"label": "Gain Débit Compilation", "value": "+840 %"},
                    {"label": "Score Qualité Visuelle", "value": "99.2 %"},
                    {"label": "Réduction TCO 3 Ans", "value": "-62 %"}
                ],
                paragraphs=[
                    ParagraphBlock(
                        text=(
                            "Dans le paysage technologique actuel, la production automatisée de délivrables critiques "
                            "(rapports ministériels, mémos de conformité, notes de conjoncture financière) nécessite "
                            "une rupture avec les méthodes rudimentaires de conversion Markdown. Les organisations "
                            "exigent des garanties strictes de fidélité typographique, d'éditabilité pérenne et de "
                            "sécurité des flux de données."
                        ),
                        style="lead"
                    ),
                    ParagraphBlock(
                        text=(
                            "La doctrine de souveraineté mise en œuvre dans Ñkyel repose sur trois piliers fondamentaux : "
                            "premièrement, l'isolation étanche des environnements d'exécution au sein de bacs à sable E2B "
                            "temporaires ; deuxièmement, la persistance immuable des artéfacts au sein de compartiments "
                            "Cloudflare R2 chiffrés ; troisièmement, l'indexation relationnelle des métadonnées sous Neon PostgreSQL."
                        ),
                        style="normal"
                    ),
                    ParagraphBlock(
                        text=(
                            "Important : Aucun contenu propriétaire ou confidentiel n'est relayé vers des tiers non "
                            "habilités. L'auditabilité complète du code source (Typst, python-docx) garantit l'absence "
                            "d'effets de boîte noire dans le rendu graphique."
                        ),
                        style="callout"
                    )
                ]
            ),
            
            # Page 2-3: Architecture et Pipeline
            DocumentSection(
                id="sec_architecture",
                title="2. Architecture du Pipeline Documentaire Multi-Agents",
                level=1,
                page_break_before=True,
                paragraphs=[
                    ParagraphBlock(
                        text=(
                            "Le pipeline d'ingénierie d'artéfacts de Ñkyel intègre une boucle d'assurance qualité en boucle "
                            "fermée (Closed-Loop Quality Control). L'orchestrateur DeerFlow transforme la requête utilisateur "
                            "en une spécification intermédiaire structurée (DocumentSpec), décorrélant expressément la logique "
                            "sémantique des contraintes propres à chaque moteur de rendu."
                        ),
                        style="normal"
                    ),
                    ParagraphBlock(
                        text=(
                            "L'inspection visuelle automatique constitue l'innovation clé de cette directive : chaque page "
                            "compilée en image haute résolution est soumise au modèle multimodal DeepSeek Flash. Ce dernier "
                            "détecte les débordements de texte, les ruptures de colonnes ou les défauts de contraste, déclenchant "
                            "des micro-ajustements chirurgicaux sur le code source jusqu'à l'obtention d'une certification visuelle."
                        ),
                        style="normal"
                    ),
                    ParagraphBlock(
                        text="Points clés de l'architecture d'ingénierie :",
                        style="bullet"
                    ),
                    ParagraphBlock(
                        text="Découplage strict entre la représentation intermédiaire (IR DocumentSpec) et les compilateurs cibles.",
                        style="bullet"
                    ),
                    ParagraphBlock(
                        text="Compilation Typst vectorielle ultra-rapide en Rust intégrée dans l'espace utilisateur.",
                        style="bullet"
                    ),
                    ParagraphBlock(
                        text="Validation déterministe pré-vol (Magic bytes, signatures ZIP, intégrité des formules) avant inspection multimodale.",
                        style="bullet"
                    ),
                    ParagraphBlock(
                        text="Tolérance aux pannes : en cas d'indisponibilité momentanée du service visuel, le moteur déterministe garantit la livraison.",
                        style="bullet"
                    )
                ]
            ),

            # Page 3-4: Benchmarks et Tableaux
            DocumentSection(
                id="sec_benchmarks",
                title="3. Banc d'Essai Comparatif et Indicateurs de Performance",
                level=1,
                page_break_before=True,
                paragraphs=[
                    ParagraphBlock(
                        text=(
                            "Une campagne de tests intensifs a été conduite sur un échantillon standardisé de 250 documents "
                            "hétérogènes (de 4 à 50 pages). Les métriques collectées englobent la latence de bout en bout, "
                            "la consommation mémoire résidente, l'empreinte disque et l'indice de satisfaction typographique."
                        ),
                        style="normal"
                    )
                ],
                tables=[
                    TableData(
                        id="tbl_comparatif_moteurs",
                        title="Tableau 1 : Comparatif des Moteurs de Rendu Documentaire (Échantillon 2026)",
                        caption="Source : Banc d'essai automatisé Ñkyel Studio, exécution moyenne sur 100 itérations A4.",
                        columns=[
                            TableColumn(header="Moteur de Rendu", key="engine", width_ratio=1.4, alignment="left"),
                            TableColumn(header="Latence Moyenne (ms)", key="latency", width_ratio=1.1, alignment="right"),
                            TableColumn(header="RAM Résidente (Mo)", key="ram", width_ratio=1.0, alignment="right"),
                            TableColumn(header="Fidélité Typo (/100)", key="typo_score", width_ratio=1.1, alignment="center"),
                            TableColumn(header="Éditabilité Cible", key="editability", width_ratio=1.1, alignment="center")
                        ],
                        rows=[
                            {"engine": "Typst 0.15 Native (Ñkyel)", "latency": "62 ms", "ram": "28 Mo", "typo_score": "98.5", "editability": "Code Typst Natif"},
                            {"engine": "python-docx Word Native", "latency": "84 ms", "ram": "35 Mo", "typo_score": "94.0", "editability": "100% DOCX Éditable"},
                            {"engine": "Chromium / Puppeteer (HTML)", "latency": "520 ms", "ram": "340 Mo", "typo_score": "88.2", "editability": "Non (Statique)"},
                            {"engine": "LaTeX (pdfLaTeX Engine)", "latency": "1 150 ms", "ram": "115 Mo", "typo_score": "97.0", "editability": "Code TeX Complexe"},
                            {"engine": "LibreOffice Headless Mode", "latency": "2 400 ms", "ram": "480 Mo", "typo_score": "85.0", "editability": "Conversion Aléatoire"}
                        ]
                    )
                ]
            ),

            # Page 4-5: Recommandations & Conclusion
            DocumentSection(
                id="sec_conclusion",
                title="4. Analyse d'Impact et Recommandations de Déploiement",
                level=1,
                page_break_before=True,
                paragraphs=[
                    ParagraphBlock(
                        text=(
                            "Les résultats observés démontrent sans ambiguïté la supériorité opérationnelle du tandem Typst + python-docx "
                            "orchestré par Ñkyel Studio. Au-delà des gains de latence bruts, la préservation intégrale de l'éditabilité "
                            "des livrables (tableaux dynamiques, hiérarchie des styles Word, vectorisation PDF) répond rigoureusement "
                            "aux exigences de productivité des organisations clientes."
                        ),
                        style="normal"
                    ),
                    ParagraphBlock(
                        text=(
                            "Recommandation opérationnelle : Déployer le module artifact-engineer comme compétence par défaut "
                            "sur l'ensemble des missions à forte valeur ajoutée. L'activation de la boucle de vision multimodale "
                            "DeepSeek Flash en production garantit un taux de conformité visuelle supérieur à 98 % dès la première itération."
                        ),
                        style="callout"
                    ),
                    ParagraphBlock(
                        text=(
                            "Conclusion : Ñkyel Studio franchit un cap décisif dans l'autonomie agentique, positionnant l'IA non plus "
                            "comme un simple assistant textuel, mais comme un atelier éditorial et typographique complet de classe mondiale."
                        ),
                        style="lead"
                    )
                ]
            )
        ],
        citations=[
            Citation(
                id="ref_1",
                title="Typst Reference Manual & Memory Model (v0.15)",
                url="https://typst.app/docs",
                access_date="2026-10-27",
                notes="Documentation officielle du compilateur de documents Typst."
            ),
            Citation(
                id="ref_2",
                title="DeepSeek Multimodal Vision & Reasoning Technical Report",
                url="https://api.deepseek.com",
                access_date="2026-10-27",
                notes="Spécifications de l'API de vision pour l'analyse d'artéfacts."
            ),
            Citation(
                id="ref_3",
                title="Cloudflare R2 Object Storage Architecture Guide",
                url="https://developers.cloudflare.com/r2",
                access_date="2026-10-27",
                notes="Persistance géodistribuée sans frais de bande passante sortante."
            ),
            Citation(
                id="ref_4",
                title="SecNumCloud 3.2 : Recommandations de Souveraineté pour les Architectures d'Agents IA",
                url="https://cyber.gouv.fr",
                access_date="2026-10-27",
                notes="Guide de sécurisation des modèles et des bacs à sable d'exécution."
            )
        ]
    )


def main():
    print("=== DÉBUT TEST A : RAPPORT PROFESSIONNEL PDF + DOCX (4-5 PAGES) ===")
    spec = create_spec_a()
    
    # Save spec file
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    spec_file = OUTPUT_DIR / "spec_test_a.json"
    with open(spec_file, "w", encoding="utf-8") as f:
        f.write(spec.model_dump_json(indent=2))
    
    print(f"Spécification enregistrée : {spec_file}")
    
    # Run full pipeline with DeepSeek Vision QA and R2 sync
    result = run_pipeline(
        doc=spec,
        output_dir=OUTPUT_DIR,
        requested_formats=["pdf", "docx"],
        perform_vision_qa=True,
        max_correction_passes=2,
        sync_to_r2=True
    )

    print("\n=== RÉSULTATS DU PIPELINE TEST A ===")
    print(f"Document ID : {result['document_id']}")
    print(f"Formats générés : {list(result['deliverables'].keys())}")
    print(f"Fichier PDF : {result['deliverables'].get('pdf')}")
    print(f"Fichier DOCX : {result['deliverables'].get('docx')}")
    print(f"Nombre de pages PDF : {result.get('page_count')}")
    print(f"Nombre de prévisualisations : {len(result.get('page_previews', []))}")
    print(f"Validation déterministe : {result['deterministic_validation']}")
    print(f"Vision QA Effectuée : {result['vision_qa']['performed']}")
    print(f"Score Visuel Initial : {result['vision_qa']['initial_score']}")
    print(f"Score Visuel Final : {result['vision_qa']['final_score']}")
    print(f"Passes de correction : {result['vision_qa']['correction_passes']}")
    print(f"Corrections appliquées : {result['vision_qa']['corrections_applied']}")
    print(f"Synchronisation R2 : {result['r2_storage']}")


if __name__ == "__main__":
    main()
