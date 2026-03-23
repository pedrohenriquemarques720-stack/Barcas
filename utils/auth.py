import streamlit as st
import hmac

def verificar_admin() -> bool:
    """Verifica se admin está autenticado"""
    return st.session_state.get('admin_autenticado', False)

def fazer_login(senha: str, senha_correta: str) -> bool:
    """Realiza login do admin"""
    if hmac.compare_digest(senha, senha_correta):
        st.session_state.admin_autenticado = True
        return True
    return False

def fazer_logout():
    """Realiza logout do admin"""
    st.session_state.admin_autenticado = False
    st.rerun()

def mostrar_login(senha_correta: str):
    """Mostra formulário de login"""
    with st.form("login_form"):
        senha = st.text_input("Senha do Administrador", type="password")
        submitted = st.form_submit_button("Entrar")
        
        if submitted:
            if fazer_login(senha, senha_correta):
                st.success("Login realizado com sucesso!")
                st.rerun()
            else:
                st.error("Senha incorreta!")