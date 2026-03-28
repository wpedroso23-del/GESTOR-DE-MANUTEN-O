import streamlit as st
import pandas as pd
import os
import base64
from datetime import datetime, timedelta
import plotly.express as px
import plotly.io as pio
from supabase import create_client

# =========================
# CONFIGURAÇÃO INICIAL
# =========================
st.set_page_config(
    page_title="Gestão de Manutenção Industrial",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =========================
# CONEXÃO COM SUPABASE
# =========================
url = os.getenv("SUPABASE_URL", "https://tvkgykvbzuciqueitov.supabase.co")
key = os.getenv("SUPABASE_KEY", "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InR2a2d5a3ZienVjaXF1ZWl0b292Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzQ1NDQwMDAsImV4cCI6MjA5MDEyMDAwMH0.2u9cSsglEnX6lBANs1P117c4iKgeh7TZHX3XM1Ma7FY")
supabase = None
supabase_conectado = False

if key:
    try:
        supabase = create_client(url, key)
        supabase_conectado = True
        st.subheader("Teste conexão Supabase")
        res = supabase.table("empresas").select("*").limit(1).execute()
        st.write(res.data)
    except Exception as e:
        st.warning("Supabase não conectado. O sistema continuará funcionando com arquivos CSV locais.")
        st.caption(str(e))
else:
    st.info("SUPABASE_KEY não configurada. O sistema continuará funcionando com arquivos CSV locais.")

# =========================
# ESTADO INICIAL
# =========================
if "nome_empresa" not in st.session_state:
    st.session_state.nome_empresa = "Sua Empresa"

if "logo_empresa_bytes" not in st.session_state:
    st.session_state.logo_empresa_bytes = None

if "mensagem_om_salva" not in st.session_state:
    st.session_state.mensagem_om_salva = ""

if "usuario_logado" not in st.session_state:
    st.session_state.usuario_logado = False

if "empresa_logada" not in st.session_state:
    st.session_state.empresa_logada = ""

if "usuario_atual" not in st.session_state:
    st.session_state.usuario_atual = ""

if "validade_assinatura" not in st.session_state:
    st.session_state.validade_assinatura = ""

if "is_admin_master" not in st.session_state:
    st.session_state.is_admin_master = False

# =========================
# CORES PADRÃO
# =========================
COR_AZUL = "#2563eb"
COR_AZUL_CLARO = "#60a5fa"
COR_AZUL_ESCURO = "#1d4ed8"
COR_VERMELHO = "#ef4444"
COR_AMARELO = "#f59e0b"
COR_VERDE = "#10b981"
PALETA_GRAFICOS = [COR_AZUL, COR_AZUL_CLARO, COR_VERMELHO, COR_AMARELO, COR_VERDE]

# =========================
# ESTILO VISUAL
# =========================
st.markdown("""
<style>
    .stApp {
        background: linear-gradient(180deg, #f4f7fb 0%, #eef3f9 100%);
    }

    .main-title {
        font-size: 2rem;
        font-weight: 800;
        color: #0f172a;
        margin-bottom: 0.2rem;
    }

    .sub-title {
        color: #475569;
        margin-bottom: 1rem;
    }

    .company-title {
        font-size: 1.15rem;
        font-weight: 700;
        color: #1d4ed8;
        margin-top: 0.25rem;
        margin-bottom: 0.75rem;
    }

    div[data-testid="stMetric"] {
        background-color: white;
        border: 1px solid #dbe4f0;
        padding: 14px;
        border-radius: 16px;
        box-shadow: 0 2px 10px rgba(15, 23, 42, 0.06);
    }

    div[data-testid="stDataFrame"] {
        background-color: white;
        border-radius: 14px;
        padding: 4px;
    }

    .block-container {
        padding-top: 1.2rem;
        padding-bottom: 2rem;
    }

    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0f172a 0%, #1e293b 100%);
    }

    section[data-testid="stSidebar"] * {
        color: white !important;
    }

    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }

    .stTabs [data-baseweb="tab"] {
        background-color: #e2e8f0;
        border-radius: 10px;
        padding: 8px 14px;
    }

    .stTabs [aria-selected="true"] {
        background-color: #2563eb !important;
        color: white !important;
    }

    .stButton>button, .stFormSubmitButton>button, .stDownloadButton>button {
        border-radius: 10px;
        border: none;
        background: #2563eb;
        color: white;
        font-weight: 600;
    }

    .stButton>button:hover, .stFormSubmitButton>button:hover, .stDownloadButton>button:hover {
        background: #1d4ed8;
        color: white;
    }

    div[data-baseweb="input"] > div,
    div[data-baseweb="select"] > div,
    textarea,
    input[type="text"],
    input[type="number"] {
        background-color: #fff8db !important;
        color: #0f172a !important;
        border: 1px solid #d6c76a !important;
        border-radius: 10px !important;
    }

    textarea:focus,
    input:focus {
        border: 1px solid #2563eb !important;
        box-shadow: 0 0 0 1px #2563eb !important;
    }

    .logo-box {
        text-align: center;
        margin-bottom: 8px;
    }

    .info-hora {
        background: #eff6ff;
        color: #1e3a8a;
        border: 1px solid #bfdbfe;
        padding: 10px 12px;
        border-radius: 10px;
        margin-bottom: 12px;
        font-weight: 600;
    }

    .login-card {
        max-width: 520px;
        margin: 2rem auto;
        background: white;
        padding: 1.5rem;
        border-radius: 18px;
        border: 1px solid #dbe4f0;
        box-shadow: 0 8px 24px rgba(15, 23, 42, 0.08);
    }

    .login-title {
        font-size: 1.5rem;
        font-weight: 800;
        color: #0f172a;
        margin-bottom: 0.35rem;
        text-align: center;
    }

    .login-subtitle {
        color: #475569;
        margin-bottom: 1rem;
        text-align: center;
    }

</style>
""", unsafe_allow_html=True)


# =========================
# CONTROLE DE ACESSO E ASSINATURA
# =========================
ARQ_ASSINATURAS = "empresas_assinaturas.csv"
COLUNAS_ASSINATURAS = ["Empresa", "Usuario", "Senha", "Validade", "Ativo", "Admin Master"]

def slug_empresa(nome):
    nome = str(nome).strip().lower()
    mapa = {
        "á": "a", "à": "a", "ã": "a", "â": "a",
        "é": "e", "ê": "e",
        "í": "i",
        "ó": "o", "ô": "o", "õ": "o",
        "ú": "u",
        "ç": "c"
    }
    for k, v in mapa.items():
        nome = nome.replace(k, v)
    nome = "".join(ch if ch.isalnum() else "_" for ch in nome)
    while "__" in nome:
        nome = nome.replace("__", "_")
    return nome.strip("_") or "empresa"

def carregar_csv_bruto(arquivo, colunas):
    if os.path.exists(arquivo):
        try:
            df = pd.read_csv(arquivo, encoding="utf-8")
            for col in colunas:
                if col not in df.columns:
                    df[col] = ""
            return df[colunas]
        except Exception:
            return pd.DataFrame(columns=colunas)
    return pd.DataFrame(columns=colunas)

def salvar_csv_bruto(df, arquivo):
    try:
        pasta = os.path.dirname(arquivo)
        if pasta:
            os.makedirs(pasta, exist_ok=True)
        df.to_csv(arquivo, index=False, encoding="utf-8")
    except Exception as e:
        st.error(f"Erro ao salvar arquivo {arquivo}: {e}")

def inicializar_assinaturas():
    if not os.path.exists(ARQ_ASSINATURAS):
        df = pd.DataFrame([{
            "Empresa": "Administrador Master",
            "Usuario": "admin",
            "Senha": "admin123",
            "Validade": "2099-12-31",
            "Ativo": "Sim",
            "Admin Master": "Sim"
        }], columns=COLUNAS_ASSINATURAS)
        salvar_csv_bruto(df, ARQ_ASSINATURAS)

def obter_caminho_arquivo(arquivo):
    arquivos_base = [ARQ_EQUIP, ARQ_COLAB, ARQ_OM]
    if arquivo not in arquivos_base:
        return arquivo

    empresa = st.session_state.get("empresa_logada", "")
    if not empresa:
        return arquivo

    pasta_base = os.path.join("dados_empresas", slug_empresa(empresa))
    os.makedirs(pasta_base, exist_ok=True)
    return os.path.join(pasta_base, arquivo)

def autenticar_empresa(usuario, senha):
    df = carregar_csv_bruto(ARQ_ASSINATURAS, COLUNAS_ASSINATURAS)
    if df.empty:
        return False, "Nenhuma empresa cadastrada.", None

    usuario = str(usuario).strip()
    senha = str(senha).strip()

    match = df[
        (df["Usuario"].astype(str).str.strip() == usuario) &
        (df["Senha"].astype(str).str.strip() == senha)
    ]

    if match.empty:
        return False, "Usuário ou senha inválidos.", None

    registro = match.iloc[0]

    if str(registro["Ativo"]).strip().lower() not in ["sim", "true", "1", "ativo"]:
        return False, "Acesso inativo. Entre em contato para renovação.", None

    try:
        validade = pd.to_datetime(registro["Validade"]).date()
    except Exception:
        return False, "Data de validade inválida no cadastro.", None

    if datetime.today().date() > validade:
        return False, f"Assinatura vencida em {validade.strftime('%d/%m/%Y')}.", None

    return True, "Acesso liberado.", registro.to_dict()

def verificar_assinatura_em_sessao():
    if not st.session_state.get("usuario_logado", False):
        return False

    validade_txt = st.session_state.get("validade_assinatura", "")
    try:
        validade = pd.to_datetime(validade_txt).date()
    except Exception:
        st.error("Validade da assinatura inválida.")
        st.stop()

    if datetime.today().date() > validade:
        st.error("Assinatura vencida. Entre em contato para renovação.")
        st.session_state.usuario_logado = False
        st.stop()

    return True

def tela_login():
    st.markdown('<div class="login-card">', unsafe_allow_html=True)
    st.markdown('<div class="login-title">Acesso da Empresa</div>', unsafe_allow_html=True)
    st.markdown('<div class="login-subtitle">Entre com usuário e senha para utilizar o sistema por assinatura.</div>', unsafe_allow_html=True)

    with st.form("form_login_empresa"):
        usuario = st.text_input("Usuário")
        senha = st.text_input("Senha", type="password")
        btn_login = st.form_submit_button("Entrar")

        if btn_login:
            ok, msg, dados = autenticar_empresa(usuario, senha)
            if ok:
                st.session_state.usuario_logado = True
                st.session_state.empresa_logada = str(dados["Empresa"])
                st.session_state.nome_empresa = str(dados["Empresa"])
                st.session_state.usuario_atual = str(dados["Usuario"])
                st.session_state.validade_assinatura = str(dados["Validade"])
                st.session_state.is_admin_master = str(dados.get("Admin Master", "")).strip().lower() in ["sim", "true", "1"]
                st.success("Login realizado com sucesso.")
                st.rerun()
            else:
                st.error(msg)

    st.markdown("</div>", unsafe_allow_html=True)
    st.stop()

def tela_admin_assinaturas():
    st.markdown("### Administração de Assinaturas")

    df_ass = carregar_csv_bruto(ARQ_ASSINATURAS, COLUNAS_ASSINATURAS)
    if not df_ass.empty:
        df_exib = df_ass.copy()
        df_exib["Validade"] = pd.to_datetime(df_exib["Validade"], errors="coerce").dt.strftime("%d/%m/%Y")
        st.dataframe(df_exib, width="stretch", hide_index=True)

    abas_admin = st.tabs(["Cadastrar empresa", "Renovar/editar empresa"])

    with abas_admin[0]:
        with st.form("form_nova_empresa"):
            a1, a2 = st.columns(2)
            with a1:
                empresa = st.text_input("Nome da empresa")
                usuario = st.text_input("Usuário da empresa")
                senha = st.text_input("Senha inicial")
            with a2:
                validade = st.date_input("Validade da assinatura", value=datetime.today().date() + timedelta(days=30))
                ativo = st.selectbox("Status", ["Sim", "Não"])

            btn_cadastrar = st.form_submit_button("Cadastrar empresa")

            if btn_cadastrar:
                if not empresa.strip() or not usuario.strip() or not senha.strip():
                    st.error("Preencha empresa, usuário e senha.")
                else:
                    df_ass = carregar_csv_bruto(ARQ_ASSINATURAS, COLUNAS_ASSINATURAS)
                    if (df_ass["Usuario"].astype(str).str.strip() == usuario.strip()).any():
                        st.error("Já existe uma empresa com esse usuário.")
                    else:
                        novo = pd.DataFrame([{
                            "Empresa": empresa.strip(),
                            "Usuario": usuario.strip(),
                            "Senha": senha.strip(),
                            "Validade": pd.to_datetime(validade).strftime("%Y-%m-%d"),
                            "Ativo": ativo,
                            "Admin Master": "Não"
                        }])
                        df_ass = pd.concat([df_ass, novo], ignore_index=True)
                        salvar_csv_bruto(df_ass, ARQ_ASSINATURAS)
                        st.success("Empresa cadastrada com sucesso.")
                        st.rerun()

    with abas_admin[1]:
        df_ass = carregar_csv_bruto(ARQ_ASSINATURAS, COLUNAS_ASSINATURAS)
        df_empresas = df_ass[df_ass["Admin Master"].astype(str).str.lower() != "sim"].copy()

        if df_empresas.empty:
            st.info("Não há empresas cadastradas.")
        else:
            opcoes = df_empresas.apply(lambda x: f'{x["Empresa"]} - {x["Usuario"]}', axis=1).tolist()
            empresa_sel = st.selectbox("Selecione a empresa", [""] + opcoes)

            if empresa_sel:
                usuario_sel = empresa_sel.split(" - ")[-1]
                linha = df_ass[df_ass["Usuario"].astype(str) == str(usuario_sel)].iloc[0]

                with st.form("form_editar_empresa"):
                    b1, b2 = st.columns(2)
                    with b1:
                        nova_empresa = st.text_input("Empresa", value=str(linha["Empresa"]))
                        novo_usuario = st.text_input("Usuário", value=str(linha["Usuario"]))
                        nova_senha = st.text_input("Senha", value=str(linha["Senha"]))
                    with b2:
                        nova_validade = st.date_input(
                            "Validade",
                            value=pd.to_datetime(linha["Validade"], errors="coerce").date()
                            if pd.notna(pd.to_datetime(linha["Validade"], errors="coerce"))
                            else datetime.today().date() + timedelta(days=30)
                        )
                        novo_ativo = st.selectbox(
                            "Status",
                            ["Sim", "Não"],
                            index=0 if str(linha["Ativo"]).strip().lower() in ["sim", "true", "1", "ativo"] else 1
                        )

                    btn_editar = st.form_submit_button("Salvar empresa")

                    if btn_editar:
                        idx = df_ass.index[df_ass["Usuario"].astype(str) == str(usuario_sel)][0]
                        df_ass.at[idx, "Empresa"] = nova_empresa.strip()
                        df_ass.at[idx, "Usuario"] = novo_usuario.strip()
                        df_ass.at[idx, "Senha"] = nova_senha.strip()
                        df_ass.at[idx, "Validade"] = pd.to_datetime(nova_validade).strftime("%Y-%m-%d")
                        df_ass.at[idx, "Ativo"] = novo_ativo
                        salvar_csv_bruto(df_ass, ARQ_ASSINATURAS)
                        st.success("Empresa atualizada com sucesso.")
                        st.rerun()

def gerar_html_oms_selecionadas(df_oms, nome_empresa):
    linhas = []
    for _, row in df_oms.iterrows():
        linhas.append(f"""
        <div class="om-card">
            <h2>OM {row['N° OM']}</h2>
            <p><b>Data:</b> {formatar_data_br(row['Data'])}</p>
            <p><b>Código:</b> {row['Código']}</p>
            <p><b>Equipamento:</b> {row['Equipamento']}</p>
            <p><b>Área:</b> {row['Área']}</p>
            <p><b>Tipo de Manutenção:</b> {row['Tipo Manutenção']}</p>
            <p><b>Solicitante:</b> {row['Solicitante']}</p>
            <p><b>Aprovador:</b> {row['Aprovador']}</p>
            <p><b>Colaborador 1:</b> {row['Colaborador 1']} | <b>Horas 1:</b> {decimal_para_hhmm(row['Horas 1'])}</p>
            <p><b>Colaborador 2:</b> {row['Colaborador 2']} | <b>Horas 2:</b> {decimal_para_hhmm(row['Horas 2'])}</p>
            <p><b>Colaborador 3:</b> {row['Colaborador 3']} | <b>Horas 3:</b> {decimal_para_hhmm(row['Horas 3'])}</p>
            <p><b>Total Horas:</b> {decimal_para_hhmm(row['Total Horas'])}</p>
            <p><b>Custo Manutenção:</b> {formatar_moeda(row['Custo Manutenção'])}</p>
            <p><b>Descrição do Problema:</b><br>{row['Descrição do Problema']}</p>
            <p><b>Serviço Executado:</b><br>{row['Serviço Executado']}</p>
        </div>
        """)

    return f"""
    <html>
    <head>
        <meta charset="utf-8">
        <title>Impressão de OMs</title>
        <style>
            body {{
                font-family: Arial, sans-serif;
                margin: 24px;
                color: #0f172a;
            }}
            .cabecalho {{
                text-align: center;
                margin-bottom: 24px;
            }}
            .om-card {{
                border: 1px solid #cbd5e1;
                border-radius: 12px;
                padding: 16px;
                margin-bottom: 18px;
                page-break-inside: avoid;
            }}
            h1, h2 {{
                margin-bottom: 8px;
            }}
            p {{
                margin: 6px 0;
            }}
        </style>
    </head>
    <body>
        <div class="cabecalho">
            <h1>Ordens de Manutenção Selecionadas</h1>
            <p><b>Empresa:</b> {nome_empresa}</p>
            <p><b>Gerado em:</b> {datetime.now().strftime("%d/%m/%Y %H:%M")}</p>
        </div>
        {"".join(linhas)}
    </body>
    </html>
    """

inicializar_assinaturas()

if not st.session_state.get("usuario_logado", False):
    tela_login()

verificar_assinatura_em_sessao()

# =========================
# CABEÇALHO
# =========================
col_logo, col_titulo = st.columns([1, 6])

with col_logo:
    if st.session_state.logo_empresa_bytes:
        st.image(st.session_state.logo_empresa_bytes, width=110)

with col_titulo:
    st.markdown('<div class="main-title">GESTÃO DE MANUTENÇÃO INDUSTRIAL</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="company-title">{st.session_state.nome_empresa}</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-title">Sistema de cadastro, controle, indicadores e histórico de ordens de manutenção</div>', unsafe_allow_html=True)

# =========================
# ARQUIVOS E COLUNAS
# =========================
ARQ_EQUIP = "equipamentos.csv"
ARQ_COLAB = "colaboradores.csv"
ARQ_OM = "ordens_manutencao.csv"

COLUNAS_EQUIP = ["Código", "Equipamento", "Marca", "Modelo", "Setor", "Área"]
COLUNAS_COLAB = ["Nome", "Função"]
COLUNAS_OM = [
    "N° OM",
    "Data",
    "Código",
    "Equipamento",
    "Marca",
    "Modelo",
    "Setor",
    "Área",
    "Tipo Manutenção",
    "Solicitante",
    "Aprovador",
    "Colaborador 1",
    "Horas 1",
    "Colaborador 2",
    "Horas 2",
    "Colaborador 3",
    "Horas 3",
    "Total Horas",
    "Descrição do Problema",
    "Serviço Executado",
    "Custo Manutenção"
]

TIPOS_MANUT = [
    "Preventiva",
    "Corretiva Programada",
    "Corretiva Não Programada",
    "Inspeção",
    "Melhoria"
]

MESES_PT = {
    1: "Janeiro", 2: "Fevereiro", 3: "Março", 4: "Abril",
    5: "Maio", 6: "Junho", 7: "Julho", 8: "Agosto",
    9: "Setembro", 10: "Outubro", 11: "Novembro", 12: "Dezembro"
}

# =========================
# FUNÇÕES GERAIS
# =========================
def carregar_csv(arquivo, colunas):
    arquivo = obter_caminho_arquivo(arquivo)
    if os.path.exists(arquivo):
        try:
            df = pd.read_csv(arquivo, encoding="utf-8")
            for col in colunas:
                if col not in df.columns:
                    df[col] = ""
            return df[colunas]
        except Exception:
            return pd.DataFrame(columns=colunas)
    return pd.DataFrame(columns=colunas)


def salvar_csv(df, arquivo):
    arquivo = obter_caminho_arquivo(arquivo)
    pasta = os.path.dirname(arquivo)
    if pasta:
        os.makedirs(pasta, exist_ok=True)
    df.to_csv(arquivo, index=False, encoding="utf-8")


def converter_numero(valor, padrao=0.0):
    try:
        if valor == "" or pd.isna(valor):
            return padrao
        if isinstance(valor, str):
            valor = valor.replace("R$", "").replace(".", "").replace(",", ".").strip()
        return float(valor)
    except Exception:
        return padrao


def validar_hora_hhmm(texto):
    try:
        partes = str(texto).strip().split(":")
        if len(partes) != 2:
            return False
        horas = int(partes[0])
        minutos = int(partes[1])
        if horas < 0 or minutos < 0 or minutos > 59:
            return False
        return True
    except Exception:
        return False


def hhmm_para_horas_decimal(texto):
    if texto is None or str(texto).strip() == "":
        return 0.0
    texto = str(texto).strip()
    if ":" in texto:
        if not validar_hora_hhmm(texto):
            raise ValueError("Formato de hora inválido. Use HH:MM.")
        horas, minutos = texto.split(":")
        return int(horas) + int(minutos) / 60.0
    return float(texto)


def decimal_para_hhmm(valor):
    try:
        total_min = int(round(float(valor) * 60))
        horas = total_min // 60
        minutos = total_min % 60
        return f"{horas:02d}:{minutos:02d}"
    except Exception:
        return "00:00"


def formatar_moeda(valor):
    try:
        return f"R$ {float(valor):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    except Exception:
        return "R$ 0,00"


def formatar_data_br(data_str):
    try:
        return pd.to_datetime(data_str).strftime("%d/%m/%Y")
    except Exception:
        return str(data_str)


def garantir_tipos():
    df_om = carregar_csv(ARQ_OM, COLUNAS_OM)
    if not df_om.empty:
        for col in ["Horas 1", "Horas 2", "Horas 3"]:
            df_om[col] = df_om[col].apply(lambda x: hhmm_para_horas_decimal(x) if str(x).strip() != "" else 0.0)

        df_om["Total Horas"] = df_om.apply(
            lambda x: converter_numero(x["Horas 1"]) + converter_numero(x["Horas 2"]) + converter_numero(x["Horas 3"]),
            axis=1
        )
        df_om["Custo Manutenção"] = pd.to_numeric(df_om["Custo Manutenção"], errors="coerce").fillna(0.0)
        salvar_csv(df_om, ARQ_OM)


def gerar_numero_om(data_om):
    ano = pd.to_datetime(data_om).year
    df_om = carregar_csv(ARQ_OM, COLUNAS_OM)

    if df_om.empty:
        return f"0001-{ano}"

    sequenciais = []
    for valor in df_om["N° OM"].astype(str):
        if "-" in valor:
            partes = valor.split("-")
            if len(partes) == 2:
                seq, ano_reg = partes
                if str(ano_reg).strip() == str(ano):
                    try:
                        sequenciais.append(int(seq))
                    except Exception:
                        pass

    proximo = max(sequenciais) + 1 if sequenciais else 1
    return f"{proximo:04d}-{ano}"


def equipamento_tem_om(codigo):
    df_om = carregar_csv(ARQ_OM, COLUNAS_OM)
    if df_om.empty:
        return False
    return (df_om["Código"].astype(str) == str(codigo)).any()


def colaborador_tem_om(nome):
    df_om = carregar_csv(ARQ_OM, COLUNAS_OM)
    if df_om.empty:
        return False

    nome = str(nome).strip()
    return (
        (df_om["Colaborador 1"].astype(str).str.strip() == nome).any()
        or (df_om["Colaborador 2"].astype(str).str.strip() == nome).any()
        or (df_om["Colaborador 3"].astype(str).str.strip() == nome).any()
    )


def preparar_df_om():
    df_om = carregar_csv(ARQ_OM, COLUNAS_OM)

    if df_om.empty:
        return df_om

    df_om["Data"] = pd.to_datetime(df_om["Data"], errors="coerce")

    for col in ["Horas 1", "Horas 2", "Horas 3"]:
        df_om[col] = df_om[col].apply(lambda x: hhmm_para_horas_decimal(x) if str(x).strip() != "" else 0.0)

    df_om["Total Horas"] = df_om.apply(
        lambda x: converter_numero(x["Horas 1"]) + converter_numero(x["Horas 2"]) + converter_numero(x["Horas 3"]),
        axis=1
    )
    df_om["Custo Manutenção"] = pd.to_numeric(df_om["Custo Manutenção"], errors="coerce").fillna(0.0)

    df_om["Ano"] = df_om["Data"].dt.year
    df_om["Mês"] = df_om["Data"].dt.month
    df_om["Nome do Mês"] = df_om["Mês"].map(MESES_PT)
    df_om["Semana"] = df_om["Data"].dt.isocalendar().week.astype("Int64")

    return df_om


def aplicar_layout_fig(fig):
    fig.update_layout(
        plot_bgcolor="white",
        paper_bgcolor="white",
        font=dict(color="#0f172a"),
        title_font=dict(size=20, color="#0f172a"),
        legend_title_text="",
        margin=dict(l=30, r=20, t=60, b=40)
    )
    fig.update_xaxes(showgrid=False)
    fig.update_yaxes(gridcolor="#dbe4f0")
    return fig


def gerar_html_dashboard(nome_empresa, logo_bytes, filtro, fig_qtd, fig_horas, fig_percentual, rank_om, rank_custo, mttr):
    logo_html = ""
    if logo_bytes:
        logo_b64 = base64.b64encode(logo_bytes).decode()
        logo_html = f'<img src="data:image/png;base64,{logo_b64}" style="max-height:90px; margin-bottom:10px;">'

    fig_qtd_html = pio.to_html(fig_qtd, include_plotlyjs="cdn", full_html=False) if fig_qtd else ""
    fig_horas_html = pio.to_html(fig_horas, include_plotlyjs=False, full_html=False) if fig_horas else ""
    fig_percentual_html = pio.to_html(fig_percentual, include_plotlyjs=False, full_html=False) if fig_percentual else ""

    html = f"""
    <html>
    <head>
        <meta charset="utf-8">
        <title>Dashboard de Manutenção</title>
        <style>
            body {{
                font-family: Arial, sans-serif;
                margin: 24px;
                color: #0f172a;
                background: #f8fbff;
            }}
            .header {{
                text-align: center;
                margin-bottom: 24px;
            }}
            .title {{
                font-size: 28px;
                font-weight: bold;
            }}
            .subtitle {{
                font-size: 18px;
                color: #1d4ed8;
                margin-top: 4px;
            }}
            .grid {{
                display: grid;
                grid-template-columns: repeat(3, 1fr);
                gap: 16px;
                margin-bottom: 24px;
            }}
            .card {{
                border: 1px solid #dbe4f0;
                border-radius: 12px;
                padding: 16px;
                background: white;
                box-shadow: 0 2px 10px rgba(15, 23, 42, 0.06);
            }}
            .label {{
                font-size: 14px;
                color: #475569;
            }}
            .value {{
                font-size: 24px;
                font-weight: bold;
                margin-top: 8px;
            }}
            h2 {{
                margin-top: 30px;
                margin-bottom: 10px;
                color: #0f172a;
            }}
            table {{
                width: 100%;
                border-collapse: collapse;
                margin-bottom: 24px;
                background: white;
            }}
            th, td {{
                border: 1px solid #cbd5e1;
                padding: 8px;
                text-align: left;
            }}
            th {{
                background: #e2e8f0;
            }}
        </style>
    </head>
    <body>
        <div class="header">
            {logo_html}
            <div class="title">GESTÃO DE MANUTENÇÃO INDUSTRIAL</div>
            <div class="subtitle">{nome_empresa}</div>
        </div>

        <div class="grid">
            <div class="card">
                <div class="label">Total de OMs</div>
                <div class="value">{len(filtro)}</div>
            </div>
            <div class="card">
                <div class="label">Horas Totais</div>
                <div class="value">{decimal_para_hhmm(filtro["Total Horas"].sum())}</div>
            </div>
            <div class="card">
                <div class="label">Custo Total</div>
                <div class="value">{formatar_moeda(filtro["Custo Manutenção"].sum())}</div>
            </div>
        </div>

        <h2>Quantidade de OMs por Tipo de Manutenção</h2>
        {fig_qtd_html}

        <h2>Horas Totais por Tipo de Manutenção</h2>
        {fig_horas_html}

        <h2>Percentual por Tipo de Manutenção</h2>
        {fig_percentual_html}

        <h2>Top 5 Equipamentos por Quantidade de OMs</h2>
        {rank_om.to_html(index=False)}

        <h2>Top 5 Equipamentos por Custo de Manutenção</h2>
        {rank_custo.to_html(index=False)}

        <h2>MTTR - 5 Equipamentos que Mais Necessitam Atenção</h2>
        {mttr.to_html(index=False)}
    </body>
    </html>
    """
    return html

# =========================
# EQUIPAMENTOS
# =========================
def adicionar_equipamento(dados):
    df = carregar_csv(ARQ_EQUIP, COLUNAS_EQUIP)
    if (df["Código"].astype(str) == str(dados["Código"])).any():
        return False, "Já existe um equipamento com esse código."
    df = pd.concat([df, pd.DataFrame([dados])], ignore_index=True)
    salvar_csv(df, ARQ_EQUIP)
    return True, "Equipamento cadastrado com sucesso."


def editar_equipamento(codigo_original, novos_dados):
    df = carregar_csv(ARQ_EQUIP, COLUNAS_EQUIP)

    if str(codigo_original) != str(novos_dados["Código"]):
        if (df["Código"].astype(str) == str(novos_dados["Código"])).any():
            return False, "Já existe outro equipamento com esse código."

    idx = df.index[df["Código"].astype(str) == str(codigo_original)]
    if len(idx) == 0:
        return False, "Equipamento não encontrado."

    idx = idx[0]
    codigo_antigo = str(df.at[idx, "Código"])

    for col in COLUNAS_EQUIP:
        df.at[idx, col] = novos_dados[col]

    salvar_csv(df, ARQ_EQUIP)

    df_om = carregar_csv(ARQ_OM, COLUNAS_OM)
    if not df_om.empty:
        mask = df_om["Código"].astype(str) == codigo_antigo
        if mask.any():
            df_om.loc[mask, "Código"] = novos_dados["Código"]
            df_om.loc[mask, "Equipamento"] = novos_dados["Equipamento"]
            df_om.loc[mask, "Marca"] = novos_dados["Marca"]
            df_om.loc[mask, "Modelo"] = novos_dados["Modelo"]
            df_om.loc[mask, "Setor"] = novos_dados["Setor"]
            df_om.loc[mask, "Área"] = novos_dados["Área"]
            salvar_csv(df_om, ARQ_OM)

    return True, "Equipamento atualizado com sucesso."


def excluir_equipamento(codigo):
    if equipamento_tem_om(codigo):
        return False, "Este equipamento possui OM vinculada e não pode ser excluído."

    df = carregar_csv(ARQ_EQUIP, COLUNAS_EQUIP)
    df = df[df["Código"].astype(str) != str(codigo)]
    salvar_csv(df, ARQ_EQUIP)
    return True, "Equipamento excluído com sucesso."

# =========================
# COLABORADORES
# =========================
def adicionar_colaborador(dados):
    df = carregar_csv(ARQ_COLAB, COLUNAS_COLAB)

    duplicado = (
        df["Nome"].astype(str).str.strip().str.lower() == str(dados["Nome"]).strip().lower()
    ).any()

    if duplicado:
        return False, "Já existe um colaborador com esse nome."

    df = pd.concat([df, pd.DataFrame([dados])], ignore_index=True)
    salvar_csv(df, ARQ_COLAB)
    return True, "Colaborador cadastrado com sucesso."


def editar_colaborador(nome_original, novos_dados):
    df = carregar_csv(ARQ_COLAB, COLUNAS_COLAB)

    idx = df.index[df["Nome"].astype(str) == str(nome_original)]

    if len(idx) == 0:
        return False, "Colaborador não encontrado."

    idx = idx[0]
    nome_antigo = str(df.at[idx, "Nome"])

    for col in COLUNAS_COLAB:
        df.at[idx, col] = novos_dados[col]

    salvar_csv(df, ARQ_COLAB)

    df_om = carregar_csv(ARQ_OM, COLUNAS_OM)
    if not df_om.empty:
        for col in ["Colaborador 1", "Colaborador 2", "Colaborador 3"]:
            mask = df_om[col].astype(str) == nome_antigo
            if mask.any():
                df_om.loc[mask, col] = novos_dados["Nome"]
        salvar_csv(df_om, ARQ_OM)

    return True, "Colaborador atualizado com sucesso."


def excluir_colaborador(nome):
    if colaborador_tem_om(nome):
        return False, "Este colaborador possui OM vinculada e não pode ser excluído."

    df = carregar_csv(ARQ_COLAB, COLUNAS_COLAB)
    df = df[df["Nome"].astype(str) != str(nome)]
    salvar_csv(df, ARQ_COLAB)
    return True, "Colaborador excluído com sucesso."

# =========================
# OM
# =========================
def adicionar_om(dados):
    df = carregar_csv(ARQ_OM, COLUNAS_OM)
    df = pd.concat([df, pd.DataFrame([dados])], ignore_index=True)
    salvar_csv(df, ARQ_OM)
    return True, "OM cadastrada com sucesso."


def editar_om(numero_om, novos_dados):
    df = carregar_csv(ARQ_OM, COLUNAS_OM)
    idx = df.index[df["N° OM"].astype(str) == str(numero_om)]

    if len(idx) == 0:
        return False, "OM não encontrada."

    idx = idx[0]

    for col in COLUNAS_OM:
        df.at[idx, col] = novos_dados[col]

    salvar_csv(df, ARQ_OM)
    return True, "OM atualizada com sucesso."


def excluir_om(numero_om):
    df = carregar_csv(ARQ_OM, COLUNAS_OM)
    df = df[df["N° OM"].astype(str) != str(numero_om)]
    salvar_csv(df, ARQ_OM)
    return True, "OM excluída com sucesso."

# =========================
# INICIALIZAÇÃO
# =========================
garantir_tipos()

# =========================
# SIDEBAR EMPRESA
# =========================
st.sidebar.markdown("## Empresa")
nome_empresa_input = st.sidebar.text_input("Nome da empresa", value=st.session_state.nome_empresa)
if nome_empresa_input.strip():
    st.session_state.nome_empresa = nome_empresa_input.strip()

# LOGO
if st.session_state.logo_empresa_bytes:
    st.sidebar.image(st.session_state.logo_empresa_bytes, width="stretch")
    if st.sidebar.button("Trocar logo"):
        st.session_state.logo_empresa_bytes = None
        st.rerun()
else:
    logo_empresa = st.sidebar.file_uploader(
        "Imagem da empresa",
        type=["png", "jpg", "jpeg"]
    )

    if logo_empresa is not None:
        st.session_state.logo_empresa_bytes = logo_empresa.read()
        st.rerun()

st.sidebar.markdown(f"**Usuário:** {st.session_state.usuario_atual}")
st.sidebar.markdown(f"**Validade:** {formatar_data_br(st.session_state.validade_assinatura)}")

if st.session_state.is_admin_master:
    st.sidebar.success("Acesso administrador master")

if st.sidebar.button("Sair do sistema"):
    st.session_state.usuario_logado = False
    st.session_state.empresa_logada = ""
    st.session_state.usuario_atual = ""
    st.session_state.validade_assinatura = ""
    st.session_state.is_admin_master = False
    st.rerun()

st.sidebar.markdown("---")

opcoes_menu = ["Dashboard", "Equipamentos", "Colaboradores", "Abrir OM", "Histórico", "Horas por Colaborador"]
if st.session_state.is_admin_master:
    opcoes_menu.append("Assinaturas")

menu = st.sidebar.radio(
    "Menu",
    opcoes_menu
)

# =========================
# ASSINATURAS
# =========================
if menu == "Assinaturas":
    st.subheader("Controle de Assinaturas")
    if st.session_state.is_admin_master:
        tela_admin_assinaturas()
    else:
        st.error("Acesso permitido apenas para administrador master.")

# =========================
# DASHBOARD
# =========================
elif menu == "Dashboard":

    st.subheader("Painel de Indicadores")

    df_om = preparar_df_om()

    if df_om.empty:
        st.info("Não há dados de OM para exibir no dashboard.")
    else:
        c1, c2, c3 = st.columns(3)

        anos = sorted([int(a) for a in df_om["Ano"].dropna().unique()])
        meses = sorted([int(m) for m in df_om["Mês"].dropna().unique()])
        areas = sorted(df_om["Área"].dropna().astype(str).unique().tolist())

        with c1:
            ano_sel = st.selectbox("Filtrar por ano", ["Todos"] + anos)

        with c2:
            opcoes_meses = ["Todos"] + [MESES_PT[m] for m in meses]
            mes_nome_sel = st.selectbox("Filtrar por mês", opcoes_meses)

        with c3:
            area_sel = st.selectbox("Filtrar por área", ["Todas"] + areas)

        filtro = df_om.copy()

        if ano_sel != "Todos":
            filtro = filtro[filtro["Ano"] == ano_sel]

        if mes_nome_sel != "Todos":
            numero_mes = [k for k, v in MESES_PT.items() if v == mes_nome_sel][0]
            filtro = filtro[filtro["Mês"] == numero_mes]

        if area_sel != "Todas":
            filtro = filtro[filtro["Área"].astype(str) == str(area_sel)]

        k1, k2, k3 = st.columns(3)

        with k1:
            st.metric("Total de OMs", len(filtro))

        with k2:
            st.metric("Horas Totais", decimal_para_hhmm(filtro["Total Horas"].sum()))

        with k3:
            st.metric("Custo Total", formatar_moeda(filtro["Custo Manutenção"].sum()))

        g1, g2 = st.columns(2)

        fig1 = None
        fig2 = None
        fig_percentual = None

        with g1:
            graf1 = filtro.groupby("Tipo Manutenção").size().reset_index(name="Quantidade")
            if not graf1.empty:
                fig1 = px.bar(
                    graf1,
                    x="Tipo Manutenção",
                    y="Quantidade",
                    title="Quantidade de OMs por Tipo de Manutenção",
                    text_auto=True,
                    color="Tipo Manutenção",
                    color_discrete_sequence=PALETA_GRAFICOS
                )
                fig1 = aplicar_layout_fig(fig1)
                st.plotly_chart(fig1, width="stretch")

        with g2:
            graf2 = filtro.groupby("Tipo Manutenção", as_index=False)["Total Horas"].sum()
            if not graf2.empty:
                graf2["Horas Texto"] = graf2["Total Horas"].apply(decimal_para_hhmm)
                fig2 = px.bar(
                    graf2,
                    x="Tipo Manutenção",
                    y="Total Horas",
                    title="Horas Totais por Tipo de Manutenção",
                    text="Horas Texto",
                    color="Tipo Manutenção",
                    color_discrete_sequence=PALETA_GRAFICOS
                )
                fig2 = aplicar_layout_fig(fig2)
                st.plotly_chart(fig2, width="stretch")

        st.markdown("### Percentual por Tipo de Manutenção")
        percentual = filtro.groupby("Tipo Manutenção").size().reset_index(name="Quantidade")
        if not percentual.empty:
            percentual["Percentual"] = (percentual["Quantidade"] / percentual["Quantidade"].sum()) * 100
            percentual["Texto"] = percentual["Percentual"].map(lambda x: f"{x:.1f}%")

            fig_percentual = px.pie(
                percentual,
                names="Tipo Manutenção",
                values="Quantidade",
                title="Distribuição Percentual por Tipo de Manutenção",
                color_discrete_sequence=PALETA_GRAFICOS
            )
            fig_percentual.update_traces(textinfo="percent+label")
            fig_percentual = aplicar_layout_fig(fig_percentual)
            st.plotly_chart(fig_percentual, width="stretch")

        r1, r2 = st.columns(2)

        with r1:
            st.markdown("### Top 5 Equipamentos por Quantidade de OMs")
            rank_om = (
                filtro.groupby(["Código", "Equipamento"])
                .size()
                .reset_index(name="Quantidade de OMs")
                .sort_values(by="Quantidade de OMs", ascending=False)
                .head(5)
            )
            st.dataframe(rank_om, width="stretch", hide_index=True)

        with r2:
            st.markdown("### Top 5 Equipamentos por Custo de Manutenção")
            rank_custo = (
                filtro.groupby(["Código", "Equipamento"], as_index=False)["Custo Manutenção"]
                .sum()
                .sort_values(by="Custo Manutenção", ascending=False)
                .head(5)
            )
            rank_custo_exib = rank_custo.copy()
            rank_custo_exib["Custo Manutenção"] = rank_custo_exib["Custo Manutenção"].map(formatar_moeda)
            st.dataframe(rank_custo_exib, width="stretch", hide_index=True)

        st.markdown("### Indicadores de Confiabilidade")

        top_atencao = (
            filtro.groupby(["Código", "Equipamento"])
            .size()
            .reset_index(name="Quantidade de OMs")
            .sort_values(by="Quantidade de OMs", ascending=False)
            .head(5)
        )

        equipamentos_atencao = top_atencao["Código"].astype(str).tolist()
        filtro_atencao = filtro[filtro["Código"].astype(str).isin(equipamentos_atencao)].copy()

        mttr = pd.DataFrame()
        mt1 = st.container()

        with mt1:
            mttr = (
                filtro_atencao.groupby(["Código", "Equipamento"], as_index=False)["Total Horas"]
                .mean()
                .rename(columns={"Total Horas": "MTTR (horas)"})
                .sort_values(by="MTTR (horas)", ascending=False)
                .head(5)
            )

            if not mttr.empty:
                mttr["MTTR Texto"] = mttr["MTTR (horas)"].apply(decimal_para_hhmm)
                fig_mttr = px.bar(
                    mttr,
                    x="Equipamento",
                    y="MTTR (horas)",
                    title="MTTR - 5 Equipamentos que Mais Necessitam Atenção",
                    text="MTTR Texto",
                    color="Equipamento",
                    color_discrete_sequence=PALETA_GRAFICOS
                )
                fig_mttr = aplicar_layout_fig(fig_mttr)
                st.plotly_chart(fig_mttr, width="stretch")

                mttr_exib = mttr[["Código", "Equipamento", "MTTR Texto"]].rename(columns={"MTTR Texto": "MTTR"})
                st.dataframe(mttr_exib, width="stretch", hide_index=True)
            else:
                st.info("Sem dados suficientes para MTTR.")

        st.markdown("### Impressão do Dashboard")
        html_dashboard = gerar_html_dashboard(
            st.session_state.nome_empresa,
            st.session_state.logo_empresa_bytes,
            filtro,
            fig1,
            fig2,
            fig_percentual,
            rank_om if 'rank_om' in locals() else pd.DataFrame(),
            rank_custo_exib if 'rank_custo_exib' in locals() else pd.DataFrame(),
            mttr_exib if 'mttr_exib' in locals() else pd.DataFrame()
        )

        st.download_button(
            label="Baixar dashboard para impressão (HTML)",
            data=html_dashboard,
            file_name="dashboard_manutencao.html",
            mime="text/html"
        )

# =========================
# EQUIPAMENTOS
# =========================
elif menu == "Equipamentos":
    st.subheader("Cadastro de Equipamentos")
    abas = st.tabs(["Cadastrar", "Editar", "Excluir", "Listagem"])

    with abas[0]:
        st.info("Os campos de preenchimento foram destacados para facilitar a visualização.")
        with st.form("form_equip"):
            c1, c2, c3 = st.columns(3)

            with c1:
                codigo = st.text_input("Código")
                equipamento = st.text_input("Equipamento")

            with c2:
                marca = st.text_input("Marca")
                modelo = st.text_input("Modelo")

            with c3:
                setor = st.text_input("Setor")
                area = st.text_input("Área")

            btn = st.form_submit_button("Salvar Equipamento")

            if btn:
                if not codigo.strip() or not equipamento.strip():
                    st.error("Preencha Código e Equipamento.")
                else:
                    ok, msg = adicionar_equipamento({
                        "Código": codigo.strip(),
                        "Equipamento": equipamento.strip(),
                        "Marca": marca.strip(),
                        "Modelo": modelo.strip(),
                        "Setor": setor.strip(),
                        "Área": area.strip()
                    })
                    if ok:
                        st.success(msg)
                        st.rerun()
                    else:
                        st.error(msg)

    with abas[1]:
        df_equip = carregar_csv(ARQ_EQUIP, COLUNAS_EQUIP)

        if df_equip.empty:
            st.info("Não há equipamentos cadastrados.")
        else:
            opcoes = df_equip.apply(
                lambda x: f'{x["Código"]} - {x["Equipamento"]} - {x["Área"]}',
                axis=1
            ).tolist()

            selecionado = st.selectbox("Selecione um equipamento para editar", [""] + opcoes)

            if selecionado:
                codigo_sel = selecionado.split(" - ")[0]
                linha = df_equip[df_equip["Código"].astype(str) == str(codigo_sel)].iloc[0]

                with st.form("form_edit_equip"):
                    c1, c2, c3 = st.columns(3)

                    with c1:
                        novo_codigo = st.text_input("Código", value=str(linha["Código"]))
                        novo_nome = st.text_input("Equipamento", value=str(linha["Equipamento"]))

                    with c2:
                        nova_marca = st.text_input("Marca", value=str(linha["Marca"]))
                        novo_modelo = st.text_input("Modelo", value=str(linha["Modelo"]))

                    with c3:
                        novo_setor = st.text_input("Setor", value=str(linha["Setor"]))
                        nova_area = st.text_input("Área", value=str(linha["Área"]))

                    btn = st.form_submit_button("Salvar Alterações")

                    if btn:
                        ok, msg = editar_equipamento(codigo_sel, {
                            "Código": novo_codigo.strip(),
                            "Equipamento": novo_nome.strip(),
                            "Marca": nova_marca.strip(),
                            "Modelo": novo_modelo.strip(),
                            "Setor": novo_setor.strip(),
                            "Área": nova_area.strip()
                        })
                        if ok:
                            st.success(msg)
                            st.rerun()
                        else:
                            st.error(msg)

    with abas[2]:
        df_equip = carregar_csv(ARQ_EQUIP, COLUNAS_EQUIP)

        if df_equip.empty:
            st.info("Não há equipamentos cadastrados.")
        else:
            opcoes = df_equip.apply(
                lambda x: f'{x["Código"]} - {x["Equipamento"]} - {x["Área"]}',
                axis=1
            ).tolist()

            excluir_sel = st.selectbox("Selecione o equipamento para excluir", [""] + opcoes, key="exc_equip")

            if excluir_sel:
                codigo_exc = excluir_sel.split(" - ")[0]

                if equipamento_tem_om(codigo_exc):
                    st.warning("Este equipamento possui OM vinculada e não pode ser excluído.")

                confirmar = st.checkbox("Confirmo a exclusão do equipamento", key="conf_exc_equip")

                if st.button("Excluir Equipamento", key="btn_exc_equip"):
                    if not confirmar:
                        st.error("Marque a confirmação para excluir.")
                    else:
                        ok, msg = excluir_equipamento(codigo_exc)
                        if ok:
                            st.success(msg)
                            st.rerun()
                        else:
                            st.error(msg)

    with abas[3]:
        df_equip = carregar_csv(ARQ_EQUIP, COLUNAS_EQUIP)
        st.dataframe(df_equip, width="stretch", hide_index=True)

# =========================
# COLABORADORES
# =========================
elif menu == "Colaboradores":
    st.subheader("Cadastro de Colaboradores")
    abas = st.tabs(["Cadastrar", "Editar", "Excluir", "Listagem"])

    with abas[0]:
        st.info("Os campos de preenchimento foram destacados para facilitar a visualização.")
        with st.form("form_colab"):
            c1, c2 = st.columns(2)

            with c1:
                nome = st.text_input("Nome")

            with c2:
                funcao = st.text_input("Função")

            btn = st.form_submit_button("Salvar Colaborador")

            if btn:
                if not nome.strip():
                    st.error("Preencha o nome.")
                else:
                    ok, msg = adicionar_colaborador({
                        "Nome": nome.strip(),
                        "Função": funcao.strip()
                    })
                    if ok:
                        st.success(msg)
                        st.rerun()
                    else:
                        st.error(msg)

    with abas[1]:
        df_colab = carregar_csv(ARQ_COLAB, COLUNAS_COLAB)

        if df_colab.empty:
            st.info("Não há colaboradores cadastrados.")
        else:
            opcoes = df_colab.apply(
                lambda x: f'{x["Nome"]} - {x["Função"]}',
                axis=1
            ).tolist()

            selecionado = st.selectbox("Selecione um colaborador para editar", [""] + opcoes)

            if selecionado:
                nome_sel = selecionado.split(" - ")[0]
                linha = df_colab[df_colab["Nome"].astype(str) == str(nome_sel)].iloc[0]

                with st.form("form_edit_colab"):
                    c1, c2 = st.columns(2)

                    with c1:
                        novo_nome = st.text_input("Nome", value=str(linha["Nome"]))

                    with c2:
                        nova_funcao = st.text_input("Função", value=str(linha["Função"]))

                    btn = st.form_submit_button("Salvar Alterações")

                    if btn:
                        ok, msg = editar_colaborador(nome_sel, {
                            "Nome": novo_nome.strip(),
                            "Função": nova_funcao.strip()
                        })
                        if ok:
                            st.success(msg)
                            st.rerun()
                        else:
                            st.error(msg)

    with abas[2]:
        df_colab = carregar_csv(ARQ_COLAB, COLUNAS_COLAB)

        if df_colab.empty:
            st.info("Não há colaboradores cadastrados.")
        else:
            opcoes = df_colab.apply(
                lambda x: f'{x["Nome"]} - {x["Função"]}',
                axis=1
            ).tolist()

            excluir_sel = st.selectbox("Selecione o colaborador para excluir", [""] + opcoes, key="exc_colab")

            if excluir_sel:
                nome_exc = excluir_sel.split(" - ")[0]

                if colaborador_tem_om(nome_exc):
                    st.warning("Este colaborador possui OM vinculada e não pode ser excluído.")

                confirmar = st.checkbox("Confirmo a exclusão do colaborador", key="conf_exc_colab")

                if st.button("Excluir Colaborador", key="btn_exc_colab"):
                    if not confirmar:
                        st.error("Marque a confirmação para excluir.")
                    else:
                        ok, msg = excluir_colaborador(nome_exc)
                        if ok:
                            st.success(msg)
                            st.rerun()
                        else:
                            st.error(msg)

    with abas[3]:
        df_colab = carregar_csv(ARQ_COLAB, COLUNAS_COLAB)
        st.dataframe(df_colab, width="stretch", hide_index=True)

# =========================
# ABRIR OM
# =========================
elif menu == "Abrir OM":
    st.subheader("Abertura de Ordem de Manutenção")

    if st.session_state.mensagem_om_salva:
        st.success(st.session_state.mensagem_om_salva)
        st.session_state.mensagem_om_salva = ""

    df_equip = carregar_csv(ARQ_EQUIP, COLUNAS_EQUIP)
    df_colab = carregar_csv(ARQ_COLAB, COLUNAS_COLAB)

    if df_equip.empty:
        st.warning("Cadastre pelo menos um equipamento antes de abrir uma OM.")
    else:
        st.markdown('<div class="info-hora">Preencha as horas no formato HH:MM. Exemplo: 01:30 para 1 hora e 30 minutos.</div>', unsafe_allow_html=True)

        opcoes_equip = df_equip.apply(
            lambda x: f'{x["Código"]} - {x["Equipamento"]} - {x["Área"]}',
            axis=1
        ).tolist()

        opcoes_colab = [""] + sorted(df_colab["Nome"].astype(str).tolist())

        with st.form("form_om"):
            c1, c2, c3 = st.columns(3)

            with c1:
                data_om = st.date_input("Data", value=datetime.today())
                numero_preview = gerar_numero_om(data_om)
                st.text_input("N° OM", value=numero_preview, disabled=True)

            with c2:
                equip_sel = st.selectbox("Equipamento", opcoes_equip)
                tipo_manut = st.selectbox("Tipo de Manutenção", TIPOS_MANUT)

            with c3:
                solicitante = st.text_input("Solicitante")
                aprovador = st.text_input("Aprovador")

            st.markdown("### Custos e Horas")
            cx1, cx2 = st.columns(2)

            with cx1:
                custo = st.number_input("Custo Manutenção (R$)", min_value=0.0, step=0.01, format="%.2f")

            linha_equip = df_equip[df_equip["Código"].astype(str) == equip_sel.split(" - ")[0]].iloc[0]

            st.markdown("### Colaboradores")
            cc1, cc2, cc3 = st.columns(3)

            with cc1:
                colab1 = st.selectbox("Colaborador 1", opcoes_colab, key="c1")
                horas1_txt = st.text_input("Horas 1 (HH:MM)", value="00:00")

            with cc2:
                colab2 = st.selectbox("Colaborador 2", opcoes_colab, key="c2")
                horas2_txt = st.text_input("Horas 2 (HH:MM)", value="00:00")

            with cc3:
                colab3 = st.selectbox("Colaborador 3", opcoes_colab, key="c3")
                horas3_txt = st.text_input("Horas 3 (HH:MM)", value="00:00")

            problema = st.text_area("Descrição do Problema")
            servico = st.text_area("Serviço Executado")

            btn = st.form_submit_button("Salvar OM")

            if btn:
                try:
                    if not validar_hora_hhmm(horas1_txt):
                        raise ValueError("Horas 1 inválida. Use HH:MM.")
                    if not validar_hora_hhmm(horas2_txt):
                        raise ValueError("Horas 2 inválida. Use HH:MM.")
                    if not validar_hora_hhmm(horas3_txt):
                        raise ValueError("Horas 3 inválida. Use HH:MM.")

                    horas1 = hhmm_para_horas_decimal(horas1_txt)
                    horas2 = hhmm_para_horas_decimal(horas2_txt)
                    horas3 = hhmm_para_horas_decimal(horas3_txt)

                    total_horas = float(horas1) + float(horas2) + float(horas3)
                    numero_om = gerar_numero_om(data_om)

                    dados_om = {
                        "N° OM": numero_om,
                        "Data": pd.to_datetime(data_om).strftime("%Y-%m-%d"),
                        "Código": str(linha_equip["Código"]),
                        "Equipamento": str(linha_equip["Equipamento"]),
                        "Marca": str(linha_equip["Marca"]),
                        "Modelo": str(linha_equip["Modelo"]),
                        "Setor": str(linha_equip["Setor"]),
                        "Área": str(linha_equip["Área"]),
                        "Tipo Manutenção": tipo_manut,
                        "Solicitante": solicitante.strip(),
                        "Aprovador": aprovador.strip(),
                        "Colaborador 1": colab1,
                        "Horas 1": float(horas1),
                        "Colaborador 2": colab2,
                        "Horas 2": float(horas2),
                        "Colaborador 3": colab3,
                        "Horas 3": float(horas3),
                        "Total Horas": total_horas,
                        "Descrição do Problema": problema.strip(),
                        "Serviço Executado": servico.strip(),
                        "Custo Manutenção": float(custo)
                    }

                    ok, msg = adicionar_om(dados_om)

                    if ok:
                        st.session_state.mensagem_om_salva = f"Ordem de Manutenção salva com sucesso. Número da OM: {numero_om}"
                        st.rerun()
                    else:
                        st.error(msg)

                except Exception as e:
                    st.error(str(e))

# =========================
# HISTÓRICO
# =========================
elif menu == "Histórico":
    st.subheader("Histórico de Ordens de Manutenção")

    df_om = preparar_df_om()

    if df_om.empty:
        st.info("Não há OMs cadastradas.")
    else:
        with st.expander("Filtros", expanded=True):
            f1, f2, f3 = st.columns(3)

            with f1:
                lista_tipos = sorted(df_om["Tipo Manutenção"].dropna().astype(str).unique().tolist())
                filtro_tipo = st.selectbox("Tipo de Manutenção", ["Todos"] + lista_tipos)

            with f2:
                lista_areas = sorted(df_om["Área"].dropna().astype(str).unique().tolist())
                filtro_area = st.selectbox("Área", ["Todas"] + lista_areas)

            with f3:
                lista_codigos = sorted(df_om["Código"].dropna().astype(str).unique().tolist())
                filtro_codigo = st.selectbox("Código", ["Todos"] + lista_codigos)

            termo = st.text_input("Pesquisar por equipamento, OM ou texto livre")

        hist = df_om.copy()

        if filtro_tipo != "Todos":
            hist = hist[hist["Tipo Manutenção"].astype(str) == filtro_tipo]

        if filtro_area != "Todas":
            hist = hist[hist["Área"].astype(str) == filtro_area]

        if filtro_codigo != "Todos":
            hist = hist[hist["Código"].astype(str) == filtro_codigo]

        if termo.strip():
            t = termo.strip().lower()
            hist = hist[
                hist["Equipamento"].astype(str).str.lower().str.contains(t, na=False)
                | hist["Código"].astype(str).str.lower().str.contains(t, na=False)
                | hist["N° OM"].astype(str).str.lower().str.contains(t, na=False)
                | hist["Descrição do Problema"].astype(str).str.lower().str.contains(t, na=False)
                | hist["Serviço Executado"].astype(str).str.lower().str.contains(t, na=False)
                | hist["Solicitante"].astype(str).str.lower().str.contains(t, na=False)
                | hist["Aprovador"].astype(str).str.lower().str.contains(t, na=False)
            ]

        hist_exib = hist.copy()
        hist_exib["Data"] = hist_exib["Data"].dt.strftime("%d/%m/%Y")
        hist_exib["Horas 1"] = hist_exib["Horas 1"].map(decimal_para_hhmm)
        hist_exib["Horas 2"] = hist_exib["Horas 2"].map(decimal_para_hhmm)
        hist_exib["Horas 3"] = hist_exib["Horas 3"].map(decimal_para_hhmm)
        hist_exib["Total Horas"] = hist_exib["Total Horas"].map(decimal_para_hhmm)
        hist_exib["Custo Manutenção"] = hist_exib["Custo Manutenção"].map(formatar_moeda)

        colunas_exibicao = [
            "N° OM",
            "Data",
            "Código",
            "Equipamento",
            "Área",
            "Tipo Manutenção",
            "Solicitante",
            "Aprovador",
            "Colaborador 1",
            "Horas 1",
            "Colaborador 2",
            "Horas 2",
            "Colaborador 3",
            "Horas 3",
            "Total Horas",
            "Descrição do Problema",
            "Serviço Executado",
            "Custo Manutenção"
        ]

        st.dataframe(hist_exib[colunas_exibicao], width="stretch", hide_index=True)

        t1, t2, t3 = st.columns(3)

        with t1:
            st.metric("OMs filtradas", len(hist))

        with t2:
            st.metric("Horas totais filtradas", decimal_para_hhmm(hist["Total Horas"].sum()))

        with t3:
            st.metric("Custo total filtrado", formatar_moeda(hist["Custo Manutenção"].sum()))

        st.markdown("### Impressão de até 5 OMs")
        opcoes_impressao = hist.apply(
            lambda x: f'{x["N° OM"]} - {formatar_data_br(x["Data"])} - {x["Código"]} - {x["Equipamento"]}',
            axis=1
        ).tolist()

        oms_selecionadas = st.multiselect(
            "Selecione até 5 OMs para impressão",
            options=opcoes_impressao,
            max_selections=5
        )

        if oms_selecionadas:
            numeros_selecionados = [item.split(" - ")[0] for item in oms_selecionadas]
            df_imp = hist[hist["N° OM"].astype(str).isin(numeros_selecionados)].copy()
            html_oms = gerar_html_oms_selecionadas(df_imp, st.session_state.nome_empresa)

            st.download_button(
                label="Baixar impressão das OMs selecionadas (HTML)",
                data=html_oms,
                file_name="oms_selecionadas.html",
                mime="text/html"
            )

        abas = st.tabs(["Editar OM", "Excluir OM"])

        with abas[0]:
            opcoes_om = hist.apply(
                lambda x: f'{x["N° OM"]} - {formatar_data_br(x["Data"])} - {x["Código"]} - {x["Equipamento"]}',
                axis=1
            ).tolist()

            om_sel = st.selectbox("Selecione uma OM para editar", [""] + opcoes_om)

            if om_sel:
                numero_sel = om_sel.split(" - ")[0]
                linha = df_om[df_om["N° OM"].astype(str) == str(numero_sel)].iloc[0]

                df_equip = carregar_csv(ARQ_EQUIP, COLUNAS_EQUIP)
                df_colab = carregar_csv(ARQ_COLAB, COLUNAS_COLAB)

                opcoes_equip = df_equip.apply(
                    lambda x: f'{x["Código"]} - {x["Equipamento"]} - {x["Área"]}',
                    axis=1
                ).tolist()

                opcoes_colab = [""] + sorted(df_colab["Nome"].astype(str).tolist())

                equip_atual = f'{linha["Código"]} - {linha["Equipamento"]} - {linha["Área"]}'
                idx_equip = opcoes_equip.index(equip_atual) if equip_atual in opcoes_equip else 0
                idx_tipo = TIPOS_MANUT.index(linha["Tipo Manutenção"]) if linha["Tipo Manutenção"] in TIPOS_MANUT else 0

                with st.form("form_edit_om"):
                    st.markdown('<div class="info-hora">Edite as horas no formato HH:MM. Exemplo: 02:15.</div>', unsafe_allow_html=True)

                    c1, c2, c3 = st.columns(3)

                    with c1:
                        st.text_input("N° OM", value=str(linha["N° OM"]), disabled=True)
                        nova_data = st.date_input(
                            "Data",
                            value=pd.to_datetime(linha["Data"]).date()
                            if pd.notna(pd.to_datetime(linha["Data"], errors="coerce"))
                            else datetime.today().date()
                        )

                    with c2:
                        novo_equip_sel = st.selectbox("Equipamento", opcoes_equip, index=idx_equip)
                        novo_tipo = st.selectbox("Tipo de Manutenção", TIPOS_MANUT, index=idx_tipo)

                    with c3:
                        novo_solicitante = st.text_input("Solicitante", value=str(linha["Solicitante"]))
                        novo_aprovador = st.text_input("Aprovador", value=str(linha["Aprovador"]))

                    novo_custo = st.number_input(
                        "Custo Manutenção (R$)",
                        min_value=0.0,
                        step=0.01,
                        format="%.2f",
                        value=float(converter_numero(linha["Custo Manutenção"]))
                    )

                    st.markdown("### Colaboradores")
                    cc1, cc2, cc3 = st.columns(3)

                    idx_c1 = opcoes_colab.index(str(linha["Colaborador 1"])) if str(linha["Colaborador 1"]) in opcoes_colab else 0
                    idx_c2 = opcoes_colab.index(str(linha["Colaborador 2"])) if str(linha["Colaborador 2"]) in opcoes_colab else 0
                    idx_c3 = opcoes_colab.index(str(linha["Colaborador 3"])) if str(linha["Colaborador 3"]) in opcoes_colab else 0

                    with cc1:
                        novo_colab1 = st.selectbox("Colaborador 1", opcoes_colab, index=idx_c1, key="edc1")
                        nova_hora1_txt = st.text_input("Horas 1 (HH:MM)", value=decimal_para_hhmm(linha["Horas 1"]))

                    with cc2:
                        novo_colab2 = st.selectbox("Colaborador 2", opcoes_colab, index=idx_c2, key="edc2")
                        nova_hora2_txt = st.text_input("Horas 2 (HH:MM)", value=decimal_para_hhmm(linha["Horas 2"]))

                    with cc3:
                        novo_colab3 = st.selectbox("Colaborador 3", opcoes_colab, index=idx_c3, key="edc3")
                        nova_hora3_txt = st.text_input("Horas 3 (HH:MM)", value=decimal_para_hhmm(linha["Horas 3"]))

                    novo_prob = st.text_area("Descrição do Problema", value=str(linha["Descrição do Problema"]))
                    novo_serv = st.text_area("Serviço Executado", value=str(linha["Serviço Executado"]))

                    btn = st.form_submit_button("Salvar Alterações da OM")

                    if btn:
                        try:
                            if not validar_hora_hhmm(nova_hora1_txt):
                                raise ValueError("Horas 1 inválida. Use HH:MM.")
                            if not validar_hora_hhmm(nova_hora2_txt):
                                raise ValueError("Horas 2 inválida. Use HH:MM.")
                            if not validar_hora_hhmm(nova_hora3_txt):
                                raise ValueError("Horas 3 inválida. Use HH:MM.")

                            nova_hora1 = hhmm_para_horas_decimal(nova_hora1_txt)
                            nova_hora2 = hhmm_para_horas_decimal(nova_hora2_txt)
                            nova_hora3 = hhmm_para_horas_decimal(nova_hora3_txt)

                            novo_cod = novo_equip_sel.split(" - ")[0]
                            linha_equip = df_equip[df_equip["Código"].astype(str) == str(novo_cod)].iloc[0]
                            novo_total_horas = float(nova_hora1) + float(nova_hora2) + float(nova_hora3)

                            dados_om = {
                                "N° OM": str(linha["N° OM"]),
                                "Data": pd.to_datetime(nova_data).strftime("%Y-%m-%d"),
                                "Código": str(linha_equip["Código"]),
                                "Equipamento": str(linha_equip["Equipamento"]),
                                "Marca": str(linha_equip["Marca"]),
                                "Modelo": str(linha_equip["Modelo"]),
                                "Setor": str(linha_equip["Setor"]),
                                "Área": str(linha_equip["Área"]),
                                "Tipo Manutenção": novo_tipo,
                                "Solicitante": novo_solicitante.strip(),
                                "Aprovador": novo_aprovador.strip(),
                                "Colaborador 1": novo_colab1,
                                "Horas 1": float(nova_hora1),
                                "Colaborador 2": novo_colab2,
                                "Horas 2": float(nova_hora2),
                                "Colaborador 3": novo_colab3,
                                "Horas 3": float(nova_hora3),
                                "Total Horas": novo_total_horas,
                                "Descrição do Problema": novo_prob.strip(),
                                "Serviço Executado": novo_serv.strip(),
                                "Custo Manutenção": float(novo_custo)
                            }

                            ok, msg = editar_om(numero_sel, dados_om)

                            if ok:
                                st.success(msg)
                                st.rerun()
                            else:
                                st.error(msg)

                        except Exception as e:
                            st.error(str(e))

        with abas[1]:
            opcoes_om = hist.apply(
                lambda x: f'{x["N° OM"]} - {formatar_data_br(x["Data"])} - {x["Código"]} - {x["Equipamento"]}',
                axis=1
            ).tolist()

            om_exc = st.selectbox("Selecione uma OM para excluir", [""] + opcoes_om, key="exc_om")

            if om_exc:
                numero_exc = om_exc.split(" - ")[0]
                confirmar = st.checkbox("Confirmo a exclusão da OM", key="conf_exc_om")

                if st.button("Excluir OM", key="btn_exc_om"):
                    if not confirmar:
                        st.error("Marque a confirmação para excluir.")
                    else:
                        ok, msg = excluir_om(numero_exc)
                        if ok:
                            st.success(msg)
                            st.rerun()
                        else:
                            st.error(msg)

# =========================
# HORAS POR COLABORADOR
# =========================
elif menu == "Horas por Colaborador":
    st.subheader("Soma de Horas por Colaborador")

    df_om = preparar_df_om()

    if df_om.empty:
        st.info("Não há dados de OMs cadastradas.")
    else:
        f1, f2, f3 = st.columns(3)

        anos = sorted([int(a) for a in df_om["Ano"].dropna().unique()])
        meses = sorted([int(m) for m in df_om["Mês"].dropna().unique()])
        semanas = sorted([int(s) for s in df_om["Semana"].dropna().unique()])

        with f1:
            ano_sel = st.selectbox("Ano", ["Todos"] + anos, key="hora_ano")

        with f2:
            opcoes_meses = ["Todos"] + [MESES_PT[m] for m in meses]
            mes_sel = st.selectbox("Mês", opcoes_meses, key="hora_mes")

        with f3:
            semana_sel = st.selectbox("Semana", ["Todas"] + semanas, key="hora_semana")

        filtro = df_om.copy()

        if ano_sel != "Todos":
            filtro = filtro[filtro["Ano"] == ano_sel]

        if mes_sel != "Todos":
            numero_mes = [k for k, v in MESES_PT.items() if v == mes_sel][0]
            filtro = filtro[filtro["Mês"] == numero_mes]

        if semana_sel != "Todas":
            filtro = filtro[filtro["Semana"] == semana_sel]

        registros = []

        for _, row in filtro.iterrows():
            for n in [1, 2, 3]:
                nome = str(row.get(f"Colaborador {n}", "")).strip()
                horas = converter_numero(row.get(f"Horas {n}", 0))
                if nome:
                    registros.append({
                        "Colaborador": nome,
                        "Horas": horas
                    })

        if registros:
            df_horas = pd.DataFrame(registros)
            resumo = (
                df_horas.groupby("Colaborador", as_index=False)["Horas"]
                .sum()
                .sort_values(by="Horas", ascending=False)
            )

            resumo_exib = resumo.copy()
            resumo_exib["Horas"] = resumo_exib["Horas"].map(decimal_para_hhmm)

            t1, t2 = st.columns(2)
            with t1:
                st.metric("Total de colaboradores no período", len(resumo))
            with t2:
                st.metric("Horas totais no período", decimal_para_hhmm(resumo["Horas"].sum()))

            st.dataframe(resumo_exib, width="stretch", hide_index=True)
        else:
            st.info("Não há horas lançadas para os filtros selecionados.")
 