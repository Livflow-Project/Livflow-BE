# utils.py

def calculate_unit_price(purchase_price, purchase_quantity):
    """
    구매가를 용량으로 나누어 단가를 계산하는 함수.
    """
    if purchase_quantity == 0:
        return 0  # 용량이 0인 경우를 대비해 0을 반환
    return round(purchase_price / purchase_quantity, 2)  # 소수점 둘째 자리까지 반올림

def calculate_recipe_cost(ingredients, sales_price_per_item, production_quantity_per_batch):
    """
    레시피 비용 계산 함수:
    - ingredients: 각 재료의 정보 (단가 포함)
    - sales_price_per_item: 메뉴의 개당 판매가
    - production_quantity_per_batch: 1배합 생산수량
    """
    total_material_cost = 0  # 총재료원가
    ingredient_costs = []

    for ingredient in ingredients:
        unit_price = ingredient['unit_price']  # 재료 단가
        quantity_used = ingredient['quantity_used']  # 사용량

        # 원가 = 사용량 * 단가
        cost = round(quantity_used * unit_price, 2)

        # 재료 원가 리스트에 저장
        ingredient_costs.append({
            "ingredient_name": ingredient['name'],
            "unit_price": unit_price,
            "quantity_used": quantity_used,
            "cost": cost
        })

        # 총재료원가에 원가 추가
        total_material_cost += cost

    # 개당 재료 원가 = 총재료원가 / 1배합 생산수량
    cost_per_item = round(total_material_cost / production_quantity_per_batch, 2)

    # 재료비율 = 총재료원가 / (개당 판매가 * 1배합 생산수량)
    total_sales_revenue = sales_price_per_item * production_quantity_per_batch
    material_ratio = round(total_material_cost / total_sales_revenue, 2) if total_sales_revenue != 0 else 0

    # 원가율 계산 (각 재료의 원가 / 전체 원가합)
    for ingredient_cost in ingredient_costs:
        ingredient_cost['cost_ratio'] = round(ingredient_cost['cost'] / total_material_cost, 2) if total_material_cost != 0 else 0

    return {
        "ingredient_costs": ingredient_costs,  # 각 재료별 원가, 원가율
        "total_material_cost": total_material_cost,  # 총재료원가
        "cost_per_item": cost_per_item,  # 개당 재료 원가
        "material_ratio": material_ratio  # 재료비율
    }
