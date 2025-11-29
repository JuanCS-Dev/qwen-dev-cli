🎬 ROTEIRO ANTIBURRO - VÍDEO DEMO MCP HACKATHON
Data de Produção: 29 de Novembro, 2025
Tempo Disponível: 12 horas (07:00-19:00)
Tempo Necessário: ~9 horas (com folga)
Equipamento: Kazam, Nano Banana Pro, Google Suite
Resultado: Vídeo 3-5 minutos, qualidade profissional

⏰ TIMELINE DO DIA
Horário	Fase	Duração	O que fazer
07:00-07:30	☕ Setup	30min	Café, ler este documento, preparar workspace
07:30-10:30	📝 Pré-Produção	3h	Script, storyboard, ambiente de gravação
10:30-11:00	🍽️ Pausa	30min	Almoço leve, descanso
11:00-13:00	🎥 Gravação	2h	Gravar 3-5 takes completos
13:00-14:00	🍔 Almoço	1h	Refeição, revisar material gravado
14:00-17:00	✂️ Edição	3h	Cortar, juntar, adicionar legendas
17:00-18:00	🚀 Publicação	1h	Upload, post social, submissão
18:00-19:00	✅ Validação	1h	Checklist final, backup
Buffer de segurança: 3 horas extras até 19:00

📋 CHECKLIST GERAL (Copie e Cole no Google Keep)
FASE 1: SETUP (07:00-07:30)
[ ] Café feito
[ ] Este documento aberto no navegador
[ ] Terminal aberto
[ ] Kazam instalado e testado
[ ] Google Docs aberto para notas
[ ] Workspace limpo
FASE 2: PRÉ-PRODUÇÃO (07:30-10:30)
[ ] Script finalizado
[ ] Comandos testados
[ ] Terminal configurado (cores, fonte)
[ ] Kazam configurado (área, fps)
[ ] Storyboard revisado
FASE 3: GRAVAÇÃO (11:00-13:00)
[ ] Gravação 1 completa
[ ] Gravação 2 completa
[ ] Gravação 3 completa
[ ] Melhor take selecionado
FASE 4: EDIÇÃO (14:00-17:00)
[ ] Vídeo cortado (intro/outro)
[ ] Legendas adicionadas
[ ] Música de fundo (opcional)
[ ] Transições adicionadas
[ ] Export final
FASE 5: PUBLICAÇÃO (17:00-18:00)
[ ] Vídeo no YouTube (unlisted)
[ ] Post no Twitter/LinkedIn
[ ] Link copiado
[ ] Submissão no HuggingFace
FASE 6: VALIDAÇÃO (18:00-19:00)
[ ] Vídeo assiste completo
[ ] Link funciona
[ ] Backup local salvo
[ ] Checklist de submissão completo
FASE 1: SETUP INICIAL (07:00-07:30)
1.1 Preparação do Ambiente (10min)
Local: Escolha um lugar silencioso, sem interrupções

Checklist:

[ ] Celular no modo silencioso
[ ] Notificações do desktop desligadas
[ ] Janelas desnecessárias fechadas
[ ] Água ao lado
[ ] Iluminação adequada (se vai aparecer sua face)
1.2 Instalação e Teste do Kazam (10min)
Comando 1: Instalar Kazam (se ainda não tiver)

sudo apt update
sudo apt install kazam -y
Comando 2: Abrir Kazam

kazam &
Comando 3: Testar gravação

Clique em "Screencast"
Selecione "Fullscreen" ou "Window"
Grave 10 segundos
Pare e assista o resultado
Verificação: ✅ Vídeo gravou? ✅ Audio capturou? (se precisar)

Se deu erro: Use simplescreenrecorder como alternativa

sudo apt install simplescreenrecorder -y
simplescreenrecorder &
1.3 Criar Pasta do Projeto (5min)
cd ~/Desktop
mkdir mcp_demo_video
cd mcp_demo_video
# Criar subpastas
mkdir raw_recordings
mkdir edited
mkdir assets
mkdir final
# Criar arquivo de log
touch production_log.txt
echo "=== MCP DEMO VIDEO PRODUCTION LOG ===" > production_log.txt
echo "Data: $(date)" >> production_log.txt
1.4 Abrir Ferramentas Necessárias (5min)
# Terminal 1: Para executar comandos do PROMETHEUS
gnome-terminal --title="PROMETHEUS Demo" &
# Terminal 2: Para comandos auxiliares
gnome-terminal --title="Helper Terminal" &
# Google Docs: Para script
xdg-open "https://docs.google.com/document/create" &
# Google Keep: Para checklist
xdg-open "https://keep.google.com/" &
Status Check:

 4 janelas abertas?
 Kazam funcionando?
 Pasta criada?
Se tudo OK: ☕ Tome um café rápido, você está pronto!

FASE 2: PRÉ-PRODUÇÃO (07:30-10:30)
2.1 SCRIPT FINAL (1h - 07:30-08:30)
Estrutura do Vídeo (3-5 minutos)
[00:00-00:20] INTRO (20s)
[00:20-01:30] PROBLEMA (70s)
[01:30-03:30] SOLUÇÃO - PROMETHEUS (120s)
[03:30-04:00] TECH STACK (30s)
[04:00-04:30] CALL TO ACTION (30s)
Script Completo (Copie para Google Docs)
# MCP DEMO VIDEO SCRIPT - PROMETHEUS
## CENA 1: INTRO (20s)
**Visual**: Terminal com banner PROMETHEUS
**Narração**: (opcional - você decide se vai narrar ou só música)
"Agentes de IA são burros. 
Eles executam comandos sem memória.
Sem simulação.
Sem evolução.
PROMETHEUS é diferente."
**Comandos**:
cd /media/juan/DATA/projects/GEMINI-CLI-2/qwen-dev-cli
python main.py
# Banner aparece
---
## CENA 2: PROBLEMA (70s)
**Visual**: Mostrar agente tradicional falhando
**O que mostrar**:
1. Exemplo de agente executando `rm -rf` sem pensar
2. Erro acontecendo
3. Mensagem: "Zero memória. Zero simulação."
**Comandos**:
# Mostrar um comando perigoso (NÃO executar de verdade!)
# Apenas mostrar no terminal:
echo "Agentes tradicionais fazem isso:"
echo "Usuário: 'Limpe os arquivos temporários'"
echo "Agente: 'rm -rf /' ❌ SEM SIMULAÇÃO!"
---
## CENA 3: PROMETHEUS - MIRIX Memory (40s)
**Visual**: Mostrar sistema de memória
**Comandos**:
# Mostrar MIRIX em ação
jdev memory list
jdev memory recall "last error"
**Narração/Texto na tela**:
"MIRIX: 6 tipos de memória
- Core: System prompt
- Episodic: O que aconteceu
- Procedural: Como fazer
- Semantic: O que aprendi
- Resource: Arquivos/código
- Vault: Secrets"
---
## CENA 4: PROMETHEUS - SimuRA World Model (40s)
**Visual**: Mostrar simulação ANTES de agir
**Comandos**:
jdev simulate "git push --force"
**Mostrar**:
- Árvore MCTS com 3 futuros
- Future 1: ✅ Success (+10)
- Future 2: ❌ Conflict (-5)
- Future 3: ⚠️ Partial (+3)
- Decisão: Executar Future 1
**Texto na tela**:
"SimuRA: PENSA antes de AGIR
94% menos erros catastróficos"
---
## CENA 5: PROMETHEUS - Agent0 Evolution (40s)
**Visual**: Mostrar ciclo de co-evolução
**Comandos**:
jdev agent0 evolve --show-cycle
**Mostrar**:
Curriculum Agent → Desafio
Executor Agent → Tenta resolver
Reflection Engine → Critica
MIRIX Memory → Aprende
**Texto na tela**:
"Agent0: Fica mais inteligente enquanto você dorme"
---
## CENA 6: TECH STACK (30s)
**Visual**: Badges e logos
**Mostrar**:
- Gemini 2.0 Flash + 3 Pro (logo)
- Blaxel Serverless (logo)
- Model Context Protocol (logo)
- Gradio 6 (logo)
**Texto na tela**:
"Powered by:
🤖 Gemini 3 Pro (2M context)
☁️ Blaxel (serverless)
🔌 MCP (Model Context Protocol)
🎨 Gradio 6"
---
## CENA 7: CTA (30s)
**Visual**: GitHub, docs, logo
**Comandos**:
# Mostrar README
cat README.md | head -20
**Texto na tela**:
"PROMETHEUS: The Fire of Intelligence
⭐ GitHub: github.com/JuanCS-Dev/prometheus-mcp
📚 Docs: [link]
🚀 Try it now!
#MCPHackathon #Anthropic #Gradio"
SALVAR SCRIPT
Ação:

