import os
import sys
import sqlite3
import datetime
import json
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters
)

# Garante raiz no PATH para imports do Python
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT_DIR not in sys.path:
    sys.path.append(ROOT_DIR)

from src.utils.env_loader import load_env
load_env()

from src.agents.agent_orchestrator import AgentOrchestrator
from src.agents.decompression_agent import DecompressionAgent
from src.obsidian.vault_sync import ObsidianSync
from src.database.upsert_engine import UpsertEngine

# CONFIGURAÇÕES
TOKEN = os.environ.get("TELEGRAM_TOKEN", "")
OPENAI_KEY = os.environ.get("OPENAI_API_KEY", "")
DB_PATH = os.path.join(ROOT_DIR, "data", "agent.db")
REPORTS_DIR = os.path.join(os.path.dirname(ROOT_DIR), "Arquivos", "Diario")

os.makedirs(REPORTS_DIR, exist_ok=True)

# Instancia os Módulos do Projeto Hórus
orchestrator = AgentOrchestrator(api_key=OPENAI_KEY)
decompression_agent = DecompressionAgent()
vault_sync = ObsidianSync(vault_path=REPORTS_DIR)
upsert_engine = UpsertEngine(db_path=DB_PATH)

# Estado global da conversa por usuário (persona padrão: sargento)
user_states = {}

def get_db_connection():
    return sqlite3.connect(DB_PATH)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando inicial do bot."""
    user_id = update.effective_user.id
    username = update.effective_user.first_name
    
    # Inicializa estado
    if user_id not in user_states:
        user_states[user_id] = {"persona": "sargento"}
        
    msg = (
        f"Atenção, Soldado {username}! ⚔️\n\n"
        "Aqui é o seu sistema **Hórus Copiloto de Vida** ativo!\n"
        "O ecossistema está unificado, rodando local-first com 3 Personas ativas no prompt.\n\n"
        "Comandos de Personas (A Trindade):\n"
        "🎖️ /sargento - Tom firme militar, cobrança dura contra a inércia.\n"
        "🧠 /amigo - Copiloto empático, analítico de sentimentos e acolhedor.\n"
        "📈 /estrategista - Planejamento a longo prazo e mini-projetos semanais.\n\n"
        "Comandos Operacionais:\n"
        "🔹 /checkin - Realizar o check-in de saúde e sono matinal\n"
        "🔹 /relatorio - Gerar e sincronizar o relatório diário com o Obsidian Vault\n"
        "🔹 /descomprimir - Iniciar descompressão ativa de final de dia\n\n"
        "Selecione uma persona ou envie uma mensagem para começar!"
    )
    await update.message.reply_text(msg)

async def set_sargento(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in user_states:
        user_states[user_id] = {}
    user_states[user_id]["persona"] = "sargento"
    await update.message.reply_text("🎖️ **Persona alterada para: SARGENTO.** Sem desculpas, soldado! O que você está procrastinando hoje?")

async def set_amigo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in user_states:
        user_states[user_id] = {}
    user_states[user_id]["persona"] = "amigo"
    await update.message.reply_text("🧠 **Persona alterada para: AMIGO.** Olá! Estou aqui para te ouvir. Como está se sentindo mentalmente hoje?")

async def set_estrategista(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in user_states:
        user_states[user_id] = {}
    user_states[user_id]["persona"] = "estrategista"
    await update.message.reply_text("📈 **Persona alterada para: ESTRATEGISTA.** Foco no futuro. Qual projeto ou OKR queremos destrinchar em sprints semanais agora?")

async def checkin_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Inicia o processo de check-in de saúde matinal."""
    user_id = update.effective_user.id
    user_states[user_id] = {
        "step": "checkin_sono",
        "data": {},
        "persona": user_states.get(user_id, {}).get("persona", "sargento")
    }
    await update.message.reply_text(
        "Soldado, começando o check-in matinal.\n"
        "Pergunta 1: Que horas você foi dormir ontem? (Ex: 23:30)"
    )

async def descomprimir_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Inicia o fluxo de descompressão ativa."""
    user_id = update.effective_user.id
    user_states[user_id] = {
        "step": "descompressao",
        "persona": user_states.get(user_id, {}).get("persona", "sargento")
    }
    await update.message.reply_text(
        "🧠 **MODO DESCOMPRESSÃO ATIVO.**\n"
        "Despeje em um único texto longo ou desabafo tudo o que aconteceu no seu dia, seus sentimentos, "
        "conquistas ou o que você procrastinou hoje. O Hórus irá analisar e extrair as tarefas automaticamente!"
    )

async def sincronizar_relatorio(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Gera o arquivo Markdown diário e roda o sync com o Obsidian."""
    data_hoje = datetime.date.today().strftime("%Y-%m-%d")
    await update.message.reply_text("Aguarde... Sincronizando dados com seu Obsidian Vault local...")
    try:
        path = vault_sync.sync_day(data_hoje)
        filename = os.path.basename(path)
        await update.message.reply_text(
            f"Sincronização concluída com sucesso! 🎖️\n\n"
            f"📂 **Nota Diária salva em:** `Arquivos/Diario/{filename}`\n"
            f"Todos os seus hábitos (Upserts) e tarefas da Curva ABC já estão atualizados no seu Obsidian."
        )
    except Exception as e:
        await update.message.reply_text(f"Erro na sincronização: {str(e)}")

