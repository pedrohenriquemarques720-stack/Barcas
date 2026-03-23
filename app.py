import streamlit as st
import json
import os
from datetime import datetime

# Configuração da página
st.set_page_config(
    page_title="Barcas de Maionese",
    page_icon="🍽️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==================== BANCO DE DADOS ====================
ARQUIVO_DADOS = "pedidos.json"

def carregar_pedidos():
    if not os.path.exists(ARQUIVO_DADOS):
        return []
    try:
        with open(ARQUIVO_DADOS, 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        return []

def salvar_pedidos(pedidos):
    with open(ARQUIVO_DADOS, 'w', encoding='utf-8') as f:
        json.dump(pedidos, f, ensure_ascii=False, indent=2)

def obter_proximo_id(pedidos):
    if not pedidos:
        return 1
    return max(p["id"] for p in pedidos) + 1

# ==================== PRODUTOS ====================
PRODUTOS = [
    {"id": 1, "nome": "Barca P", "preco": 25.00, "descricao": "Serve 2-3 pessoas", "emoji": "🍽️"},
    {"id": 2, "nome": "Barca M", "preco": 35.00, "descricao": "Serve 4-5 pessoas", "emoji": "🍽️🍽️"},
    {"id": 3, "nome": "Barca G", "preco": 45.00, "descricao": "Serve 6-8 pessoas", "emoji": "🍽️🍽️🍽️"},
]

# ==================== CSS ====================
st.markdown("""
<style>
    /* Header */
    .main-header {
        background: linear-gradient(135deg, #FF6B6B 0%, #FF8E8E 100%);
        padding: 1.5rem;
        border-radius: 15px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    
    /* Cards produtos */
    .product-card {
        background: white;
        border: 2px solid #FF6B6B;
        border-radius: 15px;
        padding: 1.5rem;
        text-align: center;
        margin: 0.5rem;
        transition: transform 0.3s;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .product-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 5px 15px rgba(0,0,0,0.2);
    }
    
    /* Botões */
    .stButton > button {
        background-color: #FF6B6B;
        color: white;
        font-weight: bold;
        border-radius: 8px;
        border: none;
        padding: 0.6rem 1.2rem;
        transition: all 0.3s;
        width: 100%;
    }
    .stButton > button:hover {
        background-color: #FF5252;
        transform: translateY(-2px);
    }
    
    /* Status */
    .status-pendente {
        background-color: #ffc107;
        color: #000;
        padding: 4px 12px;
        border-radius: 20px;
        font-weight: bold;
        display: inline-block;
    }
    .status-preparando {
        background-color: #17a2b8;
        color: white;
        padding: 4px 12px;
        border-radius: 20px;
        font-weight: bold;
        display: inline-block;
    }
    .status-entregue {
        background-color: #28a745;
        color: white;
        padding: 4px 12px;
        border-radius: 20px;
        font-weight: bold;
        display: inline-block;
    }
    
    /* Container pedido */
    .order-card {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 10px;
        margin-bottom: 1rem;
        border-left: 4px solid #FF6B6B;
    }
    
    hr {
        margin: 2rem 0;
    }
</style>
""", unsafe_allow_html=True)

# ==================== FUNÇÃO CLIENTE ====================
def mostrar_cliente():
    st.markdown("""
    <div class="main-header">
        <h1>🍽️ Barcas de Maionese</h1>
        <p>O melhor sabor da região! Faça seu pedido agora.</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Catálogo de produtos
    st.header("📋 Cardápio")
    cols = st.columns(len(PRODUTOS))
    
    for idx, produto in enumerate(PRODUTOS):
        with cols[idx]:
            st.markdown(f"""
            <div class="product-card">
                <h2 style="font-size: 2rem;">{produto['emoji']}</h2>
                <h3>{produto['nome']}</h3>
                <p style="color: gray;">{produto['descricao']}</p>
                <h2 style="color: #FF6B6B;">R$ {produto['preco']:.2f}</h2>
            </div>
            """, unsafe_allow_html=True)
    
    st.divider()
    
    # Formulário
    st.header("📝 Faça seu Pedido")
    
    with st.form("form_pedido", clear_on_submit=True):
        col1, col2 = st.columns(2)
        
        with col1:
            nome = st.text_input("👤 Nome completo *", placeholder="Digite seu nome")
            
            tipo = st.radio("📄 Tipo de Cliente *", ["PF", "PJ"], horizontal=True)
            
            if tipo == "PF":
                doc = st.text_input("CPF *", placeholder="000.000.000-00")
            else:
                doc = st.text_input("CNPJ *", placeholder="00.000.000/0000-00")
                ie = st.text_input("Inscrição Estadual", placeholder="Opcional")
        
        with col2:
            categoria = st.selectbox("🏷️ Categoria", ["Cliente Fixo", "Cliente Variável"])
            categoria_valor = "Fixo" if categoria == "Cliente Fixo" else "Variável"
            
            st.markdown("---")
            st.markdown("### 🛒 Itens do Pedido")
            
            itens = []
            total = 0
            
            for p in PRODUTOS:
                qtd = st.number_input(
                    f"{p['nome']} - R$ {p['preco']:.2f}",
                    min_value=0, max_value=10, value=0,
                    key=f"qtd_{p['id']}"
                )
                if qtd > 0:
                    subtotal = qtd * p['preco']
                    total += subtotal
                    itens.append({
                        "nome": p['nome'],
                        "quantidade": qtd,
                        "preco": p['preco'],
                        "subtotal": subtotal
                    })
        
        obs = st.text_area("📝 Observações", placeholder="Ex: sem cebola, extra picles...")
        
        if itens:
            st.info(f"💰 **Total: R$ {total:.2f}**")
        else:
            st.warning("⚠️ Selecione pelo menos um item")
        
        enviar = st.form_submit_button("✅ Finalizar Pedido", use_container_width=True)
        
        if enviar:
            erros = []
            if not nome:
                erros.append("Nome é obrigatório")
            if not doc:
                erros.append("Documento é obrigatório")
            if not itens:
                erros.append("Selecione pelo menos um item")
            
            if erros:
                for erro in erros:
                    st.error(erro)
            else:
                pedidos = carregar_pedidos()
                
                pedido = {
                    "id": obter_proximo_id(pedidos),
                    "data": datetime.now().strftime("%d/%m/%Y %H:%M"),
                    "nome": nome,
                    "tipo": tipo,
                    "documento": doc,
                    "itens": itens,
                    "total": total,
                    "status": "Pendente",
                    "categoria": categoria_valor,
                    "obs": obs
                }
                
                if tipo == "PJ" and 'ie' in locals() and ie:
                    pedido["ie"] = ie
                
                pedidos.append(pedido)
                salvar_pedidos(pedidos)
                
                st.success(f"✅ **Pedido #{pedido['id']} recebido com sucesso!**")
                st.balloons()
                
                with st.expander("📋 Detalhes do Pedido", expanded=True):
                    st.write(f"**Cliente:** {pedido['nome']}")
                    st.write(f"**Total:** R$ {pedido['total']:.2f}")
                    st.write("**Itens:**")
                    for item in pedido['itens']:
                        st.write(f"- {item['quantidade']}x {item['nome']} = R$ {item['subtotal']:.2f}")
                    if obs:
                        st.write(f"**Obs:** {obs}")

# ==================== FUNÇÃO ADMIN ====================
def mostrar_admin():
    # Login
    if "logado" not in st.session_state:
        st.session_state.logado = False
    
    if not st.session_state.logado:
        st.markdown("""
        <div class="main-header">
            <h1>🔐 Área Administrativa</h1>
            <p>Acesso restrito</p>
        </div>
        """, unsafe_allow_html=True)
        
        with st.form("login"):
            senha = st.text_input("Senha", type="password")
            if st.form_submit_button("Entrar", use_container_width=True):
                if senha == "admin123":
                    st.session_state.logado = True
                    st.rerun()
                else:
                    st.error("Senha incorreta!")
        return
    
    # Dashboard
    st.markdown("""
    <div class="main-header">
        <h1>📊 Dashboard</h1>
        <p>Gerencie seus pedidos</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Botão sair
    col1, col2, col3 = st.columns([1, 1, 8])
    with col1:
        if st.button("🚪 Sair", use_container_width=True):
            st.session_state.logado = False
            st.rerun()
    
    pedidos = carregar_pedidos()
    
    if not pedidos:
        st.info("📭 Nenhum pedido cadastrado")
        return
    
    # ===== ESTATÍSTICAS =====
    total_vendas = sum(p["total"] for p in pedidos)
    total_pedidos = len(pedidos)
    pf = len([p for p in pedidos if p["tipo"] == "PF"])
    pj = len([p for p in pedidos if p["tipo"] == "PJ"])
    
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("💰 Faturamento", f"R$ {total_vendas:,.2f}")
    col2.metric("📦 Pedidos", total_pedidos)
    col3.metric("👤 PF", pf)
    col4.metric("🏢 PJ", pj)
    
    # Status
    pendentes = len([p for p in pedidos if p["status"] == "Pendente"])
    preparando = len([p for p in pedidos if p["status"] == "Preparando"])
    entregues = len([p for p in pedidos if p["status"] == "Entregue"])
    
    col1, col2, col3 = st.columns(3)
    col1.metric("🟡 Pendente", pendentes)
    col2.metric("🔵 Preparando", preparando)
    col3.metric("🟢 Entregue", entregues)
    
    st.divider()
    
    # ===== FILTROS =====
    st.header("📋 Gestão de Pedidos")
    
    col1, col2 = st.columns(2)
    with col1:
        filtro_status = st.selectbox("Status", ["Todos", "Pendente", "Preparando", "Entregue"])
    with col2:
        filtro_tipo = st.selectbox("Tipo", ["Todos", "PF", "PJ"])
    
    # Filtrar
    pedidos_filtrados = pedidos.copy()
    if filtro_status != "Todos":
        pedidos_filtrados = [p for p in pedidos_filtrados if p["status"] == filtro_status]
    if filtro_tipo != "Todos":
        pedidos_filtrados = [p for p in pedidos_filtrados if p["tipo"] == filtro_tipo]
    
    pedidos_filtrados.sort(key=lambda x: x["id"], reverse=True)
    
    if not pedidos_filtrados:
        st.info("Nenhum pedido encontrado")
    else:
        for p in pedidos_filtrados:
            with st.container():
                col1, col2, col3, col4 = st.columns([2, 2, 2, 1.5])
                
                with col1:
                    st.markdown(f"**Pedido #{p['id']}**")
                    st.caption(p['data'])
                
                with col2:
                    st.markdown(f"**{p['nome']}**")
                    st.markdown(f"{p['tipo']}: {p['documento']}")
                    if p.get('ie'):
                        st.caption(f"IE: {p['ie']}")
                
                with col3:
                    st.markdown(f"💰 **R$ {p['total']:.2f}**")
                    st.markdown(f"🏷️ {p['categoria']}")
                    itens_resumo = ", ".join([f"{i['quantidade']}x {i['nome']}" for i in p['itens']])
                    st.caption(f"📦 {itens_resumo[:50]}")
                    if p.get('obs'):
                        st.caption(f"📝 {p['obs'][:40]}")
                
                with col4:
                    if p['status'] == "Pendente":
                        st.markdown('<span class="status-pendente">🟡 Pendente</span>', unsafe_allow_html=True)
                        if st.button("🔵 Preparar", key=f"prep_{p['id']}", use_container_width=True):
                            p['status'] = "Preparando"
                            salvar_pedidos(pedidos)
                            st.success(f"Pedido #{p['id']} em preparo!")
                            st.rerun()
                    elif p['status'] == "Preparando":
                        st.markdown('<span class="status-preparando">🔵 Preparando</span>', unsafe_allow_html=True)
                        if st.button("🟢 Entregar", key=f"ent_{p['id']}", use_container_width=True):
                            p['status'] = "Entregue"
                            salvar_pedidos(pedidos)
                            st.success(f"Pedido #{p['id']} entregue!")
                            st.rerun()
                    else:
                        st.markdown('<span class="status-entregue">🟢 Entregue</span>', unsafe_allow_html=True)
                
                st.divider()
    
    # Histórico
    with st.expander("📜 Histórico de Entregues"):
        entregues_lista = [p for p in pedidos if p["status"] == "Entregue"]
        if entregues_lista:
            for p in entregues_lista[-10:]:
                st.write(f"#{p['id']} - {p['nome']} - R$ {p['total']:.2f} - {p['data']}")
        else:
            st.info("Nenhum pedido entregue")

# ==================== MAIN ====================
def main():
    # Sidebar
    with st.sidebar:
        st.markdown("## 🍽️ Barcas")
        st.markdown("---")
        
        pagina = st.radio(
            "📌 Menu",
            ["🛍️ Fazer Pedido", "📊 Área Admin"],
            index=0
        )
        
        st.markdown("---")
        
        pedidos = carregar_pedidos()
        st.metric("📦 Pedidos", len(pedidos))
        
        st.markdown("---")
        st.caption("v1.0")
    
    # Conteúdo
    if pagina == "🛍️ Fazer Pedido":
        mostrar_cliente()
    else:
        mostrar_admin()

if __name__ == "__main__":
    main()