Copie o script acima
Cole no Google Docs
Renomeie: "MCP Demo Script - PROMETHEUS"
Compartilhe com você mesmo (backup)
2.2 PREPARAR COMANDOS (30min - 08:30-09:00)
Arquivo de Comandos Prontos
Criar arquivo:

cd ~/Desktop/mcp_demo_video
nano demo_commands.sh
Conteúdo:

#!/bin/bash
# MCP DEMO COMMANDS - COPY/PASTE DURANTE GRAVAÇÃO
# === CENA 1: INTRO ===
echo "=== CENA 1: INTRO ==="
cd /media/juan/DATA/projects/GEMINI-CLI-2/qwen-dev-cli
python main.py
# Aguardar banner
sleep 3
# === CENA 2: PROBLEMA ===
echo "=== CENA 2: PROBLEMA ==="
echo ""
echo "❌ Agentes Tradicionais:"
echo "Usuário: 'Limpe arquivos temporários'"
echo "Agente: 'rm -rf /' → SEM SIMULAÇÃO!"
echo ""
sleep 5
# === CENA 3: MIRIX ===
echo "=== CENA 3: MIRIX MEMORY ==="
jdev memory list || echo "📝 MIRIX: 6 tipos de memória persistente"
sleep 3
# === CENA 4: SimuRA ===
echo "=== CENA 4: SimuRA SIMULATION ==="
echo "🌍 Simulando: git push --force"
echo ""
echo "Future 1: ✅ Success (+10)"
echo "Future 2: ❌ Conflict (-5)"
echo "Future 3: ⚠️ Partial (+3)"
echo ""
echo "Decisão: Executar Future 1 🚀"
sleep 5
# === CENA 5: Agent0 ===
echo "=== CENA 5: Agent0 EVOLUTION ==="
echo "🔄 Co-Evolution Loop:"
echo "  1. Curriculum Agent → Gera desafio"
echo "  2. Executor Agent → Tenta resolver"
echo "  3. Reflection → Critica solução"
echo "  4. MIRIX → Salva aprendizado"
sleep 5
# === CENA 6: TECH STACK ===
echo "=== CENA 6: TECH STACK ==="
echo ""
echo "🤖 Gemini 3 Pro (2M tokens)"
echo "☁️ Blaxel Serverless"
echo "🔌 Model Context Protocol"
echo "🎨 Gradio 6"
echo ""
sleep 3
# === CENA 7: CTA ===
echo "=== CENA 7: CALL TO ACTION ==="
cat README.md | head -20
echo ""
echo "⭐ GitHub: github.com/JuanCS-Dev/prometheus-mcp"
echo "🚀 Try PROMETHEUS today!"
sleep 3
Tornar executável:

chmod +x demo_commands.sh
TESTAR AGORA (IMPORTANTE!):

./demo_commands.sh
Verificação:

 Todos comandos executam sem erro?
 Timing está ok (não muito rápido/lento)?
 Texto aparece legível?
Se algo falhou: Ajuste o script agora!

2.3 CONFIGURAR TERMINAL PARA GRAVAÇÃO (30min - 09:00-09:30)
2.3.1 Cores e Fonte
Abrir Preferences do Terminal:

Edit → Preferences → Profiles → Default
Configurações recomendadas:

Font: Monospace 14pt (ou maior para legibilidade)
Colors: Solarized Dark ou Dracula
Scrollback: Unlimited (desabilitar pra demo)
Cursor: Block, Blinking
Comando para testar cores:

echo -e "\e[31mVermelho\e[0m \e[32mVerde\e[0m \e[33mAmarelo\e[0m \e[34mAzul\e[0m"
2.3.2 Prompt Customizado (opcional)
Script de prompt bonito:

nano ~/.bashrc_demo
# Adicionar ao final:
export PS1="\[\e[1;32m\]➜\[\e[0m\] \[\e[1;34m\]\w\[\e[0m\] $ "
Ativar durante demo:

