import sqlite3
import os

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DB_PATH = os.path.join(ROOT_DIR, "data", "agent.db")

def init_db():
    """Inicializa as tabelas necessárias no SQLite."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # 1. Tabela para logs de Rotinas
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS rotinas_log (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        data TEXT NOT NULL,
        bloco TEXT NOT NULL,
        items_total INTEGER NOT NULL,
        items_cumpridos INTEGER NOT NULL,
        kpi_porcentagem REAL NOT NULL,
        observacoes TEXT
    );
    """)

    # 2. Tabela para Checkin de Saúde e Sono
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS checkin_saude (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        data TEXT UNIQUE NOT NULL,
        hora_dormiu TEXT,
        hora_acordou TEXT,
        nota_sono INTEGER,
        peso REAL,
        relato_sono TEXT,
        relato_acordar TEXT
    );
    """)

    # 3. Tabela para Descompressão Diária
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS logs_descompressao (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        data TEXT NOT NULL,
        categoria TEXT NOT NULL,
        conteudo_bruto TEXT NOT NULL,
        analise_ia TEXT NOT NULL,
        decisoes_tomadas TEXT
    );
    """)

    # 4. Tabela de Insights e Conversas
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS conversas_insights (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        data TEXT NOT NULL,
        titulo TEXT,
        conteudo TEXT NOT NULL
    );
    """)

    # 5. Tabela de Registros de Rotinas (Projeto Hórus)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS registros_rotina (
        id TEXT PRIMARY KEY,           -- Hash Composto: 'data-rotina_id' (ex: '2026-05-27-acordar')
        rotina_id TEXT NOT NULL,       -- ex: 'acordar'
        data TEXT NOT NULL,            -- ex: '2026-05-27'
        acoes_concluidas TEXT,         -- JSON array: ["acordar_01", "acordar_03"]
        acoes_puladas TEXT,            -- JSON array: ["acordar_02"]
        dados_capturados TEXT,         -- JSON Object: {"peso_kg": 83}
        horarios_reais TEXT,           -- JSON Object: {"acordar_01": "06:05"}
        observacoes TEXT,              -- Anotações do dia
        status TEXT                    -- 'completo', 'parcial', 'incompleto'
    );
    """)

    # 6. Tabela de Itens Segundo Cérebro (Projeto Hórus)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS itens_segundo_cerebro (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        data_registro TEXT NOT NULL,   -- YYYY-MM-DD
        tipo TEXT NOT NULL,            -- 'tarefa', 'projeto', 'nota', 'meta'
        curva TEXT NOT NULL,           -- 'A', 'B', 'C' (Curva ABC)
        tempo TEXT NOT NULL,           -- 'hoje', 'semana', 'mes', 'ano'
        conteudo TEXT NOT NULL,        -- Conteúdo principal da nota/insight
        projeto_id TEXT,               -- Referência à empresa/projeto em config.json
        tags TEXT,                     -- JSON array de tags anexadas
        status TEXT NOT NULL           -- 'pendente_sincronia', 'sincronizado_obsidian'
    );
    """)

    # 7. Tabela de Memórias do Usuário (Projeto Hórus)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS memorias_usuario (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        categoria TEXT,                -- 'preferencia', 'comportamento', 'decisao', 'sentimento'
        fato TEXT NOT NULL,            -- ex: "Evita fazer listas longas sob efeito de ansiedade"
        data_aprendizado TEXT,         -- YYYY-MM-DD
        importancia INTEGER            -- Grau de importância de 1 a 5
    );
    """)

    # 8. Tabela de Tarefas Kanban (Desenvolvimento de Software)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS kanban_tasks (
        id TEXT PRIMARY KEY,
        titulo TEXT NOT NULL,
        descricao_original TEXT NOT NULL,
        requisitos_refinados TEXT,
        subtarefas_json TEXT,
        branch_name TEXT,
        status TEXT NOT NULL,          -- 'backlog', 'refining', 'developing', 'testing', 'done', 'blocked'
        relatorio_qa TEXT
    );
    """)

    conn.commit()
    conn.close()
    print(f"Banco de dados SQLite inicializado com sucesso em: {DB_PATH}")

if __name__ == "__main__":
    init_db()
