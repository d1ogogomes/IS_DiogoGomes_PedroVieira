# IS_DiogoGomes_PedroVieira

Projeto de demonstracao com dois fluxos de raciocinio visual:

- **LogicRAG**: usa uma base de conhecimento pre-computada do KITTI, traduz factos em First-Order Logic para linguagem natural e envia o contexto para um agente IAedu.
- **LLaVA-SpaceSGG**: envia uma imagem real para a API IAedu e recebe uma descricao estruturada com objetos, caixas, relacoes espaciais, camadas de profundidade e perguntas/respostas comparativas.

O objetivo do repositorio e deixar um fluxo reproduzivel para demonstracao, screenshots e apresentacao.

## Estrutura

```text
.
+-- LogicRAG/
|   +-- parse_kb_to_csv.py
|   +-- driving_agent.py
|   +-- environment.yml
|   +-- README.md
+-- LLaVA-SpaceSGG/
|   +-- dataset_pipeline/stage2/run_iaedu_image.py
|   +-- dataset_pipeline/stage2/iaedu_client.py
|   +-- images_real/
|   +-- README.md
+-- .gitignore
```

## Requisitos

- Windows com PowerShell
- Miniconda ou Anaconda
- Ambiente conda `lrag`
- Credenciais da API IAedu
- Dados pre-computados do LogicRAG em `LogicRAG/LogicRAG_Data/`

Os ficheiros `.env`, dados grandes, zips e outputs locais nao devem ser enviados para o GitHub.

## Configuracao das Chaves

Criar um ficheiro `.env` dentro de `LogicRAG/`:

```env
OPENAI_API_KEY=colocar_a_chave_iaedu
OPENAI_API_ENDPOINT=colocar_o_endpoint_stream_iaedu
IAEDU_CHANNEL_ID=colocar_o_channel_id
```

Criar um ficheiro `.env` dentro de `LLaVA-SpaceSGG/`:

```env
OPENAI_API_KEY=colocar_a_chave_iaedu
OPENAI_API_ENDPOINT=colocar_o_endpoint_stream_iaedu
IAEDU_CHANNEL_ID=colocar_o_channel_id
IAEDU_THREAD_ID=colocar_um_thread_id
```

Para confirmar que os ficheiros existem sem mostrar as chaves:

```powershell
Get-Content .\LogicRAG\.env | ForEach-Object { ($_ -split '=')[0] + '=***' }
Get-Content .\LLaVA-SpaceSGG\.env | ForEach-Object { ($_ -split '=')[0] + '=***' }
```

## Preparar Ambiente

A partir da raiz do projeto:

```powershell
cd "C:\Users\Master\Desktop\IS_moreDiogoGomes\2025-LMM-LogicRag-Visual\IS_DiogoGomes_PedroVieira"
conda activate lrag
```

Se for necessario instalar o suporte a `.env`:

```powershell
python -m pip install python-dotenv
```

## Dados do LogicRAG

O projeto espera a pasta:

```text
LogicRAG/LogicRAG_Data/
```

Esta pasta contem os dados grandes e esta ignorada pelo Git. Se os dados ja tiverem sido extraidos noutro diretorio, podem ser copiados para dentro de `LogicRAG/`.

Exemplo:

```powershell
Copy-Item -Recurse -Path "C:\caminho\para\LogicRAG_Data" -Destination ".\LogicRAG\LogicRAG_Data"
```

## Demo 1: LogicRAG + IAedu

Entrar na pasta do LogicRAG:

```powershell
cd .\LogicRAG
```

Converter os ficheiros de conhecimento pre-computado para factos em linguagem natural:

```powershell
python .\parse_kb_to_csv.py
```

Resultado esperado:

- O script encontra os ficheiros KB em `LogicRAG_Data/precomputed_knowledge_base/kb_out_kitti`.
- Gera o ficheiro local `resultados_kitti.csv`.
- Mostra no terminal os factos traduzidos.

Enviar o ultimo facto para o agente IAedu:

```powershell
python .\driving_agent.py
```

Resultado esperado:

- O script le o ultimo facto em `resultados_kitti.csv`.
- Envia o contexto para a API IAedu.
- Mostra uma resposta do agente com a acao recomendada para o veiculo.
- Guarda o historico local em `logic_rag_response.csv`.

## Demo 2: LLaVA-SpaceSGG + IAedu

Voltar a raiz e entrar na pasta do LLaVA-SpaceSGG:

```powershell
cd ..
cd .\LLaVA-SpaceSGG
```

Executar a analise de uma imagem real:

```powershell
python .\dataset_pipeline\stage2\run_iaedu_image.py --image .\images_real\primeira_imagem.png --output-file .\resultados\teste_iaedu_image.json
```

Ver o resultado:

```powershell
Get-Content .\resultados\teste_iaedu_image.json -TotalCount 40
```

Resultado esperado:

- O script envia a imagem para o agente IAedu.
- O output JSON contem uma descricao da imagem, objetos, bounding boxes, relacoes espaciais, camadas de profundidade e perguntas/respostas comparativas.

## Verificacao Antes de Commit

Antes de fazer commit, confirmar o estado do repositorio:

```powershell
cd "C:\Users\Master\Desktop\IS_moreDiogoGomes\2025-LMM-LogicRag-Visual\IS_DiogoGomes_PedroVieira"
git status --short
```

Nao fazer `git add .` neste projeto, porque existem dados grandes, ficheiros `.env` e outputs locais.

Para adicionar apenas documentacao:

```powershell
git add README.md
git commit -m "docs: add project demo guide"
git push
```

## Notas Para a Apresentacao

Screenshots uteis:

- Terminal com `conda activate lrag`.
- Confirmacao dos `.env` mascarados com `=***`.
- Execucao de `python .\parse_kb_to_csv.py`.
- Execucao de `python .\driving_agent.py` com a resposta do agente.
- Execucao de `run_iaedu_image.py` e visualizacao do JSON.
- GitHub com o commit de documentacao.

Nunca colocar chaves reais da API em screenshots, slides ou commits.