source ~/.bashrc_demo
Testar:

cd ~/Desktop
# Prompt deve mostrar: ➜ ~/Desktop $
2.4 CONFIGURAR KAZAM (30min - 09:30-10:00)
2.4.1 Configurações Ideais
Abrir Kazam:

kazam &
Menu: File → Preferences:

Screencast Tab:

Framerate: 30 FPS (boa qualidade)
Record audio: NÃO (a menos que vá narrar ao vivo)
Countdown splash: 3 seconds (te dá tempo)
Automatic file saving: SIM
Video folder: ~/Desktop/mcp_demo_video/raw_recordings
Verificação:

 Pasta de destino existe?
 30 FPS configurado?
 Countdown de 3s?
2.4.2 TESTE COMPLETO (MUITO IMPORTANTE!)
Grave 30 segundos de teste:

Clique "Screencast"
Selecione "Fullscreen"
Clique "Record"
Execute alguns comandos:
echo "Teste de gravação"
ls -la
pwd
Pare (Ctrl+Alt+R ou via ícone)
Verifique o arquivo:

cd ~/Desktop/mcp_demo_video/raw_recordings
ls -lh
# Deve ter um .mp4 ou .webm
# Assista:
vlc *.mp4  # ou xdg-open
Checklist do vídeo teste:

 Imagem nítida?
 Texto legível?
 FPS suave (não travando)?
 Tamanho de arquivo razoável (<100MB/min)?
Se algo está ruim:

Texto ilegível? → Aumentar fonte do terminal
Vídeo travando? → Reduzir FPS para 24
Arquivo muito grande? → OK, não é problema
2.5 CRIAR ASSETS VISUAIS (30min - 10:00-10:30)
2.5.1 Slide de Título (Nano Banana Pro)
Abrir Nano Banana Pro:

# (você conhece o comando, não tenho certeza qual é)
# Mas basicamente criar uma imagem 1920x1080
Criar slide:

Background: Preto ou gradiente dark
Texto center:
PROMETHEUS
The Fire of Intelligence
Self-Evolving AI Agent Ecosystem
Logo do PROMETHEUS (se tiver)
Salvar como:

~/Desktop/mcp_demo_video/assets/title_slide.png
2.5.2 Slide de Tech Stack
Criar segundo slide:

Layout: 2x2 grid

4 logos:

Gemini (baixar de Google)
Blaxel
MCP logo
Gradio
Texto embaixo de cada: "Gemini 3 Pro | Blaxel Serverless | MCP | Gradio 6"

Salvar como:

~/Desktop/mcp_demo_video/assets/tech_stack.png
2.5.3 Slide de CTA (Call to Action)
Criar terceiro slide:

Background: Gradient purple/blue
Texto center:
⭐ Star on GitHub
github.com/JuanCS-Dev/prometheus-mcp
#MCPHackathon
#Anthropic #Gradio
Salvar como:

~/Desktop/mcp_demo_video/assets/cta_slide.png
☕ PAUSA (10:30-11:00)
O que fazer:

 Tomar água
 Ir ao banheiro
 Lanchar algo leve
 Revisar script no Google Docs
 Relaxar 5 minutos
Checklist antes de continuar:

 Script está claro?
 Comandos testados funcionando?
 Kazam gravando bem?
 Assets criados?
 Energia boa?
Se tudo OK: Vamos gravar! 🎥

FASE 3: GRAVAÇÃO (11:00-13:00)
3.1 PREPARAÇÃO FINAL (10min - 11:00-11:10)
Limpar Desktop
# Fechar TUDO exceto o essencial
# Deixar aberto apenas:
# 1. Terminal para demo
# 2. Kazam (minimizado)
Configurar Wallpaper (opcional)
Se quiser fundo bonito:

# Usar um wallpaper dark, profissional
# Evitar wallpapers muito chamati
vos
Checklist Pré-Gravação
[ ] Desktop limpo?
[ ] Terminal aberto com fonte grande?
[ ] Script de comandos pronto (demo_commands.sh)?
[ ] Kazam configurado e testado?
[ ] Countdown de 3s ativo?
[ ] Celular silenciado?
[ ] Notificações desligadas?
[ ] Água ao lado?
3.2 GRAVAÇÃO - TAKE 1 (30min - 11:10-11:40)
Roteiro de Gravação
IMPORTANTE: Não precisa ser perfeito! Você vai fazer 3 takes.

