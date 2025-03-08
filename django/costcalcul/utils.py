from decimal import Decimal

def calculate_recipe_cost(ingredients, sales_price_per_item, production_quantity_per_batch):
    """
    레시피 비용 계산 함수
    - ingredients: 단가 포함한 재료 정보 리스트
    - sales_price_per_item: 개당 판매 가격
    - production_quantity_per_batch: 한 배합당 생산 개수
    """
    total_material_cost = Decimal('0')  # ✅ Decimal 타입으로 설정
    ingredient_costs = []

    for ingredient in ingredients:
        unit_price = Decimal(str(ingredient['unit_price']))  # ✅ Decimal로 변환
        required_amount = Decimal(str(ingredient['quantity_used']))  # ✅ Decimal로 변환

        cost = round(required_amount * unit_price, 2)  # ✅ Decimal 간 연산
        ingredient_costs.append({
            "ingredient_name": ingredient['ingredient_name'],
            "unit_price": unit_price,
            "required_amount": required_amount,
            "cost": cost
        })
        total_material_cost += cost  # ✅ Decimal 합산

    # ✅ 0으로 나누는 오류 방지
    safe_production_quantity = max(Decimal('1'), Decimal(str(production_quantity_per_batch)))
    cost_per_item = round(total_material_cost / safe_production_quantity, 2)  # ✅ Decimal 연산

    # ✅ 총 판매 수익 계산 (0 방지)
    total_sales_revenue = Decimal(str(sales_price_per_item)) * safe_production_quantity
    material_ratio = round(total_material_cost / total_sales_revenue, 2) if total_sales_revenue != 0 else Decimal('0')

    return {
        "ingredient_costs": ingredient_costs,
        "total_material_cost": total_material_cost,
        "cost_per_item": cost_per_item,
        "material_ratio": material_ratio
    }
