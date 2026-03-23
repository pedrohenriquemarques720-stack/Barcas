import streamlit as st
import os
from dotenv import load_dotenv
from database.supabase_client import SupabaseClient
import pages.cliente as cliente
import pages.admin as admin

# Carregar configurações
load_dotenv()

# Configurar página
st.set_page_config(
    page_title="Barcas de Maionese - Sistema de Pedidos",
    page_icon="🍽️",
    layout="wide"
)

# CSS global
st.markdown("""
<style>
    .stButton > button {
        background-color: #FF6B6B;
        color: white;
        font-weight: bold;
        border-radius: 8px;
        border: none;
        padding: 0.5rem 1rem;
        transition: all 0.3s;
    }
    .stButton > button:hover {
        background-color: #FF5252;
        transform: translateY(-2px);
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    }
    .main-header {
        background: linear-gradient(135deg, #FF6B6B 0%, #FF8E8E 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
    }
</style>
""", unsafe_allow_html=True)

def main():
    """Função principal"""
    
    # Verificar conexão Supabase
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_KEY")
    
    if not supabase_url or not supabase_key:
        st.error("""
        ⚠️ **Configuração necessária**
        
        Crie um arquivo `.env` na raiz do projeto com: