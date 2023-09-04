#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import click
import sqlite3

@click.command()
@click.option('--file', help='Путь к файлу JSON для сохранения и чтения данных')
def main(file):
    if not file:
        data_file = click.prompt('Введите расположение файла:', type=str)
    else:
        data_file = file

    # Создаем базу данных SQLite3 и таблицы
    conn = sqlite3.connect('flight_data.db')
    cursor = conn.cursor()

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS flights (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        destination TEXT,
        flight_number INTEGER,
        type_plane TEXT
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS plane_types (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        type_plane TEXT
    )
    ''')

    conn.commit()
    conn.close()

    schema = {
        "type": "array",
        "items": {
            "type": "object",
            "properties": {
                "destination": {"type": "string"},
                "flight_number": {"type": "integer"},
                "type_plane": {"type": "string"}
            },
            "required": ["destination", "flight_number", "type_plane"]
        }
    }

    lst_planes = load_data(data_file, schema)

    while True:
        menu(lst_planes, schema)


def load_data(data_file, schema):
    conn = sqlite3.connect('flight_data.db')
    cursor = conn.cursor()

    cursor.execute('SELECT * FROM flights')
    data = cursor.fetchall()

    conn.close()

    return data


def save_data(data, schema):
    conn = sqlite3.connect('flight_data.db')
    cursor = conn.cursor()

    # Очищаем таблицы перед сохранением новых данных
    cursor.execute('DELETE FROM flights')
    cursor.execute('DELETE FROM plane_types')

    # Сохраняем данные в таблицы
    for plane in data:
        cursor.execute('INSERT INTO flights (destination, flight_number, type_plane) VALUES (?, ?, ?)',
                       (plane['destination'], plane['flight_number'], plane['type_plane']))

        cursor.execute('INSERT INTO plane_types (type_plane) VALUES (?)',
                       (plane['type_plane'],))

    conn.commit()
    conn.close()


def exit_to_program(data, schema):
    print('Всего доброго!')
    save_data(data, schema)
    exit(1)

def help_program():
    print("add - добавление рейса\n"
          "help - помощь по командам\n"
          "select \"пункт назначения\" - вывод самолетов летящих в п.н.\n"
          "display_plane - вывод всех самолетов\n"
          "exit - выход из программы")


def add_program(planes):
    plane = dict()
    plane["destination"] = click.prompt("Пункт назначения:")
    plane["flight_number"] = int(click.prompt("Номер рейса:", type=int))
    plane["type_plane"] = click.prompt("Тип самолета:")

    # Добавляем данные в список
    planes.append(plane)
    planes.sort(key=lambda key_plane: key_plane.get("flight_number"))

    # Добавляем данные в базу данных
    conn = sqlite3.connect('flight_data.db')
    cursor = conn.cursor()

    cursor.execute('INSERT INTO flights (destination, flight_number, type_plane) VALUES (?, ?, ?)',
                   (plane['destination'], plane['flight_number'], plane['type_plane']))

    cursor.execute('INSERT INTO plane_types (type_plane) VALUES (?)',
                   (plane['type_plane'],))

    conn.commit()
    conn.close()

    return planes


def select_program(planes, schema):
    lst = [plane['destination'] for plane in planes]
    point = click.prompt('Выберите нужное вам место:')
    print("Результаты поиска")
    if point in lst:
        print('Рейсы в эту точку')
        for plane in planes:
            if point == plane['destination']:
                print(f"{plane['flight_number']}........{plane['type_plane']}")
    else:
        print("Рейсов не найдено")


def error():
    print('Неверная команда')


def display_plane(staff):
    if staff:
        line = '+-{}-+-{}-+-{}-+-{}-+'.format(
            '-' * 4,
            '-' * 30,
            '-' * 20,
            '-' * 8
        )
        print(line)
        print(
            '| {:^4} | {:^30} | {:^20} | {:^8} |'.format(
                "№",
                "Направление",
                "Тип самолета",
                "Рейс"
            )
        )
        print(line)

        for idx, worker in enumerate(staff, 1):
            print(
                '| {:>4} | {:<30} | {:<20} | {:>8} |'.format(
                    idx,
                    worker['destination'],
                    worker['type_plane'],
                    worker['flight_number']
                )
            )
            print(line)

    else:
        print("Рейсов не найдено")


def menu(lst_plane, schema):
    command = click.prompt('Введите команду ("help" - руководство по командам):').lower()
    if command == 'exit':
        exit_to_program(lst_plane, schema)
    elif command == 'help':
        help_program()
    elif command == 'add':
        lst_plane = add_program(lst_plane)
    elif command.startswith('select'):
        select_program(lst_plane, schema)
    elif command == 'display_plane':
        display_plane(lst_plane)
    else:
        error()


if __name__ == '__main__':
    main()
