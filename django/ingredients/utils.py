# ingredients/utils.py

def calculate_unit_price(purchase_price, purchase_quantity):
    """
    구매가를 용량으로 나누어 단가를 계산하는 함수.
    """
    if purchase_quantity == 0:
        return 0  # 용량이 0인 경우를 대비해 0을 반환
    return round(purchase_price / purchase_quantity, 2)  # 소수점 둘째 자리까지 반올림
