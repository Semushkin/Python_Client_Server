'''
2. Задание на закрепление знаний по модулю json. Есть файл orders в формате JSON с информацией о заказах.
Написать скрипт, автоматизирующий его заполнение данными. Для этого:

    Создать функцию write_order_to_json(), в которую передается 5 параметров — товар (item), количество (quantity),
    цена (price), покупатель (buyer), дата (date). Функция должна предусматривать запись данных в виде словаря в файл
    orders.json. При записи данных указать величину отступа в 4 пробельных символа;
    Проверить работу программы через вызов функции write_order_to_json() с передачей в нее значений каждого параметра.
'''
import json


def write_order_to_json(item, quantity, price, buyer, date):
    """
    Функция записи данных в файл json
    """

    with open('orders.json', 'r', encoding='utf-8') as f_out:
        data = json.load(f_out)
        f_out.close()

    load_data = data['orders']
    load_data.append({'item': item, 'quantity': quantity, 'price': price, 'buyer': buyer, 'date': date})
    data['orders'] = load_data

    with open('orders.json', 'w', encoding='utf-8') as f_in:
        json.dump(data, f_in, indent=4)
        f_in.close()


write_order_to_json('Printer', '10', '600.00', 'Ivanov I.I.', '10.02.2022')
write_order_to_json('Monitor', '10', '5000.00', 'Petrov P.P.', '05.05.2022')
write_order_to_json('Laptop', '10', '15600.00', 'Sidorov S.S.', '17.08.2022')