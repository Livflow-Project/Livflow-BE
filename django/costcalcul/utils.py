# costcalcul/utils.py

def calculate_recipe_cost(ingredients, sales_price_per_item, production_quantity_per_batch):
    """
    레시피 비용 계산 함수
    - ingredients: 단가 포함한 재료 정보 리스트
    - sales_price_per_item: 개당 판매 가격
    - production_quantity_per_batch: 한 배합당 생산 개수
    """
    total_material_cost = 0  # 총재료원가
    ingredient_costs = []

    for ingredient in ingredients:
        unit_price = ingredient['unit_price']  # ✅ ingredients/utils.py의 단가 활용
        required_amount = ingredient['quantity_used']  # ✅ 프론트엔드 명칭과 맞춤

        cost = round(required_amount * unit_price, 2)  # 원가 계산
        ingredient_costs.append({
            "ingredient_name": ingredient['ingredient_name'],
            "unit_price": unit_price,
            "required_amount": required_amount,  # ✅ 프론트엔드 명칭과 일치
            "cost": cost
        })
        total_material_cost += cost  # 총 원가 누적

    # ✅ 0으로 나누는 오류 방지
    safe_production_quantity = max(1, production_quantity_per_batch)
    cost_per_item = round(total_material_cost / safe_production_quantity, 2)  # 개당 원가 계산

    # ✅ 총 판매 수익 계산 (0 방지)
    total_sales_revenue = sales_price_per_item * safe_production_quantity
    material_ratio = round(total_material_cost / total_sales_revenue, 2) if total_sales_revenue != 0 else 0

    return {
        "ingredient_costs": ingredient_costs,  # ✅ 프론트엔드 요구사항과 맞춤
        "total_material_cost": total_material_cost,  
        "cost_per_item": cost_per_item,  
        "material_ratio": material_ratio
    }
