import re
import csv
from collections import defaultdict


# Функция для нормализации телефонов (ваша рабочая реализация)
def normalize_phone_number(phone_number):
    formatted_number = ''
    # Удаляем все нецифровые символы, кроме + в начале
    cleaned_number = re.sub(r'[^+\d]', '', phone_number)

    # Проверяем, начинается ли номер с + или 8
    if cleaned_number.startswith('+') or cleaned_number.startswith('8'):
        # Преобразуем номер в международный формат
        if cleaned_number.startswith('8'):
            cleaned_number = '+7' + cleaned_number[1:]
        elif not cleaned_number.startswith('+7'):
            cleaned_number = '+7' + cleaned_number

        # Разбиваем номер на части
        if len(cleaned_number) >= 12:
            country_code = cleaned_number[:2]
            area_code = cleaned_number[2:5]
            first_part = cleaned_number[5:8]
            second_part = cleaned_number[8:10]
            third_part = cleaned_number[10:12]
            additional_number = cleaned_number[12:] if len(cleaned_number) > 12 else ''

            # Формируем номер в нужном формате
            formatted_number = f"{country_code}({area_code}){first_part}-{second_part}-{third_part}"
            if additional_number:
                formatted_number += f" доб.{additional_number}"

            return formatted_number
        else:
            return formatted_number


# Функция для подготовки и формирования ключа объединения
def prepare_key(lastname, firstname, surname):
    """Формирует единый ключ для объединения записей"""
    # Стандартизируем и очищаем данные
    surname_clean = surname.strip().replace(',', '').title()
    lastname_clean = lastname.strip().replace(',', '').title()
    firstname_clean = firstname.strip().replace(',', '').title()

    # Ключевым признаком будет ФИО (фамилия и имя)
    return (lastname_clean, firstname_clean)


# Основная логика обработки файла
if __name__ == "__main__":
    try:
        # Чтение CSV-файла
        with open('phonebook_raw.csv', mode="r", encoding="utf-8") as infile:
            reader = csv.DictReader(infile)
            data = list(reader)

        # Словарь для хранения сгруппированных контактов
        grouped_contacts = defaultdict(lambda: {})

        for row in data:
            # Получаем ФИО и готовим ключ для объединения
            surname = row.get('surname', '')
            lastname = row.get('lastname', '')
            firstname = row.get('firstname', '')

            # Формируем ключ для объединения
            key = prepare_key(lastname, firstname, surname)

            # Ищем соответствующую группу
            group = grouped_contacts[key]

            # Если группа не существует, создаем её
            if not group:
                group.update({
                    'lastname': lastname,
                    'firstname': firstname,
                    'surname': surname,
                    'organization': '',
                    'position': '',
                    'phone': '',
                    'email': ''
                })

            # Обновляем информацию, выбирая наиболее полную
            for field in ['organization', 'position', 'email']:
                if row.get(field, '').strip():
                    group[field] = row.get(field, '').strip()

            # Дополнительно нормализуем телефонный номер
            phone_value = row.get('phone', '').strip()
            if phone_value:
                group['phone'] = normalize_phone_number(phone_value)

            # Если отчество доступно, обновляем его
            if surname:
                group['surname'] = surname

        # Преобразование собранных данных в итоговую форму
        processed_data = list(grouped_contacts.values())

        # Запись обработанных данных обратно в CSV
        with open('phonebook.csv', mode="w", encoding="utf-8", newline='') as outfile:
            fieldnames = ["lastname", "firstname", "surname", "organization", "position", "phone", "email"]
            writer = csv.DictWriter(outfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(processed_data)

    except Exception as e:
        print(f"Произошла ошибка: {e}")