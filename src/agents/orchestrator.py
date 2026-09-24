"""
Orquestador Principal del Debate Macroeconómico de 7 Rondas.
Coordina el flujo de estados entre los tres agentes debatientes, el motor de simulación,
el optimizador NSGA-III y el Árbitro-Auditor, guardando logs reproducibles en JSON.
"""

import time
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional, Generator

from src.config import OUTPUTS_DIR, RANDOM_SEED
from src.simulation.policy_vector import (
    PolicyVector,
    CAPITALIST_INITIAL_VECTOR,
    COLLECTIVIST_INITIAL_VECTOR,
    SOCDEM_INITIAL_VECTOR,
)
from src.simulation.solow_engine import MacroEconomy
from src.simulation.shocks import ALL_SCENARIOS, get_scenario_shocks
from src.simulation.metrics import calculate_metrics
from src.simulation.monte_carlo import run_monte_carlo
from src.optimization.pareto_optimizer import run_pareto_optimization
from src.optimization.synthesis import synthesize_midpoint
from src.optimization.robustness import analyze_midpoint_robustness
from src.agents.debaters import CapitalistDebater, CollectivistDebater, SocdemDebater
from src.agents.referee import RefereeAuditor
from src.agents.schemas import (
    PolicyVectorSchema,
    RefereeTurnEvaluation,
    SynthesisModelProposal,
    RefereeAutonomousVerdict,
)
from data.data_loader import load_calibration_profile

