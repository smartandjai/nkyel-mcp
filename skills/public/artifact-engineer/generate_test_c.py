"""Acceptance Test C: Structured Multi-Sheet XLSX Workbook with Verified Formulas and Formatting."""

import json
from pathlib import Path
import sys

sys.path.append(str(Path(__file__).resolve().parent / "scripts"))

from document_spec import (
    DocumentSpec,
    SheetData,
    SheetColumn
)
from artifact_pipeline import run_pipeline

OUTPUT_DIR = Path(__file__).resolve().parents[3] / "artifacts_demo/test_c_workbook"


def create_spec_c() -> DocumentSpec:
    return DocumentSpec(
        document_id="modele_financier_tco_nkyel_2026",
        document_type="workbook",
        title="Modèle Financier & TCO Prévisionnel : Infrastructure Souveraine Ñkyel (2026-2029)",
        subtitle="Analyse Comparée des Coûts d'Inférence, Stockage R2 et Bacs à Sable E2B",
        author="Direction Financière & Architecture Cloud",
        organization="Ñkyel Studio · SmartANDJ AI Technologies",
        date="27 Octobre 2026",
        language="fr",
        style_preset="data_workbook",
        sheets=[
            # Feuille 1 : Analyse TCO Annuel sur 3 ans
            SheetData(
                name="Synthèse TCO 3 Ans",
                columns=[
                    SheetColumn(header="Poste d'Infrastructure", key="component", width=28, number_format="@"),
                    SheetColumn(header="Coût Annuel Ñkyel (€)", key="cost_nkyel", width=22, number_format="currency"),
                    SheetColumn(header="Coût Cloud Propriétaire (€)", key="cost_legacy", width=25, number_format="currency"),
                    SheetColumn(header="Économie Nette (€)", key="savings", width=20, number_format="currency"),
                    SheetColumn(header="Pourcentage d'Économie", key="pct_savings", width=22, number_format="percentage"),
                ],
                rows=[
                    {
                        "component": "Bacs à Sable E2B / Execution",
                        "cost_nkyel": 4800.00,
                        "cost_legacy": 14400.00,
                        "savings": 9600.00,
                        "pct_savings": 0.667
                    },
                    {
                        "component": "Stockage d'Artéfacts (R2 vs S3)",
                        "cost_nkyel": 360.00,
                        "cost_legacy": 2880.00,
                        "savings": 2520.00,
                        "pct_savings": 0.875
                    },
                    {
                        "component": "Inférence & Vision QA (DeepSeek)",
                        "cost_nkyel": 2100.00,
                        "cost_legacy": 9600.00,
                        "savings": 7500.00,
                        "pct_savings": 0.781
                    },
                    {
                        "component": "Base Relationnelle (Neon vs RDS)",
                        "cost_nkyel": 1200.00,
                        "cost_legacy": 3600.00,
                        "savings": 2400.00,
                        "pct_savings": 0.667
                    },
                    {
                        "component": "Bande Passante Sortante (Egress)",
                        "cost_nkyel": 0.00,
                        "cost_legacy": 4200.00,
                        "savings": 4200.00,
                        "pct_savings": 1.000
                    }
                ],
                has_total_row=True,
                freeze_panes="A2"
            ),

            # Feuille 2 : Métriques de Latence et Rendement des Moteurs
            SheetData(
                name="Banc d'Essai Rendu Typst",
                columns=[
                    SheetColumn(header="Moteur Documentaire", key="engine", width=26, number_format="@"),
                    SheetColumn(header="Débit Moyen (req/min)", key="throughput", width=22, number_format="integer"),
                    SheetColumn(header="Latence Médiane (ms)", key="latency_p50", width=20, number_format="integer"),
                    SheetColumn(header="Latence P99 (ms)", key="latency_p99", width=18, number_format="integer"),
                    SheetColumn(header="Empreinte RAM (Mo)", key="ram_mb", width=20, number_format="float"),
                    SheetColumn(header="Taux de Succès (%)", key="success_rate", width=18, number_format="percentage"),
                ],
                rows=[
                    {
                        "engine": "Typst 0.15 Native (Ñkyel)",
                        "throughput": 850,
                        "latency_p50": 62,
                        "latency_p99": 115,
                        "ram_mb": 28.4,
                        "success_rate": 0.999
                    },
                    {
                        "engine": "python-docx Word Native",
                        "throughput": 620,
                        "latency_p50": 84,
                        "latency_p99": 140,
                        "ram_mb": 34.8,
                        "success_rate": 0.998
                    },
                    {
                        "engine": "python-pptx Native",
                        "throughput": 480,
                        "latency_p50": 95,
                        "latency_p99": 165,
                        "ram_mb": 32.1,
                        "success_rate": 0.996
                    },
                    {
                        "engine": "openpyxl Native Engine",
                        "throughput": 550,
                        "latency_p50": 78,
                        "latency_p99": 130,
                        "ram_mb": 29.5,
                        "success_rate": 0.999
                    },
                    {
                        "engine": "Chromium Headless Mode",
                        "throughput": 95,
                        "latency_p50": 520,
                        "latency_p99": 1200,
                        "ram_mb": 340.0,
                        "success_rate": 0.975
                    }
                ],
                has_total_row=True,
                freeze_panes="A2"
            )
        ]
    )


def main():
    print("=== DÉBUT TEST C : CLASSEUR MULTI-FEUILLES ÉDITABLE XLSX ===")
    spec = create_spec_c()
    
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    spec_file = OUTPUT_DIR / "spec_test_c.json"
    with open(spec_file, "w", encoding="utf-8") as f:
        f.write(spec.model_dump_json(indent=2))
    
    print(f"Spécification enregistrée : {spec_file}")
    
    result = run_pipeline(
        doc=spec,
        output_dir=OUTPUT_DIR,
        requested_formats=["xlsx"],
        perform_vision_qa=False,
        sync_to_r2=True
    )

    print("\n=== RÉSULTATS DU PIPELINE TEST C ===")
    print(f"Document ID : {result['document_id']}")
    print(f"Fichier XLSX généré : {result['deliverables'].get('xlsx')}")
    print(f"Nombre de feuilles : {result.get('sheet_count')}")
    print(f"Validation déterministe : {result['deterministic_validation']}")
    print(f"Synchronisation R2 : {result['r2_storage']}")


if __name__ == "__main__":
    main()
