from typing import List, Dict, Optional

class Produto:
    """Catálogo de produtos"""
    PRODUTOS = [
        {"id": 1, "nome": "Barca P", "preco": 25.00, "descricao": "Serve 2-3 pessoas"},
        {"id": 2, "nome": "Barca M", "preco": 35.00, "descricao": "Serve 4-5 pessoas"},
        {"id": 3, "nome": "Barca G", "preco": 45.00, "descricao": "Serve 6-8 pessoas"},
        {"id": 4, "nome": "Barca Especial", "preco": 55.00, "descricao": "Com complementos especiais"}
    ]
    
    @classmethod
    def listar(cls):
        return cls.PRODUTOS
    
    @classmethod
    def obter(cls, produto_id: int):
        for p in cls.PRODUTOS:
            if p["id"] == produto_id:
                return p
        return None

class Pedido:
    """Classe para gerenciar pedidos"""
    
    def __init__(self, dados: Dict):
        self.id = dados.get('id')
        self.data_hora = dados.get('data_hora')
        self.nome_cliente = dados.get('nome_cliente')
        self.tipo_cliente = dados.get('tipo_cliente')
        self.documento = dados.get('documento')
        self.itens_pedido = dados.get('itens_pedido', [])
        self.valor_total = dados.get('valor_total', 0)
        self.status = dados.get('status', 'Pendente')
        self.categoria = dados.get('categoria')
        self.observacoes = dados.get('observacoes', '')
    
    def to_dict(self) -> Dict:
        return {
            'id': self.id,
            'data_hora': self.data_hora,
            'nome_cliente': self.nome_cliente,
            'tipo_cliente': self.tipo_cliente,
            'documento': self.documento,
            'itens_pedido': self.itens_pedido,
            'valor_total': self.valor_total,
            'status': self.status,
            'categoria': self.categoria,
            'observacoes': self.observacoes
        }