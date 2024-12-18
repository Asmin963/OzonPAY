from api import OzonPAY

PIN = 'тут пинкод'

COOKIE = 'тут для первого запуска нужно вписать строку куков из заголовков в девтулсе с любого запроса, чтоб скрипт засейвил их в файлик'
# COOKIE = {"__OBANK_refresh": ..., "__OBANK_session": ...} или два ключа из расширения в браузере

ozon = OzonPAY(PIN, COOKIE)

_sum = 100  # сумма заказа

# результирующая сумма заказа
order_sum = ozon.create_invoice(_sum)

if ozon.check_pay_by_sum(order_sum):
    print(f"оплата на {_sum} найдена")
else:
    print("Денег нет :sigmaface:")