async def memoria_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Inicia a busca por memórias no RAG local."""
    user_id = update.effective_user.id
    user_states[user_id] = {
        "step": "memoria_search",
        "persona": user_states.get(user_id, {}).get("persona", "sargento")
    }
    await update.message.reply_text(
        "🧠 **MODO MEMÓRIA SEMÂNTICA ATIVO.**\n"
        "O que você gostaria de buscar nos seus sentimentos ou fatos passados?\n"
        "Ex: 'Quando foi a última vez que me senti muito cansado?'"
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Manipulador central de todas as mensagens de texto."""
    user_id = update.effective_user.id
    text = update.message.text.strip()
    
    if user_id not in user_states:
        user_states[user_id] = {"persona": "sargento"}

    state = user_states[user_id]
    
    # 1. FLUXO CHECKIN DE SAÚDE
    if "step" in state and state["step"].startswith("checkin_"):
        step = state["step"]
        
        if step == "checkin_sono":
            state["data"]["hora_dormiu"] = text
            state["step"] = "checkin_acordou"
            await update.message.reply_text("Entendido. Que horas você acordou hoje? (Ex: 06:00)")
            
        elif step == "checkin_acordou":
            state["data"]["hora_acordou"] = text
            state["step"] = "checkin_nota"
            await update.message.reply_text("Qual foi a nota do seu sono de 1 a 5? (Onde 1 é péssimo e 5 é revigorante)")
            
        elif step == "checkin_nota":
            try:
                nota = int(text)
                if not (1 <= nota <= 5):
                    raise ValueError
                state["data"]["nota_sono"] = nota
                state["step"] = "checkin_peso"
                await update.message.reply_text("Anotado. Qual é o seu peso de hoje em kg? (Ex: 82.5)")
            except ValueError:
                await update.message.reply_text("Formato inválido! Envie um número inteiro de 1 a 5.")
                
        elif step == "checkin_peso":
            try:
                peso = float(text.replace(",", "."))
                state["data"]["peso"] = peso
                state["step"] = "checkin_relato"
                await update.message.reply_text("Como foi sua noite e como se sentiu ao acordar? Dê um breve relato.")
            except ValueError:
                await update.message.reply_text("Peso inválido! Envie um valor numérico decimal (Ex: 82.5).")
                
        elif step == "checkin_relato":
            state["data"]["relato"] = text
            data_hoje = datetime.date.today().strftime("%Y-%m-%d")
            d = state["data"]
            try:
                conn = get_db_connection()
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT OR REPLACE INTO checkin_saude 
                    (data, hora_dormiu, hora_acordou, nota_sono, peso, relato_sono, relato_acordar)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (data_hoje, d["hora_dormiu"], d["hora_acordou"], d["nota_sono"], d["peso"], d["relato"], "Checkin matinal"))
                conn.commit()
                conn.close()
                
                # Sincroniza peso também com a tabela de rotinas (Upsert Inteligente)
                upsert_engine.upsert_rotina(
                    rotina_id="acordar",
                    data_str=data_hoje,
                    acoes_concluidas=["acordar_02"], # Me pesar
                    dados_capturados={"peso_kg": d["peso"]}
                )
                
                await update.message.reply_text(
                    "Check-in matinal concluído e registrado com sucesso! 📁\n\n"
                    f"📅 Data: {data_hoje}\n"
                    f"💤 Sono: {d['hora_dormiu']} -> {d['hora_acordou']} (Nota: {d['nota_sono']}/5)\n"
                    f"⚖️ Peso: {d['peso']} kg\n\n"
                    "O QG local registrou tudo. Sem desculpas hoje, soldado!"
                )
            except Exception as e:
                await update.message.reply_text(f"Erro ao salvar no banco local: {str(e)}")
            finally:
                state.pop("step", None)
                state.pop("data", None)
        return

    # 2. FLUXO DESCOMPRESSÃO ATIVA
    if "step" in state and state["step"] == "descompressao":
        await update.message.reply_text("Processando descompressão ativa com a IA do Hórus...")
        try:
            data_hoje = datetime.date.today().strftime("%Y-%m-%d")
            analise = decompression_agent.processar_descompressao(text, data_hoje)
            
            # Sincroniza Obsidian automaticamente
            vault_sync.sync_day(data_hoje)
            
            # Resposta estruturada para o Telegram
            res_msg = (
                f"🧠 **ANÁLISE DE DESCOMPRESSÃO CONCLUÍDA!**\n\n"
                f"🟢 **O que foi excelente:** {analise.get('excelente')}\n"
                f"🔴 **O que dificultou:** {analise.get('dificultou')}\n"
                f"💡 **Lição:** {analise.get('licao')}\n\n"
                f"📋 **Sentimentos identificados:** {', '.join(analise.get('sentimentos', []))}\n"
                f"⚡ **Tarefas extraídas para a Curva ABC:** {len(analise.get('tarefas_extraidas', []))} tarefas adicionadas.\n\n"
                f"📂 Os dados foram sincronizados localmente no seu Obsidian!"
            )
            await update.message.reply_text(res_msg)
        except Exception as e:
            await update.message.reply_text(f"Erro no processamento da descompressão: {str(e)}")
        finally:
            state.pop("step", None)
        return

    # 3. FLUXO BUSCA MEMÓRIA (RAG LOCAL)
    if "step" in state and state["step"] == "memoria_search":
        await update.message.reply_text("Buscando no seu histórico local de diários...")
        try:
            from src.agents.memory_rag import MemoryRAG
            rag = MemoryRAG(key=OPENAI_KEY, reports_dir=REPORTS_DIR)
            resposta = rag.buscar_memoria(text)
            await update.message.reply_text(f"🧠 **MEMÓRIA RECUPERADA:**\n\n{resposta}")
        except Exception as e:
            await update.message.reply_text(f"Erro ao buscar memórias: {str(e)}")
        finally:
            state.pop("step", None)
        return

    # 3. INTERAÇÃO REGULAR DE CHAT (Utilizando a Persona Ativa)
    persona_ativa = state.get("persona", "sargento")
    await update.message.reply_text("Aguarde, processando resposta...")
    resposta = orchestrator.consultar_persona(persona_ativa, text)
    await update.message.reply_text(resposta)

