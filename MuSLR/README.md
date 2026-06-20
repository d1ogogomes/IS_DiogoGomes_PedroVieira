# MuSLR / LogiCAM

Integracao do artigo **MuSLR: Multimodal Symbolic Logical Reasoning** (NeurIPS 2025) e da framework **LogiCAM** no projeto `IS_DiogoGomes_PedroVieira`.

- Artigo: https://arxiv.org/abs/2509.25851
- Pagina oficial: https://llm-symbol.github.io/MuSLR/
- Codigo oficial: https://github.com/Aiden0526/MuSLR
- Dataset do benchmark: https://huggingface.co/datasets/Aiden0526/MuSLR

## Objetivo da Integracao

O MuSLR avalia raciocinio simbolico multimodal: a partir de uma imagem e de um contexto com regras logicas formais, o modelo deve deduzir se uma afirmacao e True, False ou Unknown, usando logica proposicional (PL), de primeira ordem (FOL) ou nao-monotonica (NM). A framework LogiCAM e modular e assenta em tres modulos sobre um VLM: o Premise Selector, o Reasoning Type Identifier e o Reasoner.

A integracao seguiu o mesmo padrao dos restantes modulos do projeto (LogicRAG e LLaVA-SpaceSGG): foi desenvolvido um agente que envia uma instancia do benchmark (imagem + contexto + pergunta) ao motor de inferencia, suportando dois backends, a **API IAedu** (nuvem) e o **Ollama** (local), atraves da variavel `LLM_BACKEND`.

## Estrutura

```text
MuSLR/
+-- README.md
+-- muslr_agent.py          # agente de integracao (IAedu + Ollama)
+-- data/
|   +-- muslr_sample.jsonl  # 2 instancias de demonstracao (do artigo)
+-- resultados/             # outputs locais (ignorados pelo git)
+-- MuSLR-Code/             # codigo oficial (Aiden0526/MuSLR)
    +-- logicam.ipynb
    +-- evaluation.py
    +-- prompts/
    +-- data/
    +-- README.md
```

## Preparar Ambiente

```bash
pip install requests python-dotenv pillow
```

As credenciais da IAedu sao lidas do ficheiro `.env` na raiz do projeto (ignorado pelo git):

```text
OPENAI_API_KEY=...        # chave x-api-key da IAedu
OPENAI_API_ENDPOINT=https://api.iaedu.pt/agent-chat/api/v1/agent/.../stream
IAEDU_CHANNEL_ID=...
LLM_BACKEND=iaedu         # ou ollama
```

## Dataset

O dataset completo (1.093 instancias) nao deve ser enviado para o GitHub. Descarregar de:

```text
https://huggingface.co/datasets/Aiden0526/MuSLR
```

e colocar localmente (ignorado pelo `.gitignore`). Para uma demonstracao rapida, este modulo inclui `data/muslr_sample.jsonl` com duas instancias do artigo.

## Executar

### Inferencia na nuvem (IAedu)

```bash
# .env com LLM_BACKEND=iaedu
python muslr_agent.py --dataset data/muslr_sample.jsonl --id demo_001
```

### Inferencia local (Ollama, modelo de visao)

```bash
ollama serve
ollama pull llava

LLM_BACKEND=ollama python muslr_agent.py --dataset data/muslr_sample.jsonl --id demo_001
```

Sem `--dataset`, o agente usa a instancia de demonstracao embutida (o exemplo de mudanca de faixa do artigo). Se a imagem indicada nao existir, o agente envia apenas o contexto textual.

O agente constroi um prompt inspirado na LogiCAM (selecionar premissas, identificar o tipo de raciocinio, aplicar as regras logicas) e termina com uma linha `FINAL ANSWER: <True/False/Unknown>`. O resultado e guardado em `resultados/muslr_output.json`.

## Avaliacao (codigo oficial)

Para a avaliacao quantitativa formal sobre o dataset completo, usa-se o codigo oficial em `MuSLR-Code/` (notebook `logicam.ipynb` e `evaluation.py`), conforme o README original. Esse fluxo exige uma chave OpenAI/Anthropic e o dataset completo, pelo que neste trabalho foi usado sobretudo para analise e para a demonstracao controlada acima.

## Nota

Este modulo integra-se com os restantes (LogicRAG, LLaVA-SpaceSGG, VisuLogic) atraves do mesmo mecanismo de backend (`LLM_BACKEND`: `iaedu` ou `ollama`), preparando o objetivo final de integrar os quatro projetos.
