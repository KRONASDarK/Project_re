import re
import csv
from collections import defaultdict


# Функция для нормализации телефонов (ваша оригинальная версия)
def normalize_phone_number(phone_number):
    formatted_number = ''
    cleaned_number = re.sub(r'[^+\d]', '', phone_number)

    if cleaned_number.startswith('+') or cleaned_number.startswith('8'):
        if cleaned_number.startswith('8'):
            cleaned_number = '+7' + cleaned_number[1:]
        elif not cleaned_number.startswith('+7'):
            cleaned_number = '+7' + cleaned_number

        if len(cleaned_number) >= 12:
            country_code = cleaned_number[:2]
            area_code = cleaned_number[2:5]
            first_part = cleaned_number[5:8]
            second_part = cleaned_number[8:10]
            third_part = cleaned_number[10:12]
            additional_number = cleaned_number[12:] if len(cleaned_number) > 12 else ''

            formatted_number = f"{country_code}({area_code}){first_part}-{second_part}-{third_part}"
            if additional_number:
                formatted_number += f" доб.{additional_number}"

            return formatted_number
        else:
            return formatted_number


# Функция для объединения дубликатов
def merge_duplicates(data):
    merged_data = {}

    for entry in data:
        key = (entry["surname"], entry["firstname"])  # Ключевое значение - фамилия и имя

        if key in merged_data:
            # Если такая запись уже существует, объединяем поля
            existing_entry = merged_data[key]

            # Обновление каждого поля, если оно пустое или отсутствует
            fields_to_merge = ["lastname", "organization", "position", "phone", "email"]
            for field in fields_to_merge:
                if not existing_entry[field]:
                    existing_entry[field] = entry[field]
                elif entry[field]:  # Проверка, есть ли новое значение
                    # Если поле имеет разные значения, объединить их
                    if isinstance(existing_entry[field], str) and isinstance(entry[field], str):
                        values = set([existing_entry[field].strip(), entry[field].strip()])
                        existing_entry[field] = ', '.join(values)
        else:
            # Иначе добавляем новую запись
            merged_data[key] = entry.copy()  # Копируем объект, чтобы избежать изменения исходных данных

    return list(merged_data.values())  # Возвращаем уникальные записи


# Основная логика обработки файла
if __name__ == "__main__":
    try:
        # Чтение CSV-файла
        with open('phonebook_raw.csv', mode="r", encoding="utf-8") as infile:
            reader = csv.DictReader(infile)
            data = list(reader)

        # Получаем ФИО и производим разбор
        full_name_finished = []
        for row in data:
            full_name = row['lastname'] + " " + row['firstname'] + " " + row['surname']
            full_name = " ".join(full_name.split())
            full_name_finished.append(full_name)

        # Новый список для хранения обработанных данных
        new_data = []

        for row, fnf in zip(data, full_name_finished):
            surname, firstname, lastname = '', '', ''

            # Разделение ФИО на составляющие
            parts = fnf.split(maxsplit=2)
            if len(parts) >= 1:
                surname = parts[0]
            if len(parts) >= 2:
                firstname = parts[1]
            if len(parts) >= 3:
                lastname = parts[2]

            # Заполняем оставшиеся поля
            organization = row.get('organization', '')
            position = row.get('position', '')
            phone = normalize_phone_number(row.get('phone'))
            email = row.get('email', '')

            # Сборка итоговых данных
            record = {
                'surname': surname,
                'firstname': firstname,
                'lastname': lastname,  # сюда кладём отчество
                'organization': organization,
                'position': position,
                'phone': phone,
                'email': email
            }

            # Добавляем обработанную запись в итоговый список
            new_data.append(record)

            # Удаление дубликатов путем слияния данных
            unique_records = merge_duplicates(new_data)

        # Запись обработанных данных обратно в CSV
        with open('phonebook.csv', mode="w", encoding="utf-8", newline='') as outfile:
            fieldnames = ["surname", "firstname", "lastname", "organization", "position", "phone", "email"]
            writer = csv.DictWriter(outfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(unique_records)

    except Exception as e:
        print(f"Произошла ошибка: {e}")