async def nova_task(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Informa que o refinamento de tarefas agora é feito diretamente via Antigravity."""
    msg = (
        "🚀 **Esteira de Desenvolvimento Hórus — Antigravity** 🚀\n\n"
        "O sistema de autodesenvolvimento autônomo no bot foi descontinuado em prol de maior segurança e controle!\n\n"
        "Agora, a gestão de backlog, refinamento (PO) e planejamento de tarefas são feitos **diretamente no seu IDE pareando com o Antigravity** utilizando as Skills locais!\n\n"
        "👉 Abra seu IDE local e use a pasta `skills/` para começarmos a planejar sua próxima feature juntos com total segurança!"
    )
    await update.message.reply_text(msg)

async def aprovar_task(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Informa que a execução e QA agora são feitos diretamente via Antigravity."""
    msg = (
        "💻 **Pipeline de Engenharia — Antigravity** 💻\n\n"
        "A execução de código e QA automática no WSL foi migrada para o ambiente controlado do **Antigravity** no seu IDE local!\n\n"
        "Isso evita que códigos mal-estruturados quebrem seu bot em segundo plano.\n\n"
        "👉 Pareie com o Antigravity no IDE e ative as Skills de `Dev Sênior` e `QA` para codificar e testar de forma robusta e transparente!"
    )
    await update.message.reply_text(msg)

async def listar_kanban(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Lista o quadro Kanban de desenvolvimento."""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT id, titulo, status, branch_name FROM kanban_tasks ORDER BY id DESC LIMIT 10")
        rows = cursor.fetchall()
        conn.close()
        
        if not rows:
            await update.message.reply_text("Nenhuma tarefa no Kanban de desenvolvimento no momento.")
            return
            
        msg = "🛠️ **QUADRO KANBAN DE DESENVOLVIMENTO (Últimas 10)**\n\n"
        for row in rows:
            tid, title, status, branch = row
            status_emoji = {
                "backlog": "📁",
                "refining": "🧠",
                "developing": "💻",
                "testing": "🧪",
                "done": "✅",
                "blocked": "❌"
            }.get(status, "❓")
            msg += f"{status_emoji} **{tid}** - {title}\n"
            msg += f"   Status: `{status}` | Branch: `{branch}`\n\n"
            
        await update.message.reply_text(msg)
    except Exception as e:
        await update.message.reply_text(f"Erro ao ler Kanban: {str(e)}")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Exibe comandos rápidos do sistema."""
    msg = (
        "⚔️ **GUIA RÁPIDO DE COMANDOS - QG HÓRUS** ⚔️\n\n"
        "🎖️ **Personas (A Trindade)**\n"
        "• `/sargento` - Rígido, cobrança dura contra a procrastinação.\n"
        "• `/amigo` - Acolhedor, analítico e empático.\n"
        "• `/estrategista` - Focado em planejamento tático e sprints.\n\n"
        "📊 **Operações Diárias**\n"
        "• `/checkin` - Registro matinal de saúde (sono/peso).\n"
        "• `/descomprimir` - Encerramento de dia com extração de tarefas.\n"
        "• `/relatorio` - Sincronização de hábitos diários com o Obsidian Vault.\n"
        "• `/memoria` - Busca semântica no seu histórico de diários.\n\n"
        "🛠️ **Esteira de Desenvolvimento (Kanban)**\n"
        "• `/nova_task [ideia]` - Cria e refina uma nova ideia de código com o PO.\n"
        "• `/aprovar_task [ID]` - Roda o pipeline automático de Dev/QA (Git + Testes).\n"
        "• `/kanban` - Lista o quadro Kanban e branch ativa de cada tarefa.\n\n"
        "📚 Para uma explicação detalhada de cada fluxo e arquitetura, digite `/help_d`!"
    )
    await update.message.reply_text(msg)

async def help_detailed_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Exibe manual detalhado de cada comando e fluxo."""
    msg = (
        "📚 **MANUAL DETALHADO DO HÓRUS SYSTEM** 📚\n\n"
        "1️⃣ **COMO FUNCIONA O CHECK-IN MATINAL (`/checkin`)**\n"
        "O bot fará perguntas rápidas: hora que dormiu, hora que acordou, qualidade do sono (1-5), peso e sentimento. "
        "Seu peso é automaticamente persistido na tabela `registros_rotina` para acompanhamento de saúde física.\n\n"
        "2️⃣ **O PROCESSO DE DESCOMPRESSÃO ATIVA (`/descomprimir`)**\n"
        "Cole um desabafo ou notas soltas. Nossa IA extrairá sentimentos, lições aprendidas e **tarefas urgentes**, "
        "classificando-as na Curva ABC (`A`: crítico hoje, `B`: médio prazo, `C`: trivial) e salvando-as para o Obsidian.\n\n"
        "3️⃣ **COMO FUNCIONA O PIPELINE DE AGENTES DE DEV**\n"
        "• `/nova_task`: O **Product Owner (PO)** refina os requisitos da sua ideia e gera um ID exclusivo.\n"
        "• `/aprovar_task`: O **Tech Lead** cria as subtarefas técnicas, o **Dev Senior** escreve os códigos, "
        "o **QA Planner** cria cenários de testes e o **QA Executável** roda tudo no WSL (com até 3 auto-correções se falhar). "
        "Se passar, cria a branch `task-[ID]` e faz o merge automático na `master`!\n\n"
        "4️⃣ **AUTOCONSCIÊNCIA DOS AGENTES**\n"
        "Qualquer persona do chat conversacional conhece a própria estrutura técnica! Se você perguntar no chat normal: "
        "*'Quais tabelas existem no meu banco de dados?'* ou *'Como está estruturado meu projeto?'*, eles saberão responder com autoridade."
    )
    await update.message.reply_text(msg)

async def post_init(application: Application):
    """Inicializações em segundo plano após o bot subir."""
    try:
        from src.scheduler.routine_scheduler import RoutineScheduler
        scheduler = RoutineScheduler(application)
        scheduler.start()
    except Exception as e:
        print(f"Erro ao iniciar o agendador de lembretes: {str(e)}")

    try:
        from src.web.server import start_web_server_thread
        start_web_server_thread(port=5050)
    except Exception as e:
        print(f"Erro ao iniciar o servidor web do painel Hórus: {str(e)}")


def main():
    print("Iniciando motor unificado do Hórus System...")
    application = Application.builder().token(TOKEN).post_init(post_init).build()
    
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("checkin", checkin_start))
    application.add_handler(CommandHandler("descomprimir", descomprimir_start))
    application.add_handler(CommandHandler("relatorio", sincronizar_relatorio))
    application.add_handler(CommandHandler("memoria", memoria_start))
    
    # Comandos de Ajuda e Manual
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("help_d", help_detailed_command))
    
    # Comandos de Kanban de Desenvolvimento
    application.add_handler(CommandHandler("nova_task", nova_task))
    application.add_handler(CommandHandler("aprovar_task", aprovar_task))
    application.add_handler(CommandHandler("kanban", listar_kanban))
    
    # Comandos de Personas
    application.add_handler(CommandHandler("sargento", set_sargento))
    application.add_handler(CommandHandler("amigo", set_amigo))
    application.add_handler(CommandHandler("estrategista", set_estrategista))
    
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    application.run_polling()

if __name__ == "__main__":
    main()
