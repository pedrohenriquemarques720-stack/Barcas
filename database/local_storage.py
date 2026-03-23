import json
import os
import pandas as pd
from datetime import datetime
from typing import List, Dict, Any

class LocalStorage:
    def __init__(self, data_file="data/local_db.json"):
        self.data_file = data_file
        self._ensure_data_file()
    
    def _ensure_data_file(self):
        """Create data file if it doesn't exist"""
        os.makedirs(os.path.dirname(self.data_file), exist_ok=True)
        if not os.path.exists(self.data_file):
            initial_data = {
                "orders": [],
                "customers": [],
                "products": [
                    {"id": 1, "name": "Barca P", "price": 25.00, "size": "P", "description": "Serve 2-3 pessoas"},
                    {"id": 2, "name": "Barca M", "price": 35.00, "size": "M", "description": "Serve 4-5 pessoas"},
                    {"id": 3, "name": "Barca G", "price": 45.00, "size": "G", "description": "Serve 6-8 pessoas"}
                ]
            }
            self._save_data(initial_data)
    
    def _load_data(self) -> Dict:
        with open(self.data_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def _save_data(self, data: Dict):
        with open(self.data_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    def get_products(self) -> List[Dict]:
        return self._load_data()["products"]
    
    def create_order(self, order: Dict) -> Dict:
        data = self._load_data()
        order["id"] = len(data["orders"]) + 1
        order["created_at"] = datetime.now().isoformat()
        order["status"] = "pending"
        data["orders"].append(order)
        self._save_data(data)
        return order
    
    def get_orders(self, status: str = None) -> List[Dict]:
        data = self._load_data()
        orders = data["orders"]
        if status:
            orders = [o for o in orders if o["status"] == status]
        return sorted(orders, key=lambda x: x["created_at"], reverse=True)
    
    def update_order_status(self, order_id: int, status: str) -> bool:
        data = self._load_data()
        for order in data["orders"]:
            if order["id"] == order_id:
                order["status"] = status
                self._save_data(data)
                return True
        return False
    
    def save_customer(self, customer: Dict) -> Dict:
        data = self._load_data()
        customer["id"] = len(data["customers"]) + 1
        data["customers"].append(customer)
        self._save_data(data)
        return customer
    
    def get_customers(self) -> List[Dict]:
        return self._load_data()["customers"]
    
    def get_customer_by_document(self, document: str) -> Dict:
        customers = self.get_customers()
        for customer in customers:
            if customer.get("document") == document:
                return customer
        return None