"""
Loop de ejecucion persistente para agentes.
Corre por DURATION segundos revisando commands.json cada POLL segundos.
"""

import sys
import json
import time

AGENT = sys.argv[1]
COMMANDS_FILE = "commands.json"
DURATION = 90
POLL = 5


def run_command(agent: str, action: str) -> str:
    if agent == "agente-busqueda":
        if action == "buscar":
            from agents.job_search_agent import search_jobs
            jobs = search_jobs()
            with open("results_jobs.json", "w", encoding="utf-8") as f:
                json.dump(jobs, f, indent=2, ensure_ascii=False)
            return f"Encontradas {len(jobs)} ofertas. Guardadas en results_jobs.json"
        return f"Accion desconocida: {action}"

    elif agent == "agente-extractor":
        if action == "extraer":
            from agents.email_scraper_agent import extract_emails
            try:
                with open("results_jobs.json", encoding="utf-8") as f:
                    jobs = json.load(f)
            except FileNotFoundError:
                return "Error: ejecuta agente-busqueda primero"
            results = extract_emails(jobs)
            with open("results_emails.json", "w", encoding="utf-8") as f:
                json.dump(results, f, indent=2, ensure_ascii=False)
            found = sum(1 for j in results if j.get("email"))
            return f"Correos encontrados: {found}/{len(results)}. Guardados en results_emails.json"
        return f"Accion desconocida: {action}"

    elif agent == "agente-enviador":
        if action == "enviar":
            from agents.email_sender_agent import send_emails
            try:
                with open("results_emails.json", encoding="utf-8") as f:
                    jobs = json.load(f)
            except FileNotFoundError:
                return "Error: ejecuta agente-extractor primero"
            send_emails(jobs)
            return "Correos enviados."
        return f"Accion desconocida: {action}"

    return f"Agente desconocido: {agent}"


def ensure_slot():
    try:
        with open(COMMANDS_FILE, encoding="utf-8") as f:
            state = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        state = {}
    if AGENT not in state:
        state[AGENT] = {"action": None, "params": {}, "result": None}
        with open(COMMANDS_FILE, "w", encoding="utf-8") as f:
            json.dump(state, f, indent=2, ensure_ascii=False)


def main():
    ensure_slot()
    print(f"[{AGENT}] Activo — esperando comandos...", flush=True)
    deadline = time.time() + DURATION

    while time.time() < deadline:
        try:
            with open(COMMANDS_FILE, encoding="utf-8") as f:
                state = json.load(f)

            action = state.get(AGENT, {}).get("action")
            if action:
                print(f"[{AGENT}] Ejecutando: {action}", flush=True)
                result = run_command(AGENT, action)
                print(f"[{AGENT}] {result}", flush=True)
                state[AGENT]["action"] = None
                state[AGENT]["result"] = result
                with open(COMMANDS_FILE, "w", encoding="utf-8") as f:
                    json.dump(state, f, indent=2, ensure_ascii=False)

        except Exception as e:
            print(f"[{AGENT}] Error: {e}", flush=True)

        time.sleep(POLL)

    print(f"[{AGENT}] Ciclo terminado, reiniciando...", flush=True)


if __name__ == "__main__":
    main()
