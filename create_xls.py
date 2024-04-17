import xlwt
import random

def crete_xls(big_data, statistic_skills, keyword):
    # Создание нового Excel документа
    workbook = xlwt.Workbook()

    # Добавление новых листов
    sheet = workbook.add_sheet("Sheet1")
    sheet2 = workbook.add_sheet("Sheet2")
    header_bold = xlwt.easyxf(
        "font: bold on; pattern: pattern solid, fore_colour gray25; align: wrap on"
    )
    col_width_1 = 256 * 20
    col_width_2 = 256 * 35
    sheet.row(4).height = 256 * 20
    headers_1 = [
        "Вакансия",
        "Компания",
        "Опубликовано",
        "Город",
        "Зарплата",
        "Адрес",
        "Стаж",
        "Статус",
        "Тип работы",
        "Тест",
        "Ссылка на вакансию ",
        "Ключевые навки",
        "Требования и пожелания",
    ]
    headers_2 = ["Навык", "Интенсивность"]

    # Запись данных о вакансиях
    row = 0
    col = 0
    for header in headers_1:
        sheet.write(row, col, str(header), header_bold)
        col += 1
    row = 1
    for data_string in big_data:
        col = 0
        for item in data_string:
            sheet.col(col).width = col_width_1 if col < 11 else col_width_2
            sheet.write(row, col, str(item))
            col += 1
        row += 1

    # Запись данных о ключевых навыках на 2-ю страницу
    col = 0
    row = 0
    sheet2.col(1).width = col_width_1
    sheet2.col(2).width = col_width_1
    for header in headers_2:
        sheet2.write(row, col, str(header), header_bold)
        col += 1
    row = 1
    for key, value in statistic_skills.items():
        col = 0
        sheet2.write(row, col, str(key))
        sheet2.write(row, col + 1, str(value))
        row += 1

    # Сохранение Excel файла
    num = random.randint(0, 1000)
    workbook.save(f"vacancies_{keyword}_{num}.xls")