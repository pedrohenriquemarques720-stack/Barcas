import streamlit as st
import json
import os
from datetime import datetime

st.set_page_config(page_title="Barcas de Maionese", layout="wide")

# CSS simples
st.markdown("""
<style>
.botao-vermelho button {
    background-color: #FF6B6B;
    color: white;
}
</style>
""", unsafe_allow_html=True)

# Banco de dados simples
ARQUIVO_DADOS = "pedidos.json"

def carregar_dados():
    if not os.path.exists(ARQUIVO_DADOS):
        return {"pedidos": [], "proximo_id": 1}
    with open(ARQUIVO_DADOS, "r") as f:
        return json.load(f)

def salvar_dados(dados):
    with open(ARQUIVO_DADOS, "w") as f:
        json.dump(dados, f, indent=2, ensure_ascii=False)

# Produtos
PRODUTOS = [
    {"id": 1, "nome": "Barca P", "preco": 25},
    {"id": 2, "nome": "Barca M", "preco": 35},
    {"id": 3, "nome": "Barca G", "preco": 45}
]

# ==================== INTERFACE ====================
st.title("🍽️ Barcas de Maionese")

# Menu no sidebar
with st.sidebar:
    st.image("https://via.placeholder.com/150x150?text=Barcas", use_container_width=True)
    menu = st.radio("Menu", ["🛍️ Fazer Pedido", "📊 Admin"])

# ==================== ÁREA DO CLIENTE ====================
if menu == "🛍️ Fazer Pedido":
    st.header("📝 Novo Pedido")
    
    with st.form("form_pedido"):
        nome = st.text_input("Seu nome")
        
        tipo = st.selectbox("Tipo de cliente", ["PF", "PJ"])
        if tipo == "PF":
            documento = st.text_input("CPF")
        else:
            documento = st.text_input("CNPJ")
        
        st.subheader("Itens do pedido")
        itens = []
        for p in PRODUTOS:
            qtd = st.number_input(f"{p['nome']} - R$ {p['preco']}", min_value=0, value=0, key=p['id'])
            if qtd > 0:
                itens.append({"nome": p['nome'], "qtd": qtd, "preco": p['preco']})
        
        obs = st.text_area("Observações")
        
        if itens:
            total = sum(i['qtd'] * i['preco'] for i in itens)
            st.info(f"Total: R$ {total:.2f}")
        
        enviar = st.form_submit_button("Finalizar Pedido")
        
        if enviar:
            if not nome:
                st.error("Digite seu nome")
            elif not documento:
                st.error("Digite o documento")
            elif not itens:
                st.error("Selecione pelo menos um item")
            else:
                dados = carregar_dados()
                pedido = {
                    "id": dados["proximo_id"],
                    "data": datetime.now().strftime("%d/%m/%Y %H:%M"),
                    "nome": nome,
                    "tipo": tipo,
                    "documento": documento,
                    "itens": itens,
                    "total": total,
                    "status": "Pendente",
                    "obs": obs
                }
                dados["pedidos"].append(pedido)
                dados["proximo_id"] += 1
                salvar_dados(dados)
                
                st.success(f"✅ Pedido #{pedido['id']} recebido!")
                st.balloons()

# ==================== ÁREA ADMIN ====================
else:
    if "admin_logado" not in st.session_state:
        st.session_state.admin_logado = False
    
    if not st.session_state.admin_logado:
        st.info("🔐 Área administrativa")
        senha = st.text_input("Senha", type="password")
        if st.button("Entrar"):
            if senha == "admin123":
                st.session_state.admin_logado = True
                st.rerun()
            else:
                st.error("Senha errada")
    else:
        st.header("📊 Dashboard")
        
        if st.button("Sair"):
            st.session_state.admin_logado = False
            st.rerun()
        
        dados = carregar_dados()
        pedidos = dados["pedidos"]
        
        if pedidos:
            # Estatísticas
            total_vendas = sum(p["total"] for p in pedidos)
            total_pedidos = len(pedidos)
            pf = len([p for p in pedidos if p["tipo"] == "PF"])
            pj = len([p for p in pedidos if p["tipo"] == "PJ"])
            
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("💰 Faturamento", f"R$ {total_vendas:,.2f}")
            col2.metric("📦 Pedidos", total_pedidos)
            col3.metric("👤 PF", pf)
            col4.metric("🏢 PJ", pj)
            
            st.divider()
            
            # Status
            pendentes = len([p for p in pedidos if p["status"] == "Pendente"])
            preparando = len([p for p in pedidos if p["status"] == "Preparando"])
            entregues = len([p for p in pedidos if p["status"] == "Entregue"])
            
            col1, col2, col3 = st.columns(3)
            col1.metric("🟡 Pendente", pendentes)
            col2.metric("🔵 Preparando", preparando)
            col3.metric("🟢 Entregue", entregues)
            
            st.divider()
            
            # Filtros
            filtro_status = st.selectbox("Filtrar por status", ["Todos", "Pendente", "Preparando", "Entregue"])
            
            # Lista de pedidos
            st.subheader("📋 Pedidos")
            
            for p in pedidos:
                if filtro_status != "Todos" and p["status"] != filtro_status:
                    continue
                
                with st.container():
                    col1, col2, col3, col4 = st.columns([2, 2, 2, 1])
                    
                    with col1:
                        st.markdown(f"**Pedido #{p['id']}**")
                        st.caption(p['data'])
                    
                    with col2:
                        st.markdown(f"**{p['nome']}**")
                        st.markdown(f"{p['tipo']}: {p['documento']}")
                    
                    with col3:
                        st.markdown(f"💰 R$ {p['total']:.2f}")
                        itens_str = ", ".join([f"{i['qtd']}x {i['nome']}" for i in p['itens']])
                        st.caption(itens_str)
                        if p.get('obs'):
                            st.caption(f"Obs: {p['obs'][:50]}")
                    
                    with col4:
                        if p['status'] == "Pendente":
                            st.markdown("🟡 **Pendente**")
                        elif p['status'] == "Preparando":
                            st.markdown("🔵 **Preparando**")
                        else:
                            st.markdown("🟢 **Entregue**")
                        
                        if p['status'] != "Entregue":
                            novo = st.selectbox(
                                "Status",
                                ["Pendente", "Preparando", "Entregue"],
                                index=["Pendente", "Preparando", "Entregue"].index(p['status']),
                                key=f"sel_{p['id']}",
                                label_visibility="collapsed"
                            )
                            if novo != p['status']:
                                if st.button("Atualizar", key=f"btn_{p['id']}"):
                                    p['status'] = novo
                                    salvar_dados(dados)
                                    st.success("Atualizado!")
                                    st.rerun()
                    
                    st.divider()
            
            # Histórico
            with st.expander("📜 Histórico de Entregues"):
                entregues_lista = [p for p in pedidos if p["status"] == "Entregue"]
                if entregues_lista:
                    for p in entregues_lista[-10:]:
                        st.write(f"#{p['id']} - {p['nome']} - R$ {p['total']} - {p['data']}")
                else:
                    st.info("Nenhum pedido entregue")
        
        else:
            st.info("Nenhum pedido ainda")

# Rodapé
st.sidebar.markdown("---")
st.sidebar.caption("Versão 1.0")
