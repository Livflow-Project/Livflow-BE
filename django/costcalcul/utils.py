from decimal import Decimal

def calculate_recipe_cost(ingredients, sales_price_per_item, production_quantity_per_batch):
    """
    레시피 비용 계산 함수
    - ingredients: 단가 포함한 재료 정보 리스트
    - sales_price_per_item: 개당 판매 가격
    - production_quantity_per_batch: 한 배합당 생산 개수
    """
    total_material_cost = Decimal("0")  
    ingredient_costs = []

    for ingredient in ingredients:
        unit_price = Decimal(str(ingredient.get('unit_price', 0)))  # ✅ KeyError 방지
        required_amount = Decimal(str(ingredient.get('quantity_used', 0)))  

        cost = round(required_amount * unit_price, 2)  
        ingredient_costs.append({
            "ingredient_name": ingredient.get('ingredient_name', 'Unknown'),
            "unit_price": float(unit_price),
            "required_amount": float(required_amount),
            "cost": float(cost)
        })
        total_material_cost += cost  

    safe_production_quantity = max(Decimal("1"), Decimal(str(production_quantity_per_batch)))
    cost_per_item = round(total_material_cost / safe_production_quantity, 2)  

    total_sales_revenue = Decimal(str(sales_price_per_item)) * safe_production_quantity
    material_ratio = round(total_material_cost / total_sales_revenue, 2) if total_sales_revenue != 0 else 0

    return {
        "ingredient_costs": ingredient_costs,  
        "total_material_cost": float(total_material_cost),  
        "cost_per_item": float(cost_per_item),  
        "material_ratio": float(material_ratio)
    }
