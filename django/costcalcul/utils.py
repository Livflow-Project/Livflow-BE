import logging
from decimal import Decimal

logger = logging.getLogger(__name__)

def calculate_recipe_cost(ingredients, sales_price_per_item, production_quantity_per_batch):
    print(f"🛠️ [DEBUG] Received Ingredients: {ingredients}")  # ✅ 원가 계산에 들어오는 값 확인

    total_material_cost = Decimal("0")  
    ingredient_costs = []

    for ingredient in ingredients:
        unit_price = Decimal(str(ingredient.get('unit_price', "0")))  
        required_amount = Decimal(str(ingredient.get('quantity_used', "0")))

        print(f"🔹 Ingredient Name: {ingredient.get('ingredient_name', 'Unknown')}, "
              f"Unit Price: {unit_price}, Required Amount: {required_amount}")

        cost = round(required_amount * unit_price, 2)  
        print(f"🔹 Calculated Cost: {cost}")  # ✅ 개별 원가 확인

        ingredient_costs.append({
            "ingredient_name": ingredient.get('ingredient_name', 'Unknown'),
            "unit_price": float(unit_price),
            "required_amount": float(required_amount),
            "cost": float(cost)
        })
        total_material_cost += cost  

    print(f"🛠️ [DEBUG] Final Total Material Cost: {total_material_cost}")  # ✅ 최종 원가 확인

    safe_production_quantity = max(Decimal("1"), Decimal(str(production_quantity_per_batch)))
    cost_per_item = round(total_material_cost / safe_production_quantity, 2)  

    total_sales_revenue = Decimal(str(sales_price_per_item)) * safe_production_quantity
    material_ratio = round(total_material_cost / total_sales_revenue, 2) if total_sales_revenue != 0 else 0

    print(f"🛠️ [DEBUG] Cost Per Item: {cost_per_item}, Material Ratio: {material_ratio}")  # ✅ 최종 계산된 값 확인

    return {
        "ingredient_costs": ingredient_costs,  
        "total_material_cost": float(total_material_cost),  
        "cost_per_item": float(cost_per_item),  
        "material_ratio": float(material_ratio)
    }

