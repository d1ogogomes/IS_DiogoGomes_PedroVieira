import subprocess
import time

def run_step(script_name, description):
    print(f"\n{'='*60}")
    print(f"PASSO: {description}")
    print(f"Executando: python {script_name}")
    print(f"{'='*60}\n")
    
    time.sleep(1)
    
    try:
        # Use local python interpreter
        subprocess.run(["./lrag_mac/bin/python", script_name], check=True)
    except subprocess.CalledProcessError as e:
        print(f"\nErro ao executar {script_name}: {e}")
        exit(1)

def main():
    print("\n" + "#"*60)
    print("DEMONSTRAÇÃO 1: Integração LogicRAG + Agente Autónomo IA")
    print("#"*60)
    
    # Fase 1: Visão -> Lógica -> Inglês (Lê os dados originais do KITTI)
    run_step("parse_kb_to_csv.py", "Fase de Perceção (LogicRAG): Traduzir Ficheiros Lógicos para Texto Natural")
    
    # Fase 2: Tomada de Decisão (API)
    run_step("driving_agent.py", "Agente LLM analisa as métricas de lógica e toma decisão de condução")
    
    print("\nDemonstração do LogicRAG concluída com sucesso!")

if __name__ == "__main__":
    main()
