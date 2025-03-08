import logging
from decimal import Decimal

logger = logging.getLogger(__name__)

def calculate_recipe_cost(ingredients, sales_price_per_item, production_quantity_per_batch):
    total_material_cost = Decimal("0")  
    ingredient_costs = []

    for ingredient in ingredients:
        unit_price = Decimal(str(ingredient.get('unit_price', "0")))  # ✅ KeyError 방지 + Decimal 변환
        required_amount = Decimal(str(ingredient.get('quantity_used', "0")))

        # ✅ unit_price와 required_amount의 값이 정확한지 디버깅 로그 추가
        logger.debug(f"[DEBUG] Ingredient: {ingredient.get('ingredient_name', 'Unknown')}, "
                     f"Unit Price: {unit_price}, Required Amount: {required_amount}")

        cost = round(required_amount * unit_price, 2)  
        ingredient_costs.append({
            "ingredient_name": ingredient.get('ingredient_name', 'Unknown'),
            "unit_price": float(unit_price),
            "required_amount": float(required_amount),
            "cost": float(cost)
        })
        total_material_cost += cost  

    # ✅ 총 원가 로그 추가
    logger.debug(f"[DEBUG] Total Material Cost: {total_material_cost}")  

    safe_production_quantity = max(Decimal("1"), Decimal(str(production_quantity_per_batch)))
    cost_per_item = round(total_material_cost / safe_production_quantity, 2)  

    total_sales_revenue = Decimal(str(sales_price_per_item)) * safe_production_quantity
    material_ratio = round(total_material_cost / total_sales_revenue, 2) if total_sales_revenue != 0 else 0

    # ✅ 최종 계산된 값 로그 추가
    logger.debug(f"[DEBUG] Cost Per Item: {cost_per_item}, Material Ratio: {material_ratio}")

    return {
        "ingredient_costs": ingredient_costs,  
        "total_material_cost": float(total_material_cost),  
        "cost_per_item": float(cost_per_item),  
        "material_ratio": float(material_ratio)
    }
