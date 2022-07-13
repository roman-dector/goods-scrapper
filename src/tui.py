import asyncio

from main_funcs import (
    add_new_products_for_monitoring,
    save_prices_to_db,
    create_result_execel_sheet,
)

from config import ROOT_DIR


def print_menu():
    print('Выберите действие:')
    print('1. добавить товары для мониторинга цен')
    print('2. спарсить актуальные цены')
    print('3. создать excel c ценами\n')


def get_action():
    print_menu()
    action = input('Введите номер действия: ')

    if action not in ('1', '2', '3'):
        get_action()

    return int(action)


def execute_action():
        action = get_action()

        match action:
            case 1:
                path = input('Укажите путь к файлу: ')
                print(path)
                if not path:
                    path = ROOT_DIR + 'src/assets/test_product_links.xlsx'
                print(path)
                mode = input('Если нужно удалить уже существующие товары, введите "r": ')
                add_new_products_for_monitoring(path, mode)

            case 2:
                print("Парсинг начат")
                asyncio.run(save_prices_to_db())
                print('Данные сохранены\n')

            case 3:
                print('Файл создается')
                asyncio.run(create_result_execel_sheet())
                print('Файл готов\n')

            case _:
                pass 


def run_tui():
    while True:
        execute_action()


if __name__ == '__main__':
    run_tui()