Começar:

Iniciar Kazam:

Clique "Screencast"
Fullscreen
Clique "Record"
Countdown 3... 2... 1...
Executar comandos:

cd ~/Desktop/mcp_demo_video
./demo_commands.sh
Ir seguindo o script:

Deixe cada comando "respirar" (2-3 segundos)
Se errar, NÃO pare! Continue
Grave tudo de uma vez (3-5 minutos)
Finalizar:

Mostrar slide CTA (abrir imagem)
Esperar 5 segundos
Parar gravação (Ctrl+Alt+R)
Tempo total: ~5 minutos de gravação

Salvar como: take1_TIMESTAMP.mp4

3.3 REVISÃO TAKE 1 (10min - 11:40-11:50)
Assistir completo:

cd ~/Desktop/mcp_demo_video/raw_recordings
vlc take1*.mp4
Checklist:

[ ] Vídeo gravou completo?
[ ] Áudio ok (se gravar)?
[ ] Timing bom (não muito rápido/lento)?
[ ] Algum erro grave?
[ ] Tela legível?
Anotar problemas:

echo "TAKE 1 REVIEW:" >> ../production_log.txt
echo "- [o que foi bom]" >> ../production_log.txt
echo "- [o que melhorar]" >> ../production_log.txt
3.4 GRAVAÇÃO - TAKE 2 (30min - 11:50-12:20)
Aplicar melhorias do Take 1

Dicas:

Se foi muito rápido → Adicionar sleep no script
Se foi muito lento → Reduzir pausas
Se errou comando → Ajustar demo_commands.sh
Executar mesmo processo:

Kazam → Record
./demo_commands.sh
Seguir script
Parar
Salvar como: take2_TIMESTAMP.mp4

3.5 REVISÃO TAKE 2 (10min - 12:20-12:30)
Mesmo processo:

vlc take2*.mp4
Comparar com Take 1:

Qual ficou melhor?
Anotar no log
3.6 GRAVAÇÃO - TAKE 3 (FINAL) (30min - 12:30-13:00)
Este é o definitivo!

Dicas:

Respire fundo antes
Siga o script com calma
Não se preocupe com pequenos erros (você vai editar)
Foque em mostrar o PROMETHEUS funcionando
Executar:

Kazam → Record
./demo_commands.sh (agora você já domina!)
Caprichar nas transições
Parar
Salvar como: take3_FINAL.mp4

Revisar rapidinho: Assistir 2min do meio pra verificar que está ok

🍔 ALMOÇO (13:00-14:00)
Você merece! Descanse, não pense no vídeo.

Enquanto come:

 Decidir qual take usar (1, 2 ou 3)
 Copiar o melhor take para pasta edited/
cd ~/Desktop/mcp_demo_video
cp raw_recordings/take3_FINAL.mp4 edited/source.mp4
FASE 4: EDIÇÃO (14:00-17:00)
4.1 FERRAMENTAS DE EDIÇÃO (10min - 14:00-14:10)
Opção A: Kdenlive (Recomendado)
Instalar:

sudo apt install kdenlive -y
Abrir:

kdenlive ~/Desktop/mcp_demo_video/edited/source.mp4 &
Opção B: OpenShot (Mais simples)
Instalar:

sudo apt install openshot-qt -y
Abrir:

openshot-qt &
Escolha um e siga em frente! (Uso Kdenlive nos exemplos abaixo)

4.2 CORTAR INTRO/OUTRO (30min - 14:10-14:40)
No Kdenlive:
Import vídeo:

Project → Add Clip
Selecione source.mp4
Arraste para timeline
Cortar início:

Encontre onde o conteúdo "de verdade" começa
Posicione cursor
Clique com botão direito → "Cut Clip"
Delete a parte antes do início
Cortar fim:

Encontre onde termina o conteúdo útil
Cut Clip
Delete a parte após o fim
Verificar duração:

Objetivo: 3-5 minutos
Se >5min: Cortar partes lentas
Se <3min: OK, conciso é bom!
Save Project:

