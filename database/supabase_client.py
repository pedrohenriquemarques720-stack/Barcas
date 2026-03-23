import streamlit as st
import pandas as pd
from datetime import datetime
from typing import List, Dict, Optional
import json

class SupabaseClient:
    def __init__(self, url: str, key: str):
        """Inicializa conexão com Supabase"""
        try:
            from supabase import create_client
            self.client = create_client(url, key)
            self.conectado = True
        except Exception as e:
            st.error(f"Erro ao conectar Supabase: {e}")
            self.client = None
            self.conectado = False
    
    def criar_pedido(self, pedido: Dict) -> Optional[Dict]:
        """Cria um novo pedido"""
        try:
            if not self.conectado:
                return None
            
            pedido['data_hora'] = datetime.now().isoformat()
            pedido['status'] = 'Pendente'
            
            # Converte itens_pedido para string JSON
            if isinstance(pedido.get('itens_pedido'), list):
                pedido['itens_pedido'] = json.dumps(pedido['itens_pedido'])
            
            response = self.client.table('pedidos').insert(pedido).execute()
            if response.data:
                # Converte de volta para lista
                if 'itens_pedido' in response.data[0]:
                    response.data[0]['itens_pedido'] = json.loads(response.data[0]['itens_pedido'])
                return response.data[0]
            return None
        except Exception as e:
            st.error(f"Erro ao criar pedido: {e}")
            return None
    
    def listar_pedidos(self, status: Optional[str] = None) -> List[Dict]:
        """Lista pedidos"""
        try:
            if not self.conectado:
                return []
            
            query = self.client.table('pedidos').select('*')
            if status:
                query = query.eq('status', status)
            
            response = query.order('data_hora', desc=True).execute()
            
            # Converte itens_pedido de volta para lista
            for pedido in response.data:
                if 'itens_pedido' in pedido and isinstance(pedido['itens_pedido'], str):
                    pedido['itens_pedido'] = json.loads(pedido['itens_pedido'])
            
            return response.data
        except Exception as e:
            st.error(f"Erro ao listar pedidos: {e}")
            return []
    
    def atualizar_status(self, pedido_id: int, novo_status: str) -> bool:
        """Atualiza status do pedido"""
        try:
            if not self.conectado:
                return False
            
            response = self.client.table('pedidos')\
                .update({'status': novo_status})\
                .eq('id', pedido_id)\
                .execute()
            return len(response.data) > 0
        except Exception as e:
            st.error(f"Erro ao atualizar status: {e}")
            return False
    
    def obter_estatisticas(self) -> Dict:
        """Obtém estatísticas"""
        try:
            pedidos = self.listar_pedidos()
            if not pedidos:
                return {
                    'faturamento_total': 0,
                    'total_pedidos': 0,
                    'pedidos_pf': 0,
                    'pedidos_pj': 0,
                    'status_counts': {}
                }
            
            df = pd.DataFrame(pedidos)
            df['valor_total'] = pd.to_numeric(df['valor_total'])
            
            return {
                'faturamento_total': df['valor_total'].sum(),
                'total_pedidos': len(df),
                'pedidos_pf': len(df[df['tipo_cliente'] == 'PF']),
                'pedidos_pj': len(df[df['tipo_cliente'] == 'PJ']),
                'status_counts': df['status'].value_counts().to_dict()
            }
        except Exception as e:
            st.error(f"Erro ao obter estatísticas: {e}")
            return {}