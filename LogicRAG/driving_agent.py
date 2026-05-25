import os
import json
import csv
import requests
from datetime import datetime
from dotenv import load_dotenv


def obter_ultimo_facto_csv(caminho_ficheiro):
    """
    Abre o ficheiro CSV do LogicRAG e extrai a última linha registada.
    """
    try:
        with open(caminho_ficheiro, mode='r', encoding='utf-8') as ficheiro:
            leitor = csv.reader(ficheiro)
            linhas = list(leitor)

            if len(linhas) > 1:
                # pega na última linha do ficheiro (ignora o cabeçalho)
                ultima_linha = linhas[-1]
                return ", ".join(ultima_linha)
            else:
                return "Nenhum facto detetado no ficheiro."

    except FileNotFoundError:
        print(f"Aviso: O ficheiro '{caminho_ficheiro}' não foi encontrado.")
        print("A usar o facto de teste por defeito...\n")
        return "Pedestrian detected at crosswalk. Distance: 100 meters. Ego-vehicle speed: 30km/h."
    except Exception as e:
        return f"Erro ao ler CSV: {e}"


def guardar_resposta_csv(caminho_ficheiro, facto, resposta):
    """
    Guarda o facto de entrada e a resposta do LLM num CSV de histórico.
    Cria o ficheiro com cabeçalho se ainda não existir.
    """
    ficheiro_existe = os.path.isfile(caminho_ficheiro)

    with open(caminho_ficheiro, mode='a', newline='', encoding='utf-8') as ficheiro:
        escritor = csv.writer(ficheiro)

        # só escreve o cabeçalho na primeira vez
        if not ficheiro_existe:
            escritor.writerow(["timestamp", "facto_logicrag", "resposta_llm"])

        escritor.writerow([datetime.now().isoformat(), facto, resposta])


def main():
    print("Starting LogicRAG + API Integration System...\n")

    # pull credentials from .env so we don't hardcode anything sensitive
    load_dotenv()
    api_key = os.getenv("OPENAI_API_KEY")
    api_endpoint = os.getenv("OPENAI_API_ENDPOINT")
    channel_id = os.getenv("IAEDU_CHANNEL_ID")

    if not api_key or not api_endpoint or not channel_id:
        print("Error: Missing credentials in .env file.")
        return

    # read the latest detected scene fact from the LogicRAG output CSV
    logic_rag_result = obter_ultimo_facto_csv("resultados_kitti.csv")
    print(f"Fact extracted by LogicRAG: \n'{logic_rag_result}'\n")

    # give the LLM its role context, then drop in the scene fact
    prompt = f"""You are an intelligent assistant for an autonomous driving car.
Our logic engine (LogicRAG) detected the following on the road:
{logic_rag_result}

Based on this fact, explain briefly and directly what the immediate action of the car should be."""

    print("Sending data to API...\n")

    # the iaedu.pt endpoint expects multipart/form-data, not JSON
    multipart_data = {
        "message": (None, prompt),
        "thread_id": (None, "logic_rag_test_01"),  # groups conversation context
        "channel_id": (None, channel_id),
        "user_info": (None, "{}")
    }

    try:
        response = requests.post(
            api_endpoint,
            headers={
                "x-api-key": api_key  # iaedu uses x-api-key, not Bearer
            },
            files=multipart_data,
            stream=True,  # response comes back as SSE chunks
            timeout=60,
        )

        response.raise_for_status()

        print("Assistant Response:")
        print("-" * 50)

        resposta_completa = []

        # read SSE stream line by line and print tokens as they arrive
        for line in response.iter_lines():
            if not line:
                continue
            decoded = line.decode("utf-8")
            if decoded.startswith("data: "):
                decoded = decoded[len("data: "):]

            try:
                chunk = json.loads(decoded)
                event_type = chunk.get("type")

                if event_type == "token":
                    token = chunk.get("content", "")
                    if token:
                        print(token, end="", flush=True)
                        resposta_completa.append(token)
                elif event_type == "done":
                    break  # server signals end of stream

            except json.JSONDecodeError:
                pass  # skip heartbeat lines or malformed chunks

        print("\n" + "-" * 50)

        # save input fact + LLM response to the history CSV
        resposta_texto = "".join(resposta_completa)
        guardar_resposta_csv("logic_rag_response.csv", logic_rag_result, resposta_texto)
        print("Resposta guardada em logic_rag_response.csv")

    except requests.exceptions.HTTPError as e:
        print(f"\nAPI Failure [{e.response.status_code}]: {e.response.text}")
    except Exception as e:
        print(f"\nError: {e}")


if __name__ == "__main__":
    main()