class DebateOrchestrator:
    """
    Controlador de la sesión de debate multi-agente estructurado en 7 rondas.
    """

    def __init__(
        self,
        calibration_country: str = "colombia",
        execution_mode: str = "record",
    ):
        self.calibration_country = calibration_country
        self.calibration_data = load_calibration_profile(calibration_country)
        self.execution_mode = execution_mode

        # Instanciar agentes
        self.capitalist = CapitalistDebater(execution_mode=execution_mode)
        self.collectivist = CollectivistDebater(execution_mode=execution_mode)
        self.socdem = SocdemDebater(execution_mode=execution_mode)
        self.referee = RefereeAuditor(execution_mode=execution_mode)

        # Vectores de política vigentes
        self.vectors = {
            "capitalist": CAPITALIST_INITIAL_VECTOR,
            "collectivist": COLLECTIVIST_INITIAL_VECTOR,
            "socdem": SOCDEM_INITIAL_VECTOR,
        }

        # Estado del debate y bitácora estructurada
        self.session_id = f"debate_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.history: List[Dict[str, Any]] = []
        self.simulation_results_by_round: Dict[int, Any] = {}
        self.evaluations_by_round: Dict[int, List[RefereeTurnEvaluation]] = {}
        self.synthesis_result: Optional[Dict[str, Any]] = None
        self.synthesis_proposal: Optional[SynthesisModelProposal] = None
        self.autonomous_verdict: Optional[RefereeAutonomousVerdict] = None

    def _build_context_summary(self) -> str:
        """Comprime el historial del debate para no sobrecargar el contexto del LLM."""
        if not self.history:
            return "Inicio del debate. No hay rondas previas."
        summary_lines = []
        for entry in self.history[-6:]:
            speaker = entry.get("speaker", "Agente")
            rnd = entry.get("round", 0)
            text_preview = entry.get("content", "")[:180].replace("\n", " ")
            summary_lines.append(f"[Ronda {rnd} | {speaker}]: {text_preview}...")
        return "\n".join(summary_lines)

    def run_round_1_opening(self) -> Dict[str, Any]:
        """Ronda 1: Apertura y Presentación de Modelos Fundamentados."""
        round_num = 1
        title = "Apertura y Tesis Fundamental"
        instructions = (
            f"Presenta tu modelo económico inicial y tus fundamentos teóricos (Hayek/Friedman vs Marx/Lange vs Keynes/Piketty) "
            f"para el contexto de {self.calibration_country.upper()}. Expón los 10 parámetros de tu vector de política económica, "
            f"justificando cuantitativamente el canal de transmisión mediante el cual tu propuesta generará inversión productiva, "
            f"abordará la informalidad estructural y garantizará la sostenibilidad macroeconómica sin quebrar las finanzas del Estado."
        )

        turn_logs = []
        sim_data = {"country_calibration": self.calibration_data}
        context = self._build_context_summary()

        for agent in [self.capitalist, self.collectivist, self.socdem]:
            speech, _, _ = agent.generate_turn(
                round_number=round_num,
                round_title=title,
                round_instruction=instructions,
                sim_data=sim_data,
                context_summary=context,
            )
            eval_result = self.referee.audit_and_score_turn(
                round_number=round_num,
                agent_name=agent.name,
                speech_text=speech,
                sim_data=sim_data,
                current_policy=agent.current_vector,
            )
            turn_entry = {
                "round": round_num,
                "title": title,
                "speaker": agent.name,
                "content": speech,
                "vector": agent.current_vector.to_dict(),
                "evaluation": eval_result.model_dump(),
            }
            self.history.append(turn_entry)
            turn_logs.append(turn_entry)

        return {"round": round_num, "title": title, "turns": turn_logs}

    def run_round_2_baseline_sim(self) -> Dict[str, Any]:
        """Ronda 2: Simulación Base a 30 Años y Reconocimiento de Debilidades."""
        round_num = 2
        title = "Simulación Base a 30 Años y Admisión de Fallos"

        # 1. Ejecutar simulación base para los tres vectores
        sim_metrics = {}
        for key, agent in [("capitalist", self.capitalist), ("collectivist", self.collectivist), ("socdem", self.socdem)]:
            econ = MacroEconomy(policy=agent.current_vector, calibration=self.calibration_data, years=30)
            res = econ.simulate()
            sim_metrics[agent.name] = calculate_metrics(res)

        self.simulation_results_by_round[round_num] = sim_metrics

        instructions = (
            "Analiza las trayectorias de 30 años proyectadas por el simulador macroeconómico "
            "(PIB per cápita terminal, Gini, desempleo, deuda/PIB e informalidad). "
            "Reglas obligatorias: (1) Aplica STEELMAN al modelo rival (resume con total honestidad intelectual su argumento más fuerte); "
            "y (2) Reconoce OBLIGATORIAMENTE 2 debilidades intrínsecas o vulnerabilidades críticas de tu propio sistema evidenciadas por las cifras."
        )

        turn_logs = []
        context = self._build_context_summary()

        for agent in [self.capitalist, self.collectivist, self.socdem]:
            speech, _, _ = agent.generate_turn(
                round_number=round_num,
                round_title=title,
                round_instruction=instructions,
                sim_data=sim_metrics,
                context_summary=context,
            )
            eval_result = self.referee.audit_and_score_turn(
                round_number=round_num,
                agent_name=agent.name,
                speech_text=speech,
                sim_data=sim_metrics,
                current_policy=agent.current_vector,
            )
            turn_entry = {
                "round": round_num,
                "title": title,
                "speaker": agent.name,
                "content": speech,
                "simulation_metrics": sim_metrics,
                "evaluation": eval_result.model_dump(),
            }
            self.history.append(turn_entry)
            turn_logs.append(turn_entry)

        return {"round": round_num, "title": title, "sim_metrics": sim_metrics, "turns": turn_logs}

    def run_round_3_cross_examination(self) -> Dict[str, Any]:
        """Ronda 3: Contrainterrogatorio Cruzado (Preguntas Incómodas con Datos)."""
        round_num = 3
        title = "Contrainterrogatorio Cruzado"
        sim_metrics = self.simulation_results_by_round.get(2, {})

        instructions = (
            "Formula 2 preguntas técnicas incómodas y fundamentadas a cada uno de tus 2 rivales, "
            "atacando frontalmente las contradicciones matemáticas reveladas en la simulación: "
            "fuga de capitales e insolvencia fiscal en el colectivismo, precarización laboral y desigualdad sin red en el capitalismo, "
            "y sobrecostos asfixiantes sobre MiPyMEs en la socialdemocracia."
        )

        turn_logs = []
        context = self._build_context_summary()

        for agent in [self.capitalist, self.collectivist, self.socdem]:
            speech, _, _ = agent.generate_turn(
                round_number=round_num,
                round_title=title,
                round_instruction=instructions,
                sim_data=sim_metrics,
                context_summary=context,
            )
            eval_result = self.referee.audit_and_score_turn(
                round_number=round_num,
                agent_name=agent.name,
                speech_text=speech,
                sim_data=sim_metrics,
                current_policy=agent.current_vector,
            )
            turn_entry = {
                "round": round_num,
                "title": title,
                "speaker": agent.name,
                "content": speech,
                "evaluation": eval_result.model_dump(),
            }
            self.history.append(turn_entry)
            turn_logs.append(turn_entry)

        return {"round": round_num, "title": title, "turns": turn_logs}

    def run_round_4_stress_shocks(self) -> Dict[str, Any]:
        """Ronda 4: Choques de Estrés (Monte Carlo) y Falsabilidad."""
        round_num = 4
        title = "Pruebas de Estrés Macroeconómico y Falsabilidad"

        # Correr Monte Carlo en el choque de pandemia y recesión global
        stress_results = {}
        for key, agent in [("capitalist", self.capitalist), ("collectivist", self.collectivist), ("socdem", self.socdem)]:
            mc_pand = run_monte_carlo(agent.current_vector, scenario_name="pandemic", runs=40, seed=RANDOM_SEED)
            mc_rec = run_monte_carlo(agent.current_vector, scenario_name="global_recession", runs=40, seed=RANDOM_SEED)
            stress_results[agent.name] = {
                "pandemic_resilience": mc_pand["summary_metrics"]["resilience_score"],
                "pandemic_max_drawdown": mc_pand["summary_metrics"]["max_drawdown"],
                "recession_terminal_gdp": mc_rec["summary_metrics"]["terminal_gdp_pc"],
                "recession_debt_gdp": mc_rec["summary_metrics"]["max_debt_gdp"],
            }

        self.simulation_results_by_round[round_num] = stress_results

        instructions = (
            "Interpreta los resultados de estrés de Monte Carlo ante pandemia global y recesión externa. "
            "Explica cómo absorbe tu modelo el choque y declara explícitamente tu CRITERIO DE FALSABILIDAD: "
            "¿Qué umbral numérico específico de caída del PIB, disparo de deuda o desempleo te obligaría a aceptar "
            "que tu sistema ha fracasado y que tu contraparte tiene la razón?"
        )

        turn_logs = []
        context = self._build_context_summary()

        for agent in [self.capitalist, self.collectivist, self.socdem]:
            speech, _, _ = agent.generate_turn(
                round_number=round_num,
                round_title=title,
                round_instruction=instructions,
                sim_data=stress_results,
                context_summary=context,
            )
            eval_result = self.referee.audit_and_score_turn(
                round_number=round_num,
                agent_name=agent.name,
                speech_text=speech,
                sim_data=stress_results,
                current_policy=agent.current_vector,
            )
            turn_entry = {
                "round": round_num,
                "title": title,
                "speaker": agent.name,
                "content": speech,
                "stress_metrics": stress_results,
                "evaluation": eval_result.model_dump(),
            }
            self.history.append(turn_entry)
            turn_logs.append(turn_entry)

        return {"round": round_num, "title": title, "stress_metrics": stress_results, "turns": turn_logs}

    def run_round_5_concessions(self) -> Dict[str, Any]:
        """Ronda 5: Concesiones y Líneas Rojas No Negociables."""
        round_num = 5
        title = "Concesiones Explícitas y Líneas Rojas"

        instructions = (
            "A la luz de los choques macroeconómicos y la evidencia cuantitativa, declara con precisión qué políticas "
            "estás dispuesto a CEDER (movimiento explícito en parámetros) y cuáles son tus LÍNEAS ROJAS NO NEGOCIABLES (vetos absolutos). "
            "Detalla cómo tu flexibilización permite destrabar un pacto nacional viable para el país."
        )

        turn_logs = []
        context = self._build_context_summary()
        sim_data = self.simulation_results_by_round.get(4, {})

        for agent in [self.capitalist, self.collectivist, self.socdem]:
            speech, _, _ = agent.generate_turn(
                round_number=round_num,
                round_title=title,
                round_instruction=instructions,
                sim_data=sim_data,
                context_summary=context,
            )
            eval_result = self.referee.audit_and_score_turn(
                round_number=round_num,
                agent_name=agent.name,
                speech_text=speech,
                sim_data=sim_data,
                current_policy=agent.current_vector,
            )
            turn_entry = {
                "round": round_num,
                "title": title,
                "speaker": agent.name,
                "content": speech,
                "evaluation": eval_result.model_dump(),
            }
            self.history.append(turn_entry)
            turn_logs.append(turn_entry)

        return {"round": round_num, "title": title, "turns": turn_logs}

    def run_round_6_parameter_adjustments(self) -> Dict[str, Any]:
        """Ronda 6: Ajuste de Vectores de Política y Re-simulación Dinámica."""
        round_num = 6
        title = "Ajuste de Vectores de Política"

        # Vectores reformados adaptados dinámicamente según el perfil del país
        c_code = self.calibration_country.lower()
        if c_code == "nordic":
            # Calibración nórdica: alta base impositiva y alta desmercantilización
            self.capitalist.current_vector = PolicyVector([0.15, 0.35, 0.50, 0.30, 0.55, 0.35, 0.40, 0.88, 0.85, 0.90])
            self.collectivist.current_vector = PolicyVector([0.45, 0.65, 0.80, 0.52, 0.80, 0.60, 0.60, 0.65, 0.70, 0.60])
            self.socdem.current_vector = PolicyVector([0.30, 0.55, 0.70, 0.45, 0.75, 0.55, 0.55, 0.85, 0.80, 0.85])
        elif c_code == "usa":
            # Calibración USA: mayor énfasis en mercado y flexibilidad de capitales
            self.capitalist.current_vector = PolicyVector([0.08, 0.22, 0.30, 0.18, 0.30, 0.20, 0.25, 0.92, 0.88, 0.92])
            self.collectivist.current_vector = PolicyVector([0.50, 0.50, 0.65, 0.40, 0.65, 0.58, 0.60, 0.60, 0.60, 0.55])
            self.socdem.current_vector = PolicyVector([0.22, 0.40, 0.55, 0.32, 0.58, 0.45, 0.50, 0.82, 0.75, 0.85])
        else:
            # Calibración Colombia / Emergente: adaptación a 56% informalidad y fondo de commodities
            self.capitalist.current_vector = PolicyVector([0.12, 0.28, 0.38, 0.24, 0.40, 0.28, 0.32, 0.88, 0.85, 0.88])
            self.collectivist.current_vector = PolicyVector([0.55, 0.52, 0.68, 0.42, 0.68, 0.62, 0.62, 0.58, 0.60, 0.52])
            self.socdem.current_vector = PolicyVector([0.26, 0.46, 0.62, 0.36, 0.66, 0.50, 0.54, 0.82, 0.75, 0.85])

        # Re-simular vectores ajustados
        adjusted_sim = {}
        for agent in [self.capitalist, self.collectivist, self.socdem]:
            econ = MacroEconomy(policy=agent.current_vector, calibration=self.calibration_data, years=30)
            res = econ.simulate()
            adjusted_sim[agent.name] = calculate_metrics(res)

        self.simulation_results_by_round[round_num] = adjusted_sim

        instructions = (
            "Presenta tu vector de parámetros AJUSTADO tras las concesiones mutuas. "
            "Justifica con los nuevos datos cuantitativos de la re-simulación por qué tu postura reformada "
            "supera con creces a tu punto de partida original en estabilidad, bienestar y reducción de brechas sociales."
        )

        turn_logs = []
        context = self._build_context_summary()

        for agent in [self.capitalist, self.collectivist, self.socdem]:
            speech, _, _ = agent.generate_turn(
                round_number=round_num,
                round_title=title,
                round_instruction=instructions,
                sim_data=adjusted_sim,
                context_summary=context,
            )
            eval_result = self.referee.audit_and_score_turn(
                round_number=round_num,
                agent_name=agent.name,
                speech_text=speech,
                sim_data=adjusted_sim,
                current_policy=agent.current_vector,
            )
            turn_entry = {
                "round": round_num,
                "title": title,
                "speaker": agent.name,
                "content": speech,
                "adjusted_vector": agent.current_vector.to_dict(),
                "metrics": adjusted_sim[agent.name],
                "evaluation": eval_result.model_dump(),
            }
            self.history.append(turn_entry)
            turn_logs.append(turn_entry)

        return {"round": round_num, "title": title, "adjusted_metrics": adjusted_sim, "turns": turn_logs}

    def run_round_7_synthesis_and_naming(self) -> Dict[str, Any]:
        """Ronda 7: Síntesis Pareto (NSGA-III), Borda, Vetos y Nombramiento."""
        round_num = 7
        title = "Síntesis de Pareto, Bautismo del Modelo y Votación"

        # 1. Optimización multiobjetivo con NSGA-III
        opt_results = run_pareto_optimization(
            algorithm_name="nsga3",
            pop_size=50,
            n_gen=30,
            seed=RANDOM_SEED,
            calibration=self.calibration_data,
        )

        # 2. Selección del punto medio robusto (TOPSIS, Nash, Euclídeo + Vetos)
        synthesis = synthesize_midpoint(opt_results)
        self.synthesis_result = synthesis

        # 3. Análisis de sensibilidad y robustez del punto medio
        robustness = analyze_midpoint_robustness(
            pareto_F_natural=opt_results["pareto_F_natural"],
            pareto_X=opt_results["pareto_X"],
            n_perturbations=50,
            seed=RANDOM_SEED,
        )
        synthesis["robustness"] = robustness

        # 4. El Árbitro redacta el documento de síntesis y bautiza el modelo
        concessions_summary = self._build_context_summary()
        proposal = self.referee.draft_synthesis_model(
            pareto_synthesis_data=synthesis,
            capitalist_vector=self.capitalist.current_vector,
            collectivist_vector=self.collectivist.current_vector,
            socdem_vector=self.socdem.current_vector,
            concessions_summary=concessions_summary,
        )
        self.synthesis_proposal = proposal

        # 4b. El Árbitro emite su veredicto autónomo e independiente
        # Simulamos los 3 vectores puros para tener sus métricas exactas
        sim_pure = {}
        for agent in [self.capitalist, self.collectivist, self.socdem]:
            econ_pure = MacroEconomy(policy=agent.current_vector, calibration=self.calibration_data, years=30)
            res_pure = econ_pure.simulate()
            sim_pure[agent.name] = calculate_metrics(res_pure)

        self.autonomous_verdict = self.referee.generate_autonomous_verdict(
            capitalist_metrics=sim_pure.get(self.capitalist.name),
            collectivist_metrics=sim_pure.get(self.collectivist.name),
            socdem_metrics=sim_pure.get(self.socdem.name),
        )

        # 5. Votación y discursos finales de los tres agentes
        final_votes = {}
        turn_logs = []
        for agent in [self.capitalist, self.collectivist, self.socdem]:
            inst = (
                f"El optimizador NSGA-III y el Árbitro han formulado el modelo de síntesis: '{proposal.model_name}'.\n"
                f"Tagline: {proposal.tagline}\n"
                f"Vector resultante: {synthesis['vector_values']}\n"
                f"Métricas esperadas: PIB pc={synthesis['synthesized_metrics']['terminal_gdp_pc']}, Gini={synthesis['synthesized_metrics']['gini_avg']}.\n"
                f"Emite tu voto final justificado (Acepto con observaciones / Veto), analizando qué elementos de tu filosofía están presentes."
            )
            speech, _, _ = agent.generate_turn(
                round_number=round_num,
                round_title=title,
                round_instruction=inst,
                sim_data=synthesis["synthesized_metrics"],
                context_summary=concessions_summary,
            )
            turn_entry = {
                "round": round_num,
                "title": title,
                "speaker": agent.name,
                "content": speech,
            }
            self.history.append(turn_entry)
            turn_logs.append(turn_entry)

        synthesis_package = {
            "round": round_num,
            "title": title,
            "proposal": proposal.model_dump(),
            "autonomous_verdict": self.autonomous_verdict.model_dump() if self.autonomous_verdict else None,
            "pareto_optimization": {
                "algorithm": opt_results["algorithm"],
                "total_time_seconds": opt_results["total_time_seconds"],
                "pareto_solutions_count": opt_results["pareto_solutions_count"],
            },
            "synthesis_metrics": synthesis["synthesized_metrics"],
            "robustness": robustness,
            "agent_utilities": synthesis["agent_utilities"],
            "turns": turn_logs,
        }

        # Guardar sesión completa en JSON
        self._save_session_json()

        return synthesis_package

    def run_all_rounds(self) -> Dict[str, Any]:
        """Ejecuta las 7 rondas de manera secuencial."""
        r1 = self.run_round_1_opening()
        r2 = self.run_round_2_baseline_sim()
        r3 = self.run_round_3_cross_examination()
        r4 = self.run_round_4_stress_shocks()
        r5 = self.run_round_5_concessions()
        r6 = self.run_round_6_parameter_adjustments()
        r7 = self.run_round_7_synthesis_and_naming()

        return {
            "session_id": self.session_id,
            "calibration_country": self.calibration_country,
            "rounds": [r1, r2, r3, r4, r5, r6, r7],
            "synthesis": self.synthesis_result,
            "proposal": self.synthesis_proposal.model_dump() if self.synthesis_proposal else None,
            "autonomous_verdict": self.autonomous_verdict.model_dump() if self.autonomous_verdict else None,
        }

    def _save_session_json(self):
        """Guarda la transcripción estructurada en JSON para reproducibilidad."""
        file_path = OUTPUTS_DIR / f"{self.session_id}.json"
        payload = {
            "session_id": self.session_id,
            "timestamp": datetime.now().isoformat(),
            "calibration_country": self.calibration_country,
            "history": self.history,
            "synthesis": self.synthesis_result["synthesized_metrics"] if self.synthesis_result else {},
            "proposal": self.synthesis_proposal.model_dump() if self.synthesis_proposal else {},
            "autonomous_verdict": self.autonomous_verdict.model_dump() if self.autonomous_verdict else {},
        }
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(payload, f, indent=2, ensure_ascii=False)
        # También guardar como debate_session_latest.json
        latest_path = OUTPUTS_DIR / "debate_session_latest.json"
        with open(latest_path, "w", encoding="utf-8") as f:
            json.dump(payload, f, indent=2, ensure_ascii=False)

