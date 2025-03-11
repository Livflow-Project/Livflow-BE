import logging
from decimal import Decimal, InvalidOperation
from .models import Recipe  # ✅ 기존 DB 값 가져오기 위해 추가

logger = logging.getLogger(__name__)

def calculate_recipe_cost(ingredients, sales_price_per_item, production_quantity_per_batch, recipe_id=None):
    print(f"🛠️ [DEBUG] Received Ingredients: {ingredients}")  # ✅ 원가 계산에 들어오는 값 확인

    # ✅ 기존 DB 값 유지
    if recipe_id:
        try:
            existing_recipe = Recipe.objects.get(id=recipe_id)
            sales_price_per_item = sales_price_per_item or existing_recipe.sales_price_per_item
            production_quantity_per_batch = production_quantity_per_batch or existing_recipe.production_quantity_per_batch
        except Recipe.DoesNotExist:
            pass  

    # ✅ Decimal 변환 및 예외 처리 (InvalidOperation 방지)
    try:
        sales_price = Decimal(str(sales_price_per_item or "0"))  
        production_quantity = Decimal(str(production_quantity_per_batch or "1"))
    except InvalidOperation:
        raise ValueError("🚨 판매 가격 또는 생산량이 올바른 숫자가 아닙니다!")

    total_material_cost = Decimal("0")
    ingredient_costs = []

    for ingredient in ingredients:
        try:
            quantity_used = Decimal(str(ingredient.get("quantity_used", "0")))
            unit_price = Decimal(str(ingredient.get("unit_price", "0"))) if ingredient.get("unit_price") is not None else Decimal("0")
        except InvalidOperation:
            raise ValueError(f"🚨 재료 {ingredient}에 잘못된 값이 포함됨!")

        cost = round(quantity_used * unit_price, 2)
        ingredient_costs.append({
            "ingredient_name": ingredient.get("ingredient_name", "Unknown"),
            "unit_price": float(unit_price),
            "required_amount": float(quantity_used),
            "cost": float(cost)
        })
        total_material_cost += cost

    if production_quantity == 0:
        raise ValueError("🚨 생산량은 0이 될 수 없습니다!")

    cost_per_item = round(total_material_cost / production_quantity, 2)

    total_sales_revenue = sales_price * production_quantity
    material_ratio = round(total_material_cost / total_sales_revenue, 2) if total_sales_revenue != 0 else 0  

    print(f"🛠️ [DEBUG] Cost Per Item: {cost_per_item}, Material Ratio: {material_ratio}")

    return {
        "ingredient_costs": ingredient_costs,
        "total_material_cost": float(total_material_cost),
        "cost_per_item": float(cost_per_item),
        "material_ratio": float(material_ratio)
    }

