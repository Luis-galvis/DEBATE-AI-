"""
CLI Principal: Consejo Económico de IA
Ejecuta el debate multi-agente de 7 rondas, la simulación macroeconómica, la optimización NSGA-III
y genera automáticamente los reportes (PDF/MD) y los activos para video en outputs/.
"""

import sys
import argparse
from pathlib import Path

# Configurar encoding seguro en consola Windows
if sys.stdout.encoding != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

ROOT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT_DIR))

from src.agents.orchestrator import DebateOrchestrator
from src.reporting.report_generator import SynthesisReportGenerator
from src.reporting.video_assets import (
    generate_key_moments_doc,
    generate_video_script_doc,
    export_video_charts,
)
from src.config import OUTPUTS_DIR

def main():
    parser = argparse.ArgumentParser(description="Consejo Económico de IA - Debate Multi-Agente & Simulación Macroeconómica")
    parser.add_argument("--country", type=str, default="colombia", choices=["colombia", "nordic", "usa"], help="País de calibración")
    parser.add_argument("--mode", type=str, default="record", choices=["record", "replay", "live"], help="Modo de ejecución LLM")
    parser.add_argument("--export-all", action="store_true", default=True, help="Exportar reportes PDF/MD, momentos clave y gráficos")
    args = parser.parse_args()

    print("=" * 70)
    print("🏛️  CONSEJO ECONÓMICO DE IA — DEBATE Y SIMULACIÓN MACROECONÓMICA")
    print(f"📍 País de Calibración: {args.country.upper()} | Modo LLM: {args.mode.upper()}")
    print("=" * 70)

    # 1. Ejecutar Orquestador de 7 Rondas
    orchestrator = DebateOrchestrator(calibration_country=args.country, execution_mode=args.mode)
    print("\n[1/7] Ejecutando Ronda 1: Apertura y Presentación de Modelos...")
    r1 = orchestrator.run_round_1_opening()

    print("\n[2/7] Ejecutando Ronda 2: Simulación Base a 30 Años y Steelman...")
    r2 = orchestrator.run_round_2_baseline_sim()

    print("\n[3/7] Ejecutando Ronda 3: Contrainterrogatorio Cruzado...")
    r3 = orchestrator.run_round_3_cross_examination()

    print("\n[4/7] Ejecutando Ronda 4: Pruebas de Estrés Macroeconómico (Monte Carlo)...")
    r4 = orchestrator.run_round_4_stress_shocks()

    print("\n[5/7] Ejecutando Ronda 5: Concesiones y Líneas Rojas (Vetos)...")
    r5 = orchestrator.run_round_5_concessions()

    print("\n[6/7] Ejecutando Ronda 6: Ajuste de Vectores de Política y Re-simulación...")
    r6 = orchestrator.run_round_6_parameter_adjustments()

    print("\n[7/7] Ejecutando Ronda 7: Optimización NSGA-III, Síntesis Pareto y Votación...")
    r7 = orchestrator.run_round_7_synthesis_and_naming()

    # 2. Generar Reportes y Entregables
    if args.export_all and orchestrator.synthesis_proposal and orchestrator.synthesis_result:
        print("\n" + "=" * 70)
        print("📄 GENERANDO ENTREGABLES Y ACTIVOS DE DIVULGACIÓN")
        print("=" * 70)

        rep_gen = SynthesisReportGenerator(
            proposal=orchestrator.synthesis_proposal,
            synthesis_data=orchestrator.synthesis_result,
            calibration_country=args.country.capitalize(),
            autonomous_verdict=orchestrator.autonomous_verdict,
        )
        md_file = rep_gen.export_markdown_file()
        print(f"  [OK] Reporte Markdown: {md_file.name}")

        try:
            pdf_file = rep_gen.export_pdf_file()
            print(f"  [OK] Reporte PDF:      {pdf_file.name}")
        except Exception as e:
            print(f"  [WARN] PDF no compilado: {e}")

        km_file = generate_key_moments_doc()
        print(f"  [OK] Momentos Clave:   {km_file.name}")

        vs_file = generate_video_script_doc()
        print(f"  [OK] Guion de Video:   {vs_file.name}")

        export_video_charts()
        print("  [OK] Figuras PNG (300 DPI) y SVG exportadas en outputs/")

    print("\n" + "=" * 70)
    print("🏆 RESULTADO FINAL DE LA SÍNTESIS")
    print(f"   Modelo Consensuado: {orchestrator.synthesis_proposal.model_name}")
    print(f"   Tagline: {orchestrator.synthesis_proposal.tagline}")
    syn_m = orchestrator.synthesis_result['synthesized_metrics']
    print(f"   PIB pc Terminal: ${syn_m.get('terminal_gdp_pc', 0):,.1f} | Desempleo Prom: {syn_m.get('unemployment_avg', 5.1):.1f}% | Recaudo Fiscal: {syn_m.get('tax_revenue_gdp_avg', 34.2):.1f}% PIB")
    print(f"   Gini Promedio: {syn_m.get('gini_avg', 0):.3f} | Deuda Máx: {syn_m.get('max_debt_gdp', 0):.1f}% | Bienestar: {syn_m.get('social_welfare_index', 0):.1f}/100")
    if orchestrator.autonomous_verdict:
        print(f"\n⚖️  VEREDICTO AUTÓNOMO DEL ÁRBITRO:")
        print(f"   Modelo Elegido: {orchestrator.autonomous_verdict.chosen_model}")
        print(f"   Justificación: {orchestrator.autonomous_verdict.detailed_verdict_text[:120]}...")
    print("=" * 70)
    print("\nPara explorar interactivamente en Streamlit ejecuta:")
    print("  streamlit run src/app/dashboard.py\n")

if __name__ == "__main__":
    main()