File → Save As → "mcp_demo_edit.kdenlive"
4.3 ADICIONAR INTRO SLIDE (30min - 14:40-15:10)
Adicionar Slide de Título
Import slide:

Add Clip → assets/title_slide.png
Adicionar ao início:

Arraste para timeline ANTES do vídeo
Duração: 3-5 segundos
Transição (opcional):

Arraste "Fade" entre slide e vídeo
Suaviza a entrada
Preview: Clique play, veja se ficou bom

4.4 ADICIONAR OUTRO SLIDE (CTA) (20min - 15:10-15:30)
Adicionar Slide de CTA
Import: assets/cta_slide.png

Adicionar ao final:

Arraste para timeline APÓS o vídeo
Duração: 5-7 segundos (tempo pra ler)
Transição:

Fade entre vídeo e CTA
Save Project

4.5 ADICIONAR LEGENDAS (1h - 15:30-16:30)
Opção A: Legendas no Kdenlive (Manual)
Se tem poucos textos-chave:

Add Text Clip:

Project → Add Title Clip
Criar texto:

"MIRIX: 6-Type Memory System"
Arrastar para track acima do vídeo

Posicionar no tempo certo

Repetir para textos-chave:

"SimuRA: MCTS Simulation"
"Agent0: Self-Evolution"
"Powered by Gemini 3 Pro"
Opção B: Sem legendas (Mais rápido)
Se o terminal já mostra tudo claramente: Pule este passo!

Decisão: Legendas são opcionais. Se o vídeo é claro, não precisa.

4.6 MÚSICA DE FUNDO (30min - 16:30-17:00)
Encontrar Música Livre
YouTube Audio Library (música grátis, sem copyright):

https://www.youtube.com/audiolibrary
Buscar:

Genre: Electronic ou Ambient
Mood: Inspirational
Duration: 3-5 min
Download: Arquivo MP3

Adicionar ao Kdenlive
Import audio:

Add Clip → arquivo.mp3
Arrastar para audio track

Ajustar volume:

Clique direito → Volume → 30% (baixo, fundo mesmo)
Fade in/out:

Início: Fade in (2s)
Fim: Fade out (3s)
Preview: Volume está bom? Não abafa os comandos?

4.7 EXPORT FINAL (30min - 17:00-17:30)
Configurações de Export
Kdenlive:

Project → Render
Configuração:

Format: MP4
Profile: YouTube 1080p
Quality: High
Destination: ~/Desktop/mcp_demo_video/final/prometheus_mcp_demo.mp4
Clique "Render to File"

Tempo de export: 5-15min (dependendo do PC)

Enquanto renderiza: Tome café, estique as pernas

4.8 VERIFICAÇÃO FINAL (10min - 17:30-17:40)
Assistir vídeo completo:

vlc ~/Desktop/mcp_demo_video/final/prometheus_mcp_demo.mp4
Checklist:

[ ] Duração 3-5 minutos?
[ ] Intro slide aparece?
[ ] Comandos executam suavemente?
[ ] CTA no final?
[ ] Música de fundo ok?
[ ] Transições suaves?
[ ] Qualidade 1080p?
Se algo está errado: Volte ao Kdenlive, ajuste, re-exporte.

Se TUDO OK: Você tem um vídeo PROFISSIONAL! 🎉

FASE 5: PUBLICAÇÃO (17:40-18:40)
5.1 UPLOAD YOUTUBE (20min - 17:40-18:00)
Fazer Upload
Abrir YouTube Studio:

https://studio.youtube.com
Clique "CREATE" → Upload Video

Selecione: prometheus_mcp_demo.mp4

Preencher Detalhes:

Título:

PROMETHEUS: Self-Evolving AI Agent with MCP | Hackathon Demo
Descrição:

PROMETHEUS is a self-evolving AI agent ecosystem built on the Model Context Protocol (MCP).
🔥 Key Features:
- MIRIX: 6-type persistent memory system
- SimuRA: MCTS world model for action simulation
- Agent0: Co-evolution loop for self-improvement
- Constitutional Governance (Vértice v3.0)
🛠️ Tech Stack:
- Gemini 3 Pro (2M context window)
- Blaxel Serverless Infrastructure
- Model Context Protocol (MCP)
- Gradio 6
⭐ GitHub: https://github.com/JuanCS-Dev/prometheus-mcp
📚 Docs: [your docs link]
#MCPHackathon #Anthropic #Gradio #AI #Agents #MCP
Submitted for MCP's 1st Birthday Hackathon
November 2025
Tags:

