import os
import glob
import csv
import re

def translate_kb_to_natural_language(kb_path):
    """Lê um ficheiro KB gerado pelo LogicRAG e extrai os predicates mais importantes para linguagem natural."""
    try:
        with open(kb_path, 'r', encoding='utf-8') as f:
            lines = [line.strip() for line in f.readlines() if line.strip() and not line.startswith('(')]
            
        facts = []
        pedestrians = []
        vehicles = []
        
        # 1. Encontrar todos os peões e veículos
        for line in lines:
            if line.startswith("Pedestrian("):
                ped = line.replace("Pedestrian(", "").replace(")", "")
                pedestrians.append(ped)
            elif line.startswith("Vehicles("):
                veh = line.replace("Vehicles(", "").replace(")", "")
                vehicles.append(veh)

        # 2. Procurar eventos críticos para os peões e veículos
        for ped in pedestrians:
            is_moving = False
            location = "Unknown"
            
            for line in lines:
                if line == f"Moving({ped})":
                    is_moving = True
                if line.startswith(f"LastLocation({ped},"):
                    # Extrair localização: LastLocation(Pedestrian_744, NearRight)
                    match = re.search(r"LastLocation\([^,]+,\s*([^)]+)\)", line)
                    if match:
                        location = match.group(1)
            
            # Ver se o peão está a aproximar-se do Ego (geralmente Vehicles_0 ou similar)
            is_getting_closer = False
            for veh in vehicles:
                if f"DistanceDecrease({ped}, {veh})" in lines or f"DistanceDecrease({veh}, {ped})" in lines:
                    is_getting_closer = True
                    break
                    
            status = "Moving" if is_moving else "Standing"
            action = "getting closer to a vehicle" if is_getting_closer else "maintaining distance"
            
            facts.append(f"{ped} detected at {location}. Status: {status} and {action}.")
            
        if not facts:
            return "Clear road ahead. No significant pedestrian or vehicle threats detected."
            
        return " | ".join(facts)

    except Exception as e:
        return f"Error parsing KB: {e}"

def main():
    print("Convertendo logs reais do LogicRAG (KB) para o formato do System 2...")
    
    # Procurar a pasta com os KBs
    kb_dir = "LogicRAG_Data/precomputed_knowledge_base/kb_out_kitti"
    
    if not os.path.exists(kb_dir):
        print(f"Erro: Pasta {kb_dir} não encontrada.")
        return
        
    # Encontrar todos os ficheiros .txt gerados (KB windows)
    kb_files = glob.glob(f"{kb_dir}/*/*.txt")
    if not kb_files:
        print("Erro: Nenhum ficheiro KB encontrado.")
        return
        
    # Ordenar por nome para simular uma sequência temporal e processar os primeiros 5 ficheiros
    kb_files.sort()
    
    # Prepara o CSV de saída
    with open('resultados_kitti.csv', 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(["fact"])
        
    print(f"Encontrados {len(kb_files)} ficheiros KB. A processar os 3 mais recentes como demonstração...")
    
    # Processar os últimos 3 ficheiros para gerar um histórico no CSV
    for kb_file in kb_files[-3:]:
        fact_sentence = translate_kb_to_natural_language(kb_file)
        
        with open('resultados_kitti.csv', 'a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow([fact_sentence])
            
        print(f"Ficheiro: {os.path.basename(kb_file)}")
        print(f"Facto traduzido: {fact_sentence}\n")
        
    print("Concluído! O 'resultados_kitti.csv' contém agora traduções de First-Order Logic reais.")

if __name__ == "__main__":
    main()
