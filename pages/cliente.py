import streamlit as st
from models.pedido import Produto
from datetime import datetime

def mostrar_catalogo():
    """Mostra catálogo de produtos"""
    st.header("🍽️ Cardápio")
    
    produtos = Produto.listar()
    cols = st.columns(len(produtos))
    
    for idx, produto in enumerate(produtos):
        with cols[idx]:
            st.markdown(f"""
            <div style="border: 2px solid #FF6B6B; border-radius: 10px; 
                        padding: 1rem; text-align: center; margin: 0.5rem;">
                <h3>{produto['nome']}</h3>
                <p style="color: gray;">{produto['descricao']}</p>
                <h2 style="color: #FF6B6B;">R$ {produto['preco']:.2f}</h2>
            </div>
            """, unsafe_allow_html=True)

def pagina_cliente(db):
    """Página do cliente"""
    
    mostrar_catalogo()
    st.divider()
    
    st.subheader("📝 Faça seu Pedido")
    
    with st.form("form_pedido", clear_on_submit=True):
        col1, col2 = st.columns(2)
        
        with col1:
            nome = st.text_input("Nome completo *")
            tipo = st.radio("Tipo de Cliente *", ["PF", "PJ"], horizontal=True)
            
            if tipo == "PF":
                documento = st.text_input("CPF *", placeholder="000.000.000-00")
            else:
                documento = st.text_input("CNPJ *", placeholder="00.000.000/0000-00")
                ie = st.text_input("Inscrição Estadual (opcional)")
        
        with col2:
            categoria = st.selectbox("Categoria *", ["Cliente Fixo", "Cliente Variável"])
            categoria_valor = "Fixo" if categoria == "Cliente Fixo" else "Variável"
            
            st.markdown("---")
            st.markdown("### Itens do Pedido")
            
            itens = []
            for produto in Produto.listar():
                qtd = st.number_input(
                    f"{produto['nome']} - R$ {produto['preco']:.2f}",
                    min_value=0, max_value=10, value=0,
                    key=f"qtd_{produto['id']}"
                )
                if qtd > 0:
                    itens.append({
                        "nome": produto['nome'],
                        "quantidade": qtd,
                        "preco_unitario": produto['preco']
                    })
        
        observacoes = st.text_area("Observações", placeholder="Ex: sem cebola, extra picles")
        
        # Calcular total
        if itens:
            total = sum(i['quantidade'] * i['preco_unitario'] for i in itens)
            st.info(f"💰 **Total: R$ {total:.2f}**")
        
        submitted = st.form_submit_button("✅ Finalizar Pedido", type="primary", use_container_width=True)
        
        if submitted:
            # Validações
            erros = []
            if not nome:
                erros.append("Nome é obrigatório")
            if not documento:
                erros.append("Documento é obrigatório")
            if not itens:
                erros.append("Selecione pelo menos um item")
            
            if erros:
                for erro in erros:
                    st.error(erro)
            else:
                # Criar pedido
                total = sum(i['quantidade'] * i['preco_unitario'] for i in itens)
                
                pedido = {
                    "nome_cliente": nome,
                    "tipo_cliente": tipo,
                    "documento": documento,
                    "itens_pedido": itens,
                    "valor_total": total,
                    "categoria": categoria_valor,
                    "observacoes": observacoes
                }
                
                if tipo == "PJ" and 'ie' in locals() and ie:
                    pedido["inscricao_estadual"] = ie
                
                # Salvar
                pedido_salvo = db.criar_pedido(pedido)
                
                if pedido_salvo:
                    st.success(f"✅ Pedido #{pedido_salvo['id']} recebido com sucesso!")
                    st.balloons()
                    
                    with st.expander("📋 Detalhes do Pedido", expanded=True):
                        st.write(f"**Cliente:** {pedido_salvo['nome_cliente']}")
                        st.write(f"**Total:** R$ {pedido_salvo['valor_total']:.2f}")
                        st.write("**Itens:**")
                        for item in pedido_salvo['itens_pedido']:
                            st.write(f"- {item['quantidade']}x {item['nome']}")
                        if observacoes:
                            st.write(f"**Obs:** {observacoes}")
                else:
                    st.error("Erro ao salvar pedido. Tente novamente.")

def main(db):
    pagina_cliente(db)