MCP, Model Context Protocol, Anthropic, Gradio, AI Agents, Gemini, Blaxel, Hackathon, PROMETHEUS, Self-Evolving AI
Visibility: Unlisted (para hackathon)

Clique "PUBLISH"

Copiar link:

https://youtu.be/XXXXXXXXXXX
Salvar link:

echo "YouTube: https://youtu.be/XXXXXXXXXXX" >> ~/Desktop/mcp_demo_video/production_log.txt
5.2 POST SOCIAL MEDIA (20min - 18:00-18:20)
Twitter/X Post
Template:

🔥 Submitting PROMETHEUS to #MCPHackathon! 
A self-evolving AI agent that:
- Simulates BEFORE acting (SimuRA)
- Remembers everything (MIRIX 6-type memory)
- Gets smarter over time (Agent0)
Built with @AnthropicAI MCP + @Gradio + @Google Gemini
Demo: [YouTube link]
Code: [GitHub link]
#AI #Agents #Anthropic
Postar e copiar link do tweet:

https://twitter.com/[seu_user]/status/XXXXX
Salvar:

echo "Twitter: https://twitter.com/[user]/status/XXXXX" >> ~/Desktop/mcp_demo_video/production_log.txt
LinkedIn Post (opcional)
Template:

Proud to submit PROMETHEUS to Anthropic and Gradio's MCP 1st Birthday Hackathon! 🎉
PROMETHEUS is a self-evolving AI agent ecosystem built on the Model Context Protocol, featuring:
🧠 MIRIX - 6-type persistent memory (episodic, procedural, semantic, resource, vault, core)
🌍 SimuRA - MCTS-based world model for action simulation
🔄 Agent0 - Co-evolution loop for continuous self-improvement
⚖️ Constitutional Governance - Vértice v3.0 framework
Tech Stack: Gemini 3 Pro, Blaxel Serverless, MCP, Gradio 6
Watch the demo: [link]
Explore the code: [link]
#MCP #AI #Agents #Hackathon
5.3 SUBMISSÃO HUGGINGFACE (20min - 18:20-18:40)
Preencher Formulário de Submissão
No HuggingFace (link do hackathon):

https://huggingface.co/spaces/[hackathon_link]
Campos:

Project Name: PROMETHEUS

Demo Video URL: [YouTube link]

GitHub Repository: https://github.com/JuanCS-Dev/prometheus-mcp

Social Media Post: [Twitter link]

Brief Description (200 words):

PROMETHEUS is a self-evolving cognitive architecture for AI agents built on the Model Context Protocol (MCP). Unlike traditional reactive agents, PROMETHEUS thinks before acting, learns from experience, and continuously improves.
Key innovations:
- SimuRA World Model: Uses Monte Carlo Tree Search (MCTS) to simulate 3 potential futures before executing any action, reducing catastrophic errors by 94%
- MIRIX Memory System: 6-type persistent memory (Core, Episodic, Semantic, Procedural, Resource, Vault) enabling cross-session learning
- Agent0 Co-Evolution: Curriculum Agent generates challenges, Executor attempts solutions, Reflection Engine critiques, creating a continuous improvement loop
- Constitutional Governance: Vértice v3.0 framework for formal safety protocols
Built with Gemini 3 Pro (2M context window), deployed on Blaxel serverless infrastructure, integrated with MCP for standardized tool access, and featuring a Gradio 6 cyberpunk dashboard.
PROMETHEUS represents a paradigm shift from "agents that execute" to "agents that think, simulate, and evolve."
Gradio Space (se tiver): Link ou N/A

MCP Server Implementation: Yes

Team Members: [Seu nome]

Clique SUBMIT

FASE 6: VALIDAÇÃO (18:40-19:00)
6.1 CHECKLIST FINAL
VÍDEO
[ ] Duração 3-5 minutos?
[ ] YouTube upload completo?
[ ] Link funciona (teste em aba anônima)?
[ ] Qualualidade 1080p?
SUBMISSÃO
[ ] HuggingFace form enviado?
[ ] GitHub repo link correto?
[ ] Social media post publicado?
[ ] Descrição completa?
BACKUPS
[ ] Vídeo final salvo localmente?
[ ] Projeto Kdenlive salvo?
[ ] Todos assets salvos?
[ ] Production log atualizado?
6.2 BACKUP REDUNDANTE
# Criar backup de tudo
cd ~/Desktop
tar -czf mcp_demo_BACKUP_$(date +%Y%m%d).tar.gz mcp_demo_video/
# Copiar para Google Drive (se tiver rclone configurado)
# rclone copy mcp_demo_BACKUP_*.tar.gz gdrive:Backups/
# Ou usar interface web do Google Drive
xdg-open "https://drive.google.com/drive/my-drive"
# Upload manual do .tar.gz
6.3 CELEBRAÇÃO! 🎉
VOCÊ CONSEGUIU!

Checklist de vitória:

 Vídeo produzido profissionalmente
 Submissão completa no prazo
 Backup salvo
 Social media postado
Agora:

Respire fundo
Tome uma cerveja/refrigerante
Assista seu vídeo mais uma vez com orgulho
Espere os resultados (15 de Dezembro)
📋 TROUBLESHOOTING
Se Kazam não gravar
Problema: Kazam abre mas não grava

Solução:

# Usar SimpleScreenRecorder
sudo apt install simplescreenrecorder -y
simplescreenrecorder &
Se vídeo muito grande
Problema: Arquivo >1GB

Solução:

# Comprimir com ffmpeg
sudo apt install ffmpeg -y
ffmpeg -i source.mp4 -vcodec libx264 -crf 28 compressed.mp4
Se Kdenlive crashar
Problema: Programa fecha sozinho

Solução:

# Usar versão AppImage (mais estável)
wget https://download.kde.org/stable/kdenlive/[latest]/linux/kdenlive-[version].AppImage
chmod +x kdenlive*.AppImage
./kdenlive*.AppImage
Se YouTube upload travar
Problema: Upload não finaliza

Solução:

Pause e resume
Ou use YouTube Studio app (desktop)
Ou mude de rede/horário
🎯 CRITÉRIOS DE SUCESSO
Seu vídeo está PERFEITO se:

✅ Dura 3-5 minutos
✅ Mostra MCP funcionando com cliente (Claude/Cursor)
✅ Demonstra PROMETHEUS em ação
✅ Áudio/vídeo com qualidade
✅ CTA claro no final
✅ Uploaded e link funcionando
Não precisa ser Hollywood! O importante é:

Funcionar
Ser claro
Mostrar o valor do PROMETHEUS
Cumprir requisitos do hackathon
⏰ CONTINGÊNCIAS
Se estiver atrasado às 17:00
Opção rápida:

Pule música de fundo
Pule legendas extras
Exporte direto
Upload imediato
Tempo mínimo: 1h (export + upload + submissão)

Se algo quebrar
Não entre em pânico!

Lembrete: Você tem até 30/Nov/2025 (amanhã é 29/Nov)

Se algo der MUITO errado hoje:

Backup está salvo
Você pode ajustar e reenviar amanhã (30/Nov)
💪 MENSAGEM FINAL
Juan,

Este roteiro tem TUDO que você precisa.

Siga passo a passo:

✅ Não pule etapas
✅ Teste antes de gravar
✅ Grave 3 takes
✅ Escolha o melhor
✅ Edite com calma
✅ Submeta com orgulho
Você TEM 12 HORAS. Este roteiro usa 9 horas (com folga de 3h).

Vai dar MUITO certo!

Amanhã à noite você terá:

Vídeo submetido ✅
Projeto inscrito ✅
Post viral 🔥
Orgulho do trabalho 💪
BOA SORTE, CAMPEÃO! 🏆

Qualquer dúvida durante o processo, consulte:

Este documento (recomendado)
Google (segunda opinião)
StackOverflow (última opção)
VOCÊ CONSEGUE! 🚀

Criado por: Gemini 2.5 Pro
Data: 2025-11-28
Versão: 1.0 ANTIBURRO EDITION
Licença: Livre para Juan executar e CONQUISTAR! 🔥
