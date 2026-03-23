import streamlit as st
import pandas as pd
import plotly.express as px
from utils.auth import verificar_admin, mostrar_login, fazer_logout

def pagina_admin(db):
    """Página do administrador"""
    
    # Verificar login
    if not verificar_admin():
        st.warning("🔐 Área restrita - Faça login para continuar")
        mostrar_login("admin123")
        return
    
    # Dashboard
    st.header("📊 Dashboard")
    
    # Botão logout
    col1, col2, col3 = st.columns([1, 1, 8])
    with col1:
        if st.button("🚪 Sair"):
            fazer_logout()
    
    # Estatísticas
    stats = db.obter_estatisticas()
    
    # Cards
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("💰 Faturamento", f"R$ {stats['faturamento_total']:,.2f}")
    with col2:
        st.metric("📦 Total Pedidos", stats['total_pedidos'])
    with col3:
        st.metric("👤 Pedidos PF", stats['pedidos_pf'])
    with col4:
        st.metric("🏢 Pedidos PJ", stats['pedidos_pj'])
    
    st.divider()
    
    # Gráficos
    col1, col2 = st.columns(2)
    
    with col1:
        if stats['status_counts']:
            fig = px.pie(
                values=list(stats['status_counts'].values()),
                names=list(stats['status_counts'].keys()),
                title="Status dos Pedidos",
                color_discrete_sequence=['#FF6B6B', '#4ECDC4', '#45B7D1']
            )
            st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        fig = px.bar(
            x=['PF', 'PJ'],
            y=[stats['pedidos_pf'], stats['pedidos_pj']],
            title="Pedidos por Tipo",
            text_auto=True,
            color=['PF', 'PJ'],
            color_discrete_sequence=['#FF6B6B', '#4ECDC4']
        )
        st.plotly_chart(fig, use_container_width=True)
    
    st.divider()
    
    # Gestão de pedidos
    st.header("📋 Gestão de Pedidos")
    
    # Filtros
    col1, col2 = st.columns(2)
    with col1:
        filtro_status = st.selectbox("Status", ["Todos", "Pendente", "Preparando", "Entregue"])
    with col2:
        filtro_tipo = st.selectbox("Tipo", ["Todos", "PF", "PJ"])
    
    # Buscar pedidos
    status_filtro = None if filtro_status == "Todos" else filtro_status
    pedidos = db.listar_pedidos(status=status_filtro)
    
    if pedidos:
        # Filtrar por tipo
        if filtro_tipo != "Todos":
            pedidos = [p for p in pedidos if p['tipo_cliente'] == filtro_tipo]
        
        for pedido in pedidos:
            with st.container():
                col1, col2, col3, col4, col5 = st.columns([2, 2, 2, 1.5, 1.5])
                
                with col1:
                    st.markdown(f"**Pedido #{pedido['id']}**")
                    st.caption(pedido['data_hora'][:16])
                
                with col2:
                    st.markdown(f"**{pedido['nome_cliente']}**")
                    st.markdown(f"{pedido['tipo_cliente']}: {pedido['documento']}")
                
                with col3:
                    st.markdown(f"💰 **R$ {pedido['valor_total']:.2f}**")
                    st.markdown(f"🏷️ {pedido['categoria']}")
                    if pedido.get('observacoes'):
                        st.caption(f"📝 {pedido['observacoes'][:40]}")
                
                with col4:
                    status = pedido['status']
                    if status == "Pendente":
                        st.markdown("🟡 **Pendente**")
                    elif status == "Preparando":
                        st.markdown("🔵 **Preparando**")
                    else:
                        st.markdown("🟢 **Entregue**")
                
                with col5:
                    if status != "Entregue":
                        opcoes = ["Pendente", "Preparando", "Entregue"]
                        idx = opcoes.index(status)
                        novo = st.selectbox(
                            "Status",
                            opcoes,
                            index=idx,
                            key=f"sel_{pedido['id']}",
                            label_visibility="collapsed"
                        )
                        
                        if novo != status:
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
            df['data'] = pd.to_datetime(df['data_hora']).dt.strftime('%d/%m/%Y %H:%M')
            df['valor'] = df['valor_total'].apply(lambda x: f"R$ {x:.2f}")
            st.dataframe(
                df[['id', 'data', 'nome_cliente', 'tipo_cliente', 'valor']],
                use_container_width=True,
                hide_index=True
            )

def main(db):
    pagina_admin(db)