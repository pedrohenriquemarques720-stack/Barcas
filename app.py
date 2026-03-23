import streamlit as st
import pandas as pd
from datetime import datetime
import json
import os

st.set_page_config(page_title="Barcas de Maionese", page_icon="🍽️", layout="wide")

# CSS
st.markdown("""
<style>
.stButton>button {
    background-color: #FF6B6B;
    color: white;
    font-weight: bold;
    border-radius: 8px;
    border: none;
    padding: 0.5rem 1rem;
}
.stButton>button:hover {
    background-color: #FF5252;
}
.main-header {
    background: linear-gradient(135deg, #FF6B6B 0%, #FF8E8E 100%);
    padding: 1rem;
    border-radius: 10px;
    color: white;
    text-align: center;
    margin-bottom: 2rem;
}
.product-card {
    border: 2px solid #FF6B6B;
    border-radius: 10px;
    padding: 1rem;
    text-align: center;
    margin: 0.5rem;
}
.status-pendente { color: #ffc107; font-weight: bold; }
.status-preparando { color: #17a2b8; font-weight: bold; }
.status-entregue { color: #28a745; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

# ==================== BANCO DE DADOS ====================
class Database:
    def __init__(self):
        self.arquivo = "dados.json"
        self.produtos = [
            {"id": 1, "nome": "Barca P", "preco": 25.00, "descricao": "Serve 2-3 pessoas"},
            {"id": 2, "nome": "Barca M", "preco": 35.00, "descricao": "Serve 4-5 pessoas"},
            {"id": 3, "nome": "Barca G", "preco": 45.00, "descricao": "Serve 6-8 pessoas"}
        ]
        self.carregar()
    
    def carregar(self):
        if not os.path.exists(self.arquivo):
            self.pedidos = []
            self.proximo_id = 1
            self.salvar()
        else:
            with open(self.arquivo, 'r', encoding='utf-8') as f:
                dados = json.load(f)
                self.pedidos = dados.get('pedidos', [])
                self.proximo_id = dados.get('proximo_id', 1)
    
    def salvar(self):
        with open(self.arquivo, 'w', encoding='utf-8') as f:
            json.dump({
                'pedidos': self.pedidos,
                'proximo_id': self.proximo_id
            }, f, ensure_ascii=False, indent=2)
    
    def criar_pedido(self, pedido):
        pedido["id"] = self.proximo_id
        pedido["data_hora"] = datetime.now().strftime("%d/%m/%Y %H:%M")
        pedido["status"] = "Pendente"
        self.pedidos.append(pedido)
        self.proximo_id += 1
        self.salvar()
        return pedido
    
    def listar_pedidos(self, status=None):
        if status:
            return [p for p in self.pedidos if p["status"] == status]
        return self.pedidos
    
    def atualizar_status(self, pedido_id, novo_status):
        for pedido in self.pedidos:
            if pedido["id"] == pedido_id:
                pedido["status"] = novo_status
                self.salvar()
                return True
        return False
    
    def obter_estatisticas(self):
        if not self.pedidos:
            return {
                'faturamento': 0,
                'total': 0,
                'pf': 0,
                'pj': 0,
                'pendente': 0,
                'preparando': 0,
                'entregue': 0
            }
        
        df = pd.DataFrame(self.pedidos)
        return {
            'faturamento': df['valor_total'].sum(),
            'total': len(df),
            'pf': len(df[df['tipo_cliente'] == 'PF']),
            'pj': len(df[df['tipo_cliente'] == 'PJ']),
            'pendente': len(df[df['status'] == 'Pendente']),
            'preparando': len(df[df['status'] == 'Preparando']),
            'entregue': len(df[df['status'] == 'Entregue'])
        }

db = Database()

# ==================== ÁREA DO CLIENTE ====================
def area_cliente():
    st.header("🍽️ Cardápio")
    
    # Mostrar produtos
    cols = st.columns(3)
    for idx, produto in enumerate(db.produtos):
        with cols[idx]:
            st.markdown(f"""
            <div class="product-card">
                <h3>{produto['nome']}</h3>
                <p>{produto['descricao']}</p>
                <h2 style="color: #FF6B6B;">R$ {produto['preco']:.2f}</h2>
            </div>
            """, unsafe_allow_html=True)
    
    st.divider()
    st.subheader("📝 Faça seu Pedido")
    
    with st.form("pedido_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            nome = st.text_input("Nome completo *")
            tipo = st.radio("Tipo de Cliente", ["PF", "PJ"], horizontal=True)
            
            if tipo == "PF":
                doc = st.text_input("CPF *", placeholder="000.000.000-00")
            else:
                doc = st.text_input("CNPJ *", placeholder="00.000.000/0000-00")
                ie = st.text_input("Inscrição Estadual (opcional)")
        
        with col2:
            categoria = st.selectbox("Categoria", ["Cliente Fixo", "Cliente Variável"])
            categoria_valor = "Fixo" if categoria == "Cliente Fixo" else "Variável"
            
            st.markdown("---")
            st.markdown("### Selecione os Itens")
            
            itens = []
            for p in db.produtos:
                qtd = st.number_input(f"{p['nome']} - R$ {p['preco']:.2f}", 
                                     min_value=0, max_value=10, value=0, key=f"p{p['id']}")
                if qtd > 0:
                    itens.append({"nome": p['nome'], "quantidade": qtd, "preco": p['preco']})
        
        obs = st.text_area("Observações")
        
        if itens:
            total = sum(i['quantidade'] * i['preco'] for i in itens)
            st.info(f"💰 **Total: R$ {total:.2f}**")
        
        if st.form_submit_button("✅ Finalizar Pedido", type="primary", use_container_width=True):
            erros = []
            if not nome: erros.append("Nome obrigatório")
            if not doc: erros.append("Documento obrigatório")
            if not itens: erros.append("Selecione pelo menos um item")
            
            if erros:
                for erro in erros:
                    st.error(erro)
            else:
                total = sum(i['quantidade'] * i['preco'] for i in itens)
                pedido = {
                    "nome_cliente": nome,
                    "tipo_cliente": tipo,
                    "documento": doc,
                    "itens_pedido": itens,
                    "valor_total": total,
                    "categoria": categoria_valor,
                    "observacoes": obs
                }
                if tipo == "PJ" and 'ie' in locals() and ie:
                    pedido["ie"] = ie
                
                pedido_salvo = db.criar_pedido(pedido)
                st.success(f"✅ Pedido #{pedido_salvo['id']} recebido!")
                st.balloons()
                
                with st.expander("Ver detalhes"):
                    st.write(f"**Cliente:** {pedido_salvo['nome_cliente']}")
                    st.write(f"**Total:** R$ {pedido_salvo['valor_total']:.2f}")
                    for item in pedido_salvo['itens_pedido']:
                        st.write(f"- {item['quantidade']}x {item['nome']}")
                    if obs:
                        st.write(f"**Obs:** {obs}")

# ==================== ÁREA ADMIN ====================
def area_admin():
    if 'logado' not in st.session_state:
        st.session_state.logado = False
    
    if not st.session_state.logado:
        st.info("🔐 Área Restrita")
        with st.form("login"):
            senha = st.text_input("Senha", type="password")
            if st.form_submit_button("Entrar"):
                if senha == "admin123":
                    st.session_state.logado = True
                    st.rerun()
                else:
                    st.error("Senha incorreta")
        return
    
    st.header("📊 Dashboard")
    
    # Botão sair
    if st.button("🚪 Sair"):
        st.session_state.logado = False
        st.rerun()
    
    # Estatísticas
    stats = db.obter_estatisticas()
    
    # Cards
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("💰 Faturamento", f"R$ {stats['faturamento']:,.2f}")
    with col2:
        st.metric("📦 Total Pedidos", stats['total'])
    with col3:
        st.metric("👤 PF", stats['pf'])
    with col4:
        st.metric("🏢 PJ", stats['pj'])
    
    # Status
    st.subheader("Status dos Pedidos")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("🟡 Pendente", stats['pendente'])
    with col2:
        st.metric("🔵 Preparando", stats['preparando'])
    with col3:
        st.metric("🟢 Entregue", stats['entregue'])
    
    st.divider()
    
    # Gestão de pedidos
    st.header("📋 Gestão de Pedidos")
    
    # Filtros
    col1, col2 = st.columns(2)
    with col1:
        filtro_status = st.selectbox("Filtrar por status", ["Todos", "Pendente", "Preparando", "Entregue"])
    with col2:
        filtro_tipo = st.selectbox("Filtrar por tipo", ["Todos", "PF", "PJ"])
    
    # Buscar pedidos
    status_filtro = None if filtro_status == "Todos" else filtro_status
    pedidos = db.listar_pedidos(status=status_filtro)
    
    if pedidos:
        if filtro_tipo != "Todos":
            pedidos = [p for p in pedidos if p['tipo_cliente'] == filtro_tipo]
        
        for pedido in pedidos:
            with st.container():
                col1, col2, col3, col4, col5 = st.columns([2, 2, 2, 1.5, 1.5])
                
                with col1:
                    st.markdown(f"**Pedido #{pedido['id']}**")
                    st.caption(pedido['data_hora'])
                
                with col2:
                    st.markdown(f"**{pedido['nome_cliente']}**")
                    st.markdown(f"{pedido['tipo_cliente']}: {pedido['documento']}")
                
                with col3:
                    st.markdown(f"💰 **R$ {pedido['valor_total']:.2f}**")
                    st.markdown(f"🏷️ {pedido['categoria']}")
                
                with col4:
                    if pedido['status'] == "Pendente":
                        st.markdown("🟡 **Pendente**")
                    elif pedido['status'] == "Preparando":
                        st.markdown("🔵 **Preparando**")
                    else:
                        st.markdown("🟢 **Entregue**")
                
                with col5:
                    if pedido['status'] != "Entregue":
                        opcoes = ["Pendente", "Preparando", "Entregue"]
                        idx = opcoes.index(pedido['status'])
                        novo = st.selectbox(
                            "Status", opcoes, index=idx,
                            key=f"status_{pedido['id']}",
                            label_visibility="collapsed"
                        )
                        if novo != pedido['status']:
                            if st.button("Atualizar", key=f"btn_{pedido['id']}", use_container_width=True):
                                if db.atualizar_status(pedido['id'], novo):
                                    st.success(f"Pedido #{pedido['id']} atualizado!")
                                    st.rerun()
                
                st.divider()
    else:
        st.info("Nenhum pedido encontrado")
    
    # Histórico
    with st.expander("📜 Histórico de Entregues"):
        entregues = db.listar_pedidos(status="Entregue")
        if entregues:
            df = pd.DataFrame(entregues)
            st.dataframe(
                df[['id', 'data_hora', 'nome_cliente', 'tipo_cliente', 'valor_total']],
                use_container_width=True,
                hide_index=True
            )

# ==================== MAIN ====================
def main():
    st.markdown("""
    <div class="main-header">
        <h1>🍽️ Barcas de Maionese</h1>
        <p>O melhor sabor da região!</p>
    </div>
    """, unsafe_allow_html=True)
    
    with st.sidebar:
        st.image("https://via.placeholder.com/150x150?text=Barcas", use_container_width=True)
        st.markdown("## 🍽️ Menu")
        pagina = st.radio("Navegação", ["🛍️ Fazer Pedido", "📊 Área Administrativa"])
        
        stats = db.obter_estatisticas()
        st.metric("📦 Pedidos Hoje", stats['total'])
    
    if pagina == "🛍️ Fazer Pedido":
        area_cliente()
    else:
        area_admin()

if __name__ == "__main__":
    main()
