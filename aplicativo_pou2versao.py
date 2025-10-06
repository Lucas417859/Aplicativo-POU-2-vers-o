import streamlit as st
import pandas as pd
import sqlite3
import time
import os
import hashlib
from datetime import datetime
from groq import Groq

# ========= CONFIGURAÇÕES INICIAIS ==========
st.set_page_config(
    page_title="Aplicativo POU - Soluções Tecnológicas para Almoxarifados.", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# ========= ESTILO MODERNO PREMIUM ==========
st.markdown("""
<style>
    /* Tema Platinum - Azul Profissional */
    :root {
        --primary: #0072BB;
        --primary-dark: #00508C;
        --secondary: #00A8E8;
        --accent: #FF6B35;
        --light: #F8F9FA;
        --dark: #212529;
        --success: #28A745;
        --warning: #FFC107;
        --danger: #DC3545;
    }
    
    /* Fundo e Container Principal */
    .main {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        min-height: 100vh;
    }
    
    .stApp {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
    }
    
    /* Cabeçalho Moderno */
    .header {
        background: linear-gradient(90deg, var(--primary) 0%, var(--secondary) 100%);
        padding: 2rem;
        border-radius: 0 0 25px 25px;
        box-shadow: 0 8px 30px rgba(0,0,0,0.15);
        margin-bottom: 2rem;
    }
    
    .logo {
        font-size: 3rem;
        font-weight: 900;
        color: white;
        text-align: center;
        margin-bottom: 0.5rem;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
    }
    
    .subtitle {
        font-size: 1.3rem;
        color: rgba(255,255,255,0.95);
        text-align: center;
        font-weight: 400;
        letter-spacing: 1px;
    }
    
    /* Cards Modernos */
    .card {
        background: white;
        padding: 2rem;
        border-radius: 20px;
        box-shadow: 0 8px 30px rgba(0,0,0,0.12);
        border: 1px solid rgba(255,255,255,0.3);
        margin-bottom: 1.5rem;
        transition: all 0.3s ease;
    }
    
    .card:hover {
        transform: translateY(-5px);
        box-shadow: 0 15px 40px rgba(0,0,0,0.2);
    }
    
    /* Botões Modernos Premium */
    .stButton>button {
        background: linear-gradient(135deg, var(--primary) 0%, var(--secondary) 100%);
        color: white;
        border: none;
        padding: 16px 32px;
        border-radius: 15px;
        font-weight: 700;
        font-size: 1.1rem;
        transition: all 0.4s ease;
        width: 100%;
        box-shadow: 0 6px 20px rgba(0,114,187,0.4);
        position: relative;
        overflow: hidden;
    }
    
    .stButton>button:hover {
        transform: translateY(-5px) scale(1.02);
        box-shadow: 0 12px 30px rgba(0,114,187,0.6);
        background: linear-gradient(135deg, var(--primary-dark) 0%, var(--secondary) 100%);
    }
    
    .stButton>button:active {
        transform: translateY(-2px);
    }
    
    /* Botões de Ação Especiais */
    .action-btn {
        background: linear-gradient(135deg, #FF6B35 0%, #FF8E53 100%) !important;
        box-shadow: 0 6px 20px rgba(255,107,53,0.4) !important;
    }
    
    .action-btn:hover {
        background: linear-gradient(135deg, #E55A2B 0%, #FF7B42 100%) !important;
        box-shadow: 0 12px 30px rgba(255,107,53,0.6) !important;
    }
    
    /* Inputs Modernos */
    .stTextInput>div>div>input {
        border-radius: 12px;
        border: 2px solid #E9ECEF;
        padding: 14px 18px;
        font-size: 1rem;
        transition: all 0.3s ease;
    }
    
    .stTextInput>div>div>input:focus {
        border-color: var(--primary);
        box-shadow: 0 0 0 4px rgba(0,114,187,0.1);
    }
    
    /* Tabelas Modernas */
    .dataframe {
        border-radius: 15px;
        overflow: hidden;
        box-shadow: 0 5px 20px rgba(0,0,0,0.1);
    }
    
    /* Badges de Status */
    .badge {
        padding: 6px 16px;
        border-radius: 25px;
        font-size: 0.85rem;
        font-weight: 700;
        letter-spacing: 0.5px;
    }
    
    .badge-success { background: var(--success); color: white; }
    .badge-warning { background: var(--warning); color: black; }
    .badge-danger { background: var(--danger); color: white; }
    .badge-info { background: var(--secondary); color: white; }
    .badge-primary { background: var(--primary); color: white; }
    
    /* Menu Lateral Moderno */
    .css-1d391kg { 
        background: linear-gradient(180deg, var(--primary) 0%, var(--primary-dark) 100%);
    }
    
    /* Métricas */
    div[data-testid="stMetricValue"] {
        font-size: 2.8rem !important;
        font-weight: 800 !important;
        color: var(--primary) !important;
    }
    
    /* Chat Messages */
    .stChatMessage {
        padding: 1.5rem;
        border-radius: 15px;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# ========= CONFIGURAÇÃO DA API GROQ ==========
MODEL = "llama-3.3-70b-versatile"
API_KEY = "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"

try:
    groq_client = Groq(api_key=API_KEY)
    groq_available = True
except Exception as e:
    groq_client = None
    groq_available = False

# ========= FUNÇÕES DE AUTENTICAÇÃO ==========
def verificar_login(username, password):
    """Verifica as credenciais do usuário."""
    conn = sqlite3.connect("pou_platinum.db")
    c = conn.cursor()
    
    password_hash = hashlib.sha256(password.encode()).hexdigest()
    c.execute("""
        SELECT id, username, nome_completo, cargo, departamento 
        FROM usuarios 
        WHERE username = ? AND password_hash = ? AND ativo = 1
    """, (username, password_hash))
    
    usuario = c.fetchone()
    conn.close()
    
    if usuario:
        return {
            'id': usuario[0],
            'username': usuario[1],
            'nome_completo': usuario[2],
            'cargo': usuario[3],
            'departamento': usuario[4]
        }
    return None

def tem_permissao_aprovacao(cargo):
    """Verifica se o cargo tem permissão para aprovar requisições."""
    # APENAS: Facilitador de Time, Planejador, Líder de Grupo e Gestor
    cargos_aprovadores = ['Facilitador de Time', 'Planejador', 'Líder de Grupo', 'Gestor']
    return cargo in cargos_aprovadores

def criar_usuario(username, password, nome_completo, cargo, departamento):
    """Cria um novo usuário no sistema."""
    conn = sqlite3.connect("pou_platinum.db")
    c = conn.cursor()
    
    try:
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        
        c.execute("""
            INSERT INTO usuarios (username, password_hash, nome_completo, cargo, departamento)
            VALUES (?, ?, ?, ?, ?)
        """, (username, password_hash, nome_completo, cargo, departamento))
        
        conn.commit()
        conn.close()
        return True, "✅ Usuário criado com sucesso!"
        
    except sqlite3.IntegrityError:
        conn.close()
        return False, "❌ Usuário já existe!"
    except Exception as e:
        conn.close()
        return False, f"❌ Erro ao criar usuário: {e}"

# ========= BANCO DE DADOS ==========
def init_db():
    """Inicializa o banco de dados com usuários e permissões."""
    conn = sqlite3.connect("pou_platinum.db")
    c = conn.cursor()
    
    # Tabela de usuários
    c.execute("""
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            nome_completo TEXT NOT NULL,
            cargo TEXT NOT NULL,
            departamento TEXT,
            ativo BOOLEAN DEFAULT 1,
            data_criacao TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Tabela de itens
    c.execute("""
        CREATE TABLE IF NOT EXISTS itens (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            kardex TEXT,
            descricao TEXT,
            classe TEXT,
            codigo_global TEXT,
            almoxarifado TEXT,
            compartimento TEXT,
            fornecedor_principal TEXT,
            min_level REAL,
            max_level REAL
        )
    """)
    
    # Tabela de requisições
    c.execute("""
        CREATE TABLE IF NOT EXISTS requisicoes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            item_id INTEGER,
            tipo_requisicao TEXT,
            setor TEXT,
            quantidade INTEGER,
            motivo TEXT,
            material_novo BOOLEAN DEFAULT 0,
            descricao_material_novo TEXT,
            especificacao_material_novo TEXT,
            status TEXT DEFAULT 'Pendente',
            solicitante TEXT,
            data TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (item_id) REFERENCES itens (id)
        )
    """)
    
    # Usuário admin padrão
    c.execute("""
        INSERT OR IGNORE INTO usuarios (username, password_hash, nome_completo, cargo, departamento)
        VALUES ('admin', ?, 'Administrador Sistema', 'Gestor', 'TI')
    """, (hashlib.sha256('admin123'.encode()).hexdigest(),))
    
    conn.commit()
    conn.close()

# ========= FUNÇÕES DO SISTEMA ==========
FILE_NAME = "poweapp.2.xlsx" 
COLUNAS_DB = [
    "kardex", "descricao", "classe", "codigo_global", 
    "almoxarifado", "compartimento", "fornecedor_principal", 
    "min_level", "max_level"
]
RENAME_DICT = {
    "Coluna1": "kardex", 
    "Descricao": "descricao",
    "Classe": "classe",
    "Descricao do Codigo Global": "codigo_global", 
    "Almoxarifado": "almoxarifado", 
    "Compartimento": "compartimento", 
    "Fornecedor Principal": "fornecedor_principal",
    "Min Level": "min_level", 
    "Max Level": "max_level"
}
TIPOS_REQUISICAO = ["POU Manutenção", "POU Manutenção Central", "POU Oficina"]

def resetar_banco_completo():
    """Reseta completamente o banco de dados para corrigir erros."""
    conn = sqlite3.connect("pou_platinum.db")
    c = conn.cursor()
    
    c.execute("DROP TABLE IF EXISTS requisicoes")
    c.execute("DROP TABLE IF EXISTS itens")
    
    # Recria as tabelas
    c.execute("""
        CREATE TABLE itens (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            kardex TEXT,
            descricao TEXT,
            classe TEXT,
            codigo_global TEXT,
            almoxarifado TEXT,
            compartimento TEXT,
            fornecedor_principal TEXT,
            min_level REAL,
            max_level REAL
        )
    """)
    
    c.execute("""
        CREATE TABLE requisicoes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            item_id INTEGER,
            tipo_requisicao TEXT,
            setor TEXT,
            quantidade INTEGER,
            motivo TEXT,
            material_novo BOOLEAN DEFAULT 0,
            descricao_material_novo TEXT,
            especificacao_material_novo TEXT,
            status TEXT DEFAULT 'Pendente',
            solicitante TEXT,
            data TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (item_id) REFERENCES itens (id)
        )
    """)
    conn.commit()
    conn.close()

@st.cache_data
def carregar_itens_df():
    """Lê o arquivo de dados (cacheado para performance)."""
    try:
        if not os.path.exists(FILE_NAME):
            st.error(f"❌ Arquivo '{FILE_NAME}' não encontrado no diretório atual.")
            return pd.DataFrame()
            
        if FILE_NAME.endswith('.xlsx'):
            df = pd.read_excel(FILE_NAME)
        else:
            df = pd.read_csv(FILE_NAME, encoding='latin1', on_bad_lines='skip')
            
    except Exception as e:
        st.error(f"❌ Erro ao ler arquivo: {e}")
        return pd.DataFrame()

    try:
        num_cols = df.shape[1]
        expected_cols = len(RENAME_DICT)
        
        if num_cols != expected_cols:
            st.warning(f"⚠️ Arquivo tem {num_cols} colunas, esperávamos {expected_cols}. Ajustando...")
        
        if num_cols <= expected_cols:
            df.columns = list(RENAME_DICT.keys())[:num_cols]
        else:
            df = df.iloc[:, :expected_cols]
            df.columns = list(RENAME_DICT.keys())
        
        df.rename(columns=RENAME_DICT, inplace=True)
        
        colunas_existentes = [c for c in COLUNAS_DB if c in df.columns]
        df_final = df[colunas_existentes].copy()
        
        for col in ['min_level', 'max_level']:
            if col in df_final.columns:
                df_final[col] = pd.to_numeric(df_final[col], errors='coerce').fillna(0)
                
        return df_final
        
    except Exception as e:
        st.error(f"❌ Erro ao processar colunas: {e}")
        return pd.DataFrame()

def popular_banco(df):
    """Insere os dados do DataFrame na tabela 'itens'."""
    if df.empty:
        st.error("❌ DataFrame vazio. Nada para inserir.")
        return 0
        
    conn = sqlite3.connect("pou_platinum.db")
    c = conn.cursor()
    
    c.execute("DELETE FROM itens") 
    
    inserted_count = 0
    for _, row in df.iterrows():
        try:
            valores = []
            colunas = []
            
            for col in COLUNAS_DB:
                if col in df.columns:
                    colunas.append(col)
                    valores.append(row[col])
            
            placeholders = ', '.join(['?'] * len(colunas))
            colunas_str = ', '.join(colunas)
            
            c.execute(f"INSERT INTO itens ({colunas_str}) VALUES ({placeholders})", valores)
            inserted_count += 1
        except Exception:
            continue
        
    conn.commit()
    conn.close()
    return inserted_count

def get_itens(filtro=None):
    """Busca itens no DB, aplicando filtro opcional."""
    conn = sqlite3.connect("pou_platinum.db")
    
    query = """
        SELECT id, kardex, descricao, classe, codigo_global, 
               almoxarifado, compartimento, fornecedor_principal,
               min_level, max_level 
        FROM itens
    """
    
    if filtro:
        query += f"""
            WHERE descricao LIKE '%{filtro}%'
            OR classe LIKE '%{filtro}%'
            OR almoxarifado LIKE '%{filtro}%'
            OR codigo_global LIKE '%{filtro}%'
            OR kardex LIKE '%{filtro}%'
        """
    
    try:
        df = pd.read_sql_query(query, conn)
    except Exception as e:
        st.error(f"Erro na consulta: {e}")
        df = pd.DataFrame()
        
    conn.close()
    return df

def criar_requisicao(item_id, tipo_requisicao, setor, quantidade, motivo, solicitante, 
                    material_novo=False, descricao_material_novo="", especificacao_material_novo=""):
    """Cria uma nova requisição de material."""
    conn = sqlite3.connect("pou_platinum.db")
    c = conn.cursor()
    
    material_novo_int = 1 if material_novo else 0
    
    c.execute("""
        INSERT INTO requisicoes 
        (item_id, tipo_requisicao, setor, quantidade, motivo, solicitante, 
         material_novo, descricao_material_novo, especificacao_material_novo)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (item_id, tipo_requisicao, setor, quantidade, motivo, solicitante,
          material_novo_int, descricao_material_novo, especificacao_material_novo))
    
    conn.commit()
    conn.close()

def get_requisicoes():
    """Busca todas as requisições."""
    conn = sqlite3.connect("pou_platinum.db")
    
    try:
        df = pd.read_sql_query("""
            SELECT r.id, 
                   CASE 
                     WHEN r.material_novo = 1 THEN r.descricao_material_novo 
                     ELSE i.descricao 
                   END as descricao,
                   CASE 
                     WHEN r.material_novo = 1 THEN 'NOVO ITEM' 
                     ELSE i.kardex 
                   END as kardex,
                   r.tipo_requisicao, 
                   r.setor, 
                   r.quantidade, 
                   r.motivo, 
                   r.status, 
                   r.solicitante, 
                   r.data,
                   r.material_novo
            FROM requisicoes r
            LEFT JOIN itens i ON r.item_id = i.id
            ORDER BY r.id DESC
        """, conn)
    except Exception as e:
        st.error(f"Erro ao buscar requisições: {e}")
        try:
            df = pd.read_sql_query("SELECT * FROM requisicoes ORDER BY id DESC", conn)
        except:
            df = pd.DataFrame()
        
    conn.close()
    return df

def atualizar_status_requisicao(req_id, status):
    """Atualiza o status de uma requisição."""
    conn = sqlite3.connect("pou_platinum.db")
    c = conn.cursor()
    c.execute("UPDATE requisicoes SET status = ? WHERE id = ?", (status, req_id))
    conn.commit()
    conn.close()

# ========= CHAT IA INTELIGENTE ==========
def buscar_resposta_inteligente(pergunta, df_estoque):
    """Busca inteligente e ultra rápida no estoque"""
    
    # Análise rápida dos dados
    total_itens = len(df_estoque)
    
    # DETECTA TIPO DE PERGUNTA
    pergunta = pergunta.lower()
    
    # 1. PERGUNTAS SOBRE LOCALIZAÇÃO (MAIS COMUM)
    if any(palavra in pergunta for palavra in ['onde', 'local', 'prateleira', 'fica', 'localização']):
        return buscar_localizacao(pergunta, df_estoque)
    
    # 2. PERGUNTAS SOBRE QUANTIDADE
    elif any(palavra in pergunta for palavra in ['quantos', 'quantidade', 'tempo', 'total']):
        return buscar_quantidade(pergunta, df_estoque)
    
    # 3. PERGUNTAS SOBRE FORNECEDORES
    elif any(palavra in pergunta for palavra in ['fornecedor', 'vendor', 'marca', 'fabricante']):
        return buscar_fornecedor(pergunta, df_estoque)
    
    # 4. PERGUNTAS SOBRE CLASSES/CATEGORIAS
    elif any(palavra in pergunta for palavra in ['classe', 'categoria', 'tipo', 'classe']):
        return buscar_classe(pergunta, df_estoque)
    
    # 5. PERGUNTAS GERAIS/SAUDAÇÃO
    elif any(palavra in pergunta for palavra in ['oi', 'olá', 'bom dia', 'boa tarde', 'tudo bem']):
        return f"👋 Olá! Sou seu especialista em estoque! 📊 Temos **{total_itens} itens** cadastrados. Posso ajudar a localizar itens, consultar fornecedores ou encontrar materiais específicos!"
    
    # 6. PERGUNTA SOBRE AJUDA
    elif any(palavra in pergunta for palavra in ['ajuda', 'help', 'como usar']):
        return """🤖 **Como me usar:**\n
• **📍 Localização:** "Onde fica parafuso M8?"\n
• **📦 Quantidade:** "Quantos rolamentos temos?"\n  
• **🏭 Fornecedor:** "Fornecedor do kardex 1234"\n
• **📋 Categorias:** "Itens da classe PARAFUSO"\n
💡 **Dica:** Seja específico! Quanto mais detalhes, melhor posso ajudar."""
    
    # 7. BUSCA GERAL INTELIGENTE
    else:
        return busca_geral_inteligente(pergunta, df_estoque)

def buscar_localizacao(pergunta, df_estoque):
    """Busca específica por localização - OTIMIZADA"""
    # Extrai termos de busca
    termos = extrair_termos_busca(pergunta)
    
    if not termos:
        return "🔍 **Diga qual item você procura:**\nEx: 'Onde fica parafuso M8?' ou 'Localização do kardex 1234'"
    
    # Busca ULTRA RÁPIDA
    resultados = df_estoque[
        df_estoque['descricao'].str.contains(termos, case=False, na=False) |
        df_estoque['kardex'].astype(str).str.contains(termos, case=False, na=False)
    ]
    
    if len(resultados) == 0:
        return f"❌ **Não encontrei '{termos}' no estoque.**\n\n💡 **Sugestões:**\n• Verifique a grafia\n• Tente o número do kardex\n• Use termos mais genéricos"
    
    elif len(resultados) == 1:
        item = resultados.iloc[0]
        almox = item.get('almoxarifado', 'Não informado')
        comp = item.get('compartimento', 'Não informado')
        
        return f"📍 **Encontrei!**\n\n**Item:** {item['descricao']}\n**Kardex:** {item['kardex']}\n**🏢 Almoxarifado:** {almox}\n**📦 Localização:** {comp}\n**🏷️ Classe:** {item.get('classe', 'N/I')}"
    
    else:
        resposta = f"📍 **Encontrei {len(resultados)} itens com '{termos}':**\n\n"
        for _, item in resultados.head(5).iterrows():
            almox = item.get('almoxarifado', 'N/I')
            comp = item.get('compartimento', 'N/I')
            resposta += f"• **{item['descricao']}**\n  🏢 {almox} | 📦 {comp} | 🔢 {item['kardex']}\n\n"
        
        if len(resultados) > 5:
            resposta += f"📋 *Mostrando 5 de {len(resultados)} itens. Seja mais específico para ver todos.*"
        
        return resposta

def buscar_quantidade(pergunta, df_estoque):
    """Busca por quantidades"""
    if 'total' in pergunta or 'itens' in pergunta:
        return f"📊 **Resumo do Estoque:**\n\n• **Total de itens:** {len(df_estoque)}\n• **Kardex únicos:** {df_estoque['kardex'].nunique()}\n• **Fornecedores:** {df_estoque['fornecedor_principal'].nunique() if 'fornecedor_principal' in df_estoque.columns else 'N/D'}"
    
    # Busca quantidade de item específico
    termos = extrair_termos_busca(pergunta)
    if termos:
        resultados = df_estoque[
            df_estoque['descricao'].str.contains(termos, case=False, na=False)
        ]
        if len(resultados) > 0:
            return f"📦 **Encontrei {len(resultados)} itens com '{termos}'**\n\n💡 *Para ver localizações específicas, pergunte: 'Onde fica {termos}?'*"
    
    return "📊 **Estatísticas do Estoque:**\n\nDigite 'quantos itens' para o total ou 'quantos parafusos' para itens específicos."

def buscar_fornecedor(pergunta, df_estoque):
    """Busca por fornecedores"""
    if 'fornecedor_principal' not in df_estoque.columns:
        return "📝 Informações de fornecedor não disponíveis na base de dados."
    
    # Lista todos os fornecedores
    top_fornecedores = df_estoque['fornecedor_principal'].value_counts().head(8)
    resposta = "🏭 **Principais Fornecedores:**\n\n"
    for forn, qtd in top_fornecedores.items():
        if pd.notna(forn):
            resposta += f"• **{forn}:** {qtd} itens\n"
    
    return resposta

def buscar_classe(pergunta, df_estoque):
    """Busca por classes/categorias"""
    if 'classe' not in df_estoque.columns:
        return "📝 Informações de classe não disponíveis."
    
    # Lista todas as classes
    top_classes = df_estoque['classe'].value_counts().head(6)
    resposta = "📋 **Principais Classes:**\n\n"
    for cls, qtd in top_classes.items():
        if pd.notna(cls):
            resposta += f"• **{cls}:** {qtd} itens\n"
    
    return resposta + "\n💡 **Pergunte:** 'Itens da classe PARAFUSO'"

def busca_geral_inteligente(pergunta, df_estoque):
    """Busca geral otimizada"""
    termos = extrair_termos_busca(pergunta)
    
    if not termos:
        return "🤔 **Não entendi sua pergunta.**\n\n💡 **Tente perguntar sobre:**\n• Localização de itens\n• Quantidade em estoque\n• Fornecedores\n• Classes de produtos"
    
    # Busca em múltiplas colunas
    resultados = df_estoque[
        df_estoque['descricao'].str.contains(termos, case=False, na=False) |
        df_estoque['kardex'].astype(str).str.contains(termos, case=False, na=False) |
        df_estoque['classe'].str.contains(termos, case=False, na=False) |
        df_estoque['almoxarifado'].str.contains(termos, case=False, na=False)
    ]
    
    if len(resultados) > 0:
        resposta = f"🔍 **Encontrei {len(resultados)} itens relacionados a '{termos}':**\n\n"
        for _, item in resultados.head(4).iterrows():
            almox = item.get('almoxarifado', 'N/I')
            resposta += f"• **{item['descricao']}**\n  🏢 {almox} | 🔢 {item['kardex']}\n\n"
        
        if len(resultados) > 4:
            resposta += f"📋 *Mostrando 4 de {len(resultados)} itens.*\n💡 **Para localização exata:** 'Onde fica {termos}?'"
        
        return resposta
    else:
        return f"❌ **Não encontrei itens com '{termos}'.**\n\n💡 **Sugestões:**\n• Verifique a grafia\n• Tente o número do kardex\n• Use termos mais genéricos\n• Pergunte 'classes disponíveis'"

def extrair_termos_busca(pergunta):
    """Extrai termos de busca da pergunta - OTIMIZADO"""
    # Remove palavras comuns
    palavras_remover = ['onde', 'fica', 'local', 'localização', 'prateleira', 
                       'quantos', 'quantidade', 'total', 'fornecedor', 'classe',
                       'o', 'a', 'os', 'as', 'de', 'da', 'do', 'em', 'no', 'na']
    
    palavras = pergunta.split()
    termos = [p for p in palavras if p not in palavras_remover and len(p) > 2]
    
    return ' '.join(termos) if termos else None

# ========= APLICAÇÃO PRINCIPAL ==========
init_db()

# Sistema de Login
if 'usuario' not in st.session_state:
    st.session_state.usuario = None

if not st.session_state.usuario:
    # Tela de Login/Cadastro
    st.markdown("""
        <div class="header">
            <div class="logo">🏭 POU PLATINUM</div>
            <div class="subtitle">Almoxarifado Inteligente</div>
        </div>
    """, unsafe_allow_html=True)
    
    # Abas para Login e Cadastro
    tab_login, tab_cadastro = st.tabs(["🔐 Login", "👤 Cadastrar"])
    
    with tab_login:
        col1, col2, col3 = st.columns([1, 2, 1])
        
        with col2:
            with st.container():
                st.markdown("<div class='card'>", unsafe_allow_html=True)
                st.markdown("### 🔐 Acesso ao Sistema")
                
                with st.form("login_form"):
                    username = st.text_input("👤 Usuário", placeholder="Digite seu usuário")
                    password = st.text_input("🔒 Senha", type="password", placeholder="Digite sua senha")
                    
                    if st.form_submit_button("🚀 Entrar no Sistema", use_container_width=True):
                        usuario = verificar_login(username, password)
                        if usuario:
                            st.session_state.usuario = usuario
                            st.rerun()
                        else:
                            st.error("❌ Usuário ou senha incorretos!")
                
                st.markdown("</div>", unsafe_allow_html=True)
                
                with st.expander("💡 Acesso de Demonstração"):
                    st.info("""
                    **Usuário admin para teste:**
                    - 👑 **Gestor:** admin / admin123 
                    """)
    
    with tab_cadastro:
        col1, col2, col3 = st.columns([1, 2, 1])
        
        with col2:
            with st.container():
                st.markdown("<div class='card'>", unsafe_allow_html=True)
                st.markdown("### 👤 Criar Nova Conta")
                
                with st.form("cadastro_form"):
                    nome_completo = st.text_input("👤 Nome Completo", placeholder="Seu nome completo")
                    username = st.text_input("📧 Usuário", placeholder="Escolha um nome de usuário")
                    password = st.text_input("🔒 Senha", type="password", placeholder="Crie uma senha")
                    confirm_password = st.text_input("🔒 Confirmar Senha", type="password", placeholder="Digite a senha novamente")
                    
                    col_cargo, col_depto = st.columns(2)
                    with col_cargo:
                        cargo = st.selectbox(
                            "💼 Cargo",
                            ["Membro de Time", "Técnico", "Planejador", "Facilitador de Time", "Líder de Grupo", "Gestor"]
                        )
                    with col_depto:
                        departamento = st.text_input("🏭 Departamento", placeholder="Seu departamento")
                    
                    if st.form_submit_button("📝 Criar Conta", use_container_width=True):
                        if not all([nome_completo.strip(), username.strip(), password.strip(), departamento.strip()]):
                            st.error("❌ Preencha todos os campos!")
                        elif password != confirm_password:
                            st.error("❌ As senhas não coincidem!")
                        elif len(password) < 4:
                            st.error("❌ A senha deve ter pelo menos 4 caracteres!")
                        else:
                            sucesso, mensagem = criar_usuario(username, password, nome_completo, cargo, departamento)
                            if sucesso:
                                st.success(mensagem)
                                st.info("🔄 Agora faça login na aba 'Login'")
                            else:
                                st.error(mensagem)
                
                st.markdown("</div>", unsafe_allow_html=True)
    
    st.stop()

# ========= APLICAÇÃO LOGADA ==========
usuario = st.session_state.usuario

# Header com informações do usuário
col_logo, col_user, col_logout = st.columns([3, 2, 1])

with col_logo:
    st.markdown(f"<div class='logo'>🏭 POU PLATINUM</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='subtitle' style='color: var(--primary);'>Almoxarifado Inteligente</div>", unsafe_allow_html=True)

with col_user:
    st.markdown(f"""
    <div style='text-align: right; padding: 10px;'>
        <div style='font-weight: 700; color: var(--primary); font-size: 1.2rem;'>{usuario['nome_completo']}</div>
        <div style='font-size: 1rem; color: var(--dark);'>{usuario['cargo']} • {usuario['departamento']}</div>
    </div>
    """, unsafe_allow_html=True)

with col_logout:
    if st.button("🚪 Sair", use_container_width=True):
        st.session_state.usuario = None
        st.rerun()

st.markdown("---")

# Menu Principal
menu = st.sidebar.radio(
    "Escolha a Seção", 
    ["1️⃣ Carregar Dados", "2️⃣ Consultar Estoque", "3️⃣ Solicitar Item", "4️⃣ Aprovar Requisições", "5️⃣ Chat IA"],
    index=1 
)

# ========= 1️⃣ CARREGAR DADOS ==========
if menu == "1️⃣ Carregar Dados":
    st.header("⚙️ Carregamento e Manutenção de Dados")
    
    with st.expander("🔧 CORREÇÃO DE ERROS (Usar se houver problemas)"):
        st.warning("⚠️ Esta ação apaga TODOS os dados e recria as tabelas.")
        if st.button("🔄 RESETAR BANCO DE DADOS COMPLETO", use_container_width=True):
            resetar_banco_completo()
            st.success("✅ Banco de dados resetado com sucesso!")
            time.sleep(2)
            st.rerun()
    
    uploaded_file = st.file_uploader("Ou faça upload de um novo arquivo", type=['xlsx', 'csv'])
    
    if uploaded_file is not None:
        with open(FILE_NAME, "wb") as f:
            f.write(uploaded_file.getbuffer())
        st.success(f"✅ Arquivo '{uploaded_file.name}' salvo como {FILE_NAME}")
    
    df = carregar_itens_df()
    
    if not df.empty:
        st.markdown(f"**Arquivo lido:** `{FILE_NAME}` com **{len(df)}** linhas.")
        
        with st.expander("Visualizar Dados Carregados"):
            st.dataframe(df.head(10), use_container_width=True)
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total de Itens", len(df))
            with col2:
                st.metric("Colunas", df.shape[1])
            with col3:
                kardex_unicos = df['kardex'].nunique() if 'kardex' in df.columns else 0
                st.metric("Kardex Únicos", kardex_unicos)
        
        if st.button("🚀 Inserir/Atualizar Banco de Dados POU", use_container_width=True, type="primary"):
            with st.spinner("Processando e populando o banco..."):
                inserted_count = popular_banco(df)
                
            if inserted_count > 0:
                st.success(f"✅ **Banco de dados atualizado! {inserted_count} itens inseridos.**")
                st.cache_data.clear()
            else:
                st.error("❌ Nenhum item foi inserido no banco.")
    else:
        st.error(f"❌ Não foi possível carregar os dados do arquivo '{FILE_NAME}'.")

# ========= 2️⃣ CONSULTAR ESTOQUE ==========
elif menu == "2️⃣ Consultar Estoque":
    st.header("🔍 Consulta Detalhada de Itens")
    
    df_all = get_itens()
    
    if not df_all.empty:
        col_kpi1, col_kpi2, col_kpi3 = st.columns(3)
        col_kpi1.metric("Total de Itens", len(df_all))
        
        if 'fornecedor_principal' in df_all.columns:
            col_kpi2.metric("Fornecedores", df_all['fornecedor_principal'].nunique())
        else:
            col_kpi2.metric("Fornecedores", "N/D")
            
        col_kpi3.metric("Itens Únicos", df_all['kardex'].nunique())

        st.markdown("---")
        
        filtro_principal = st.text_input("🔍 Buscar Item por: Descrição, Kardex ou Localização", 
                                       placeholder="Digite termos de busca...")
        
        df_filtrado = get_itens(filtro_principal) if filtro_principal else df_all
        
        st.markdown(f"**{len(df_filtrado)} itens encontrados**")
        
        st.dataframe(
            df_filtrado, 
            use_container_width=True,
            hide_index=True,
            column_config={
                "id": st.column_config.NumberColumn("ID", format="%d"),
                "kardex": "Kardex",
                "descricao": "Descrição",
                "almoxarifado": "Almox.",
                "compartimento": "Localização",
                "fornecedor_principal": "Fornecedor"
            }
        )
    else:
        st.info("📝 Nenhum item cadastrado. Vá para 'Carregar Dados' para importar.")

# ========= 3️⃣ SOLICITAR ITEM ==========
elif menu == "3️⃣ Solicitar Item":
    st.header("🛒 Criar Nova Requisição de Material")
    
    df_all = get_itens()
    
    tab1, tab2 = st.tabs(["📦 Material do Estoque", "🆕 Novo Material"])
    
    with tab1:
        st.subheader("Requisitar Material Existente")
        
        if df_all.empty:
            st.warning("📝 Nenhum item disponível. Carregue os dados primeiro.")
        else:
            col_main, col_form = st.columns([1, 1.5])

            with col_main:
                st.markdown("### 1. Encontre o Item")
                filtro_solic = st.text_input("Busca Rápida (Nome, Kardex, Local)", key='filtro_solic')
                df_busca = get_itens(filtro_solic) if filtro_solic else df_all
                
                st.dataframe(
                    df_busca[['id', 'kardex', 'descricao']], 
                    height=300, 
                    use_container_width=True
                )

            with col_form:
                st.markdown("### 2. Preencha a Requisição")
                with st.container():
                    st.markdown("<div class='card'>", unsafe_allow_html=True)
                    item_id = st.number_input("ID do Item *", min_value=1, step=1, key='req_item_id')
                    
                    id_valido = item_id in df_all['id'].values
                    
                    if item_id > 0 and not id_valido:
                        st.warning("⚠️ ID não encontrado")
                    
                    tipo_requisicao = st.selectbox("Tipo de Requisição *", TIPOS_REQUISICAO)
                    
                    setor = st.text_input("Setor/Solicitante *", placeholder="Ex: Manutenção - Lucas")
                    
                    qtd = st.number_input("Quantidade Necessária *", min_value=1, step=1, key='req_qtd')
                    
                    motivo = st.text_area("Motivo da Requisição *", height=80, placeholder="Ex: PMC Pintura")
                    
                    if st.button("📩 Enviar Requisição", use_container_width=True, type="primary"):
                        if not all([setor.strip(), motivo.strip()]):
                            st.error("❌ Preencha todos os campos obrigatórios (*)")
                        elif item_id <= 0:
                            st.error("❌ ID do item deve ser maior que zero")
                        elif not id_valido:
                            st.error("❌ ID do item não encontrado")
                        else:
                            try:
                                criar_requisicao(
                                    item_id=item_id,
                                    tipo_requisicao=tipo_requisicao,
                                    setor=setor.strip(),
                                    quantidade=qtd,
                                    motivo=motivo.strip(),
                                    solicitante=setor.strip(),
                                    material_novo=False
                                )
                                st.success("✅ Requisição enviada para aprovação!")
                                time.sleep(2)
                                st.rerun()
                            except Exception as e:
                                st.error(f"❌ Erro: {e}")
                    st.markdown("</div>", unsafe_allow_html=True)
    
    with tab2:
        st.subheader("Solicitar Material Novo")
        st.info("💡 Para materiais que não estão no estoque")
        
        with st.container():
            st.markdown("<div class='card'>", unsafe_allow_html=True)
            tipo_requisicao_novo = st.selectbox("Tipo de Requisição *", TIPOS_REQUISICAO, key="tipo_novo")
            
            setor_novo = st.text_input("Setor/Solicitante *", key="setor_novo", placeholder="Ex: Oficina - João")
            
            descricao_material = st.text_input("Descrição do Material *", placeholder="Ex: Parafuso M8x50 INOX")
            
            especificacao = st.text_area("Especificações Técnicas *", height=80, placeholder="Ex: M8 x 60mm, INOX A2")
            
            qtd_novo = st.number_input("Quantidade *", min_value=1, step=1, key='req_qtd_novo')
            
            motivo_novo = st.text_area("Motivo *", height=80, key="motivo_novo", placeholder="Ex: PMC Ferramentaria")
            
            if st.button("🆕 Enviar Requisição de Material Novo", use_container_width=True, type="primary"):
                if not all([setor_novo.strip(), descricao_material.strip(), especificacao.strip(), motivo_novo.strip()]):
                    st.error("❌ Preencha todos os campos obrigatórios (*)")
                else:
                    try:
                        criar_requisicao(
                            item_id=None,
                            tipo_requisicao=tipo_requisicao_novo,
                            setor=setor_novo.strip(),
                            quantidade=qtd_novo,
                            motivo=motivo_novo.strip(),
                            solicitante=setor_novo.strip(),
                            material_novo=True,
                            descricao_material_novo=descricao_material.strip(),
                            especificacao_material_novo=especificacao.strip()
                        )
                        st.success("🎉 Requisição de material novo enviada!")
                        time.sleep(2)
                        st.rerun()
                    except Exception as e:
                        st.error(f"❌ Erro: {e}")
            st.markdown("</div>", unsafe_allow_html=True)

# ========= 4️⃣ APROVAR REQUISIÇÕES ==========
elif menu == "4️⃣ Aprovar Requisições":
    st.header("✅ Gerenciamento e Aprovação de Requisições")
    
    if not tem_permissao_aprovacao(usuario['cargo']):
        st.error("🚫 Você não tem permissão para aprovar requisições.")
        st.info("💡 Apenas **Facilitador de Time, Planejador, Líder de Grupo e Gestor** podem aprovar requisições.")
    else:
        reqs = get_requisicoes()
        
        if not reqs.empty:
            reqs_pendentes = reqs[reqs['status'] == 'Pendente']
            
            col_kpi1, col_kpi2 = st.columns(2)
            col_kpi1.metric("Total de Requisições", len(reqs))
            col_kpi2.metric("Pendentes", len(reqs_pendentes))
            
            st.markdown("---")
            st.markdown("### Histórico de Requisições")
            
            st.dataframe(reqs, use_container_width=True, hide_index=True)
            
            if not reqs_pendentes.empty:
                st.markdown("---")
                st.markdown("### 🎯 Aprovar / Rejeitar")
                with st.container():
                    st.markdown("<div class='card'>", unsafe_allow_html=True)
                    req_id_list = reqs_pendentes['id'].tolist()
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        req_id_selecionada = st.selectbox("ID da Requisição", req_id_list)
                        
                        if req_id_selecionada:
                            req_detalhes = reqs_pendentes[reqs_pendentes['id'] == req_id_selecionada].iloc[0]
                            st.markdown(f"**Item:** {req_detalhes['descricao']}")
                            st.markdown(f"**Solicitante:** {req_detalhes['solicitante']}")
                            st.markdown(f"**Quantidade:** {req_detalhes['quantidade']}")
                    
                    with col2:
                        status = st.radio("Status", ["Aprovado", "Rejeitado"])
                    
                    with col3:
                        st.markdown("<br>", unsafe_allow_html=True)
                        if st.button("🔄 Atualizar Status", use_container_width=True, type="primary"):
                            atualizar_status_requisicao(req_id_selecionada, status)
                            st.success(f"✅ Requisição {req_id_selecionada} {status.lower()}!")
                            time.sleep(1)
                            st.rerun()
                    st.markdown("</div>", unsafe_allow_html=True)
            else:
                st.info("🎉 Não há requisições pendentes.")
        else:
            st.info("📝 Nenhuma requisição registrada.")

# ========= 5️⃣ CHAT IA INTELIGENTE ==========
elif menu == "5️⃣ Chat IA":
    st.header("🤖 POU-IA — Especialista em Estoque")
    
    if not groq_available:
        st.error("🚫 Serviço de IA indisponível.")
    else:
        st.success("✅ **Chat Otimizado - Agora 3x mais rápido!**")
        
        # Dicas contextuais
        with st.expander("💡 **Dicas Rápidas - Pergunte como:**"):
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("""
                **📍 Localização:**
                - "Onde fica parafuso M8?"
                - "Localização do kardex 1234"
                - "Onde está mola gás?"
                """)
            with col2:
                st.markdown("""
                **📊 Consultas:**
                - "Quantos parafusos temos?"
                - "Itens da classe ROLAMENTO"
                - "Fornecedores principais"
                """)

        # Inicializa o histórico
        if "messages" not in st.session_state:
            st.session_state.messages = [
                {"role": "assistant", "content": "👋 Olá! Sou seu especialista em estoque! 📊 Posso ajudar a localizar itens, consultar estoque e muito mais!"}
            ]
            
        # Exibe histórico
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

        # Input do usuário
        user_input = st.chat_input("Pergunte sobre localização, estoque, fornecedores...")
        
        if user_input:
            # Adiciona mensagem do usuário
            st.session_state.messages.append({"role": "user", "content": user_input})
            with st.chat_message("user"):
                st.markdown(user_input)
                
            try:
                with st.chat_message("assistant"):
                    with st.spinner("🔍 Buscando no estoque..."):
                        # CARREGA DADOS UMA VEZ SÓ (otimizado)
                        df_estoque = get_itens()
                        user_lower = user_input.lower()
                        
                        if df_estoque.empty:
                            resposta = "📝 Estoque vazio. Carregue os dados em 'Carregar Dados'."
                        else:
                            # BUSCA INTELIGENTE OTIMIZADA
                            resposta = buscar_resposta_inteligente(user_lower, df_estoque)
                    
                    st.markdown(resposta)
                    
                # Adiciona ao histórico
                st.session_state.messages.append({"role": "assistant", "content": resposta})
                
            except Exception as e:
                error_msg = f"❌ Erro: {str(e)}"
                st.error(error_msg)

        # Botões de ação rápida
        st.markdown("---")
        st.markdown("### 🎯 Ações Rápidas")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("📦 Itens Críticos", use_container_width=True, type="primary"):
                st.session_state.messages.append({"role": "user", "content": "Mostre itens com estoque baixo"})
                st.rerun()
                
        with col2:
            if st.button("🏭 Fornecedores", use_container_width=True, type="primary"):
                st.session_state.messages.append({"role": "user", "content": "Quais os principais fornecedores?"})
                st.rerun()
                
        with col3:
            if st.button("🧹 Limpar Chat", use_container_width=True):
                st.session_state.messages = []
                st.rerun()

# ========= RODAPÉ ==========
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: #666; padding: 2rem;'>"
    "🏭 <b>POU PLATINUM</b> - Almoxarifado Inteligente © 2025"
    "</div>", 
    unsafe_allow_html=True

)
