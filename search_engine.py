from pywebio import input, output
from pywebio.input import select
import requests

import re
import time
from collections import Counter

from create_xls import crete_xls

from words import (
    WORDS,
    MISSED_VACANCY,
    VACANCY_URL,
    SEARCH_VACANCY_URL,
    EXPERIENCE,
    SCHEDULE,
    AREA,
)


def get_dict(filtered_skills: dict, statistic_skills: dict) -> dict:
    # Сложение значений одинаковых слов
    for key in statistic_skills:
        if key in filtered_skills:
            statistic_skills[key] = statistic_skills[key] + filtered_skills[key]
        else:
            statistic_skills[key] = statistic_skills[key]

    # Добавление новых ключевых слов
    for key in filtered_skills:
        if key not in statistic_skills:
            statistic_skills[key] = filtered_skills[key]
    return statistic_skills


def get_vacancy_data(vacancy_id, words: set, statistic_skills:dict) -> set:
    # Поиск данных о вакансии по id
    # Добавление статистики популярных навыков
    global MISSED_VACANCY
    url = VACANCY_URL + str(vacancy_id)
    headers = {
        "User-Agent": "Your User Agent",  # Replace with your User-Agent header
    }
    response = requests.get(url, headers=headers)
    vacancy_data = []
    if response.status_code == 200:
        data = response.json()
        skill_words = set(re.findall(r"\b[a-zA-Z]+\b", data.get("description")))
        fil_words = [i.capitalize() for i in skill_words if i.capitalize() in WORDS]
        data_key_skills = data.get("key_skills")
        key_skills = set(
            [
                i["name"].capitalize()
                for i in data_key_skills
                if data_key_skills
            ]
        )
        words = " ,".join(sorted(fil_words))
        skills = " ,".join(
            sorted(
                [i["name"] for i in data_key_skills if data_key_skills]
            )
        )

        filtered_skills = set(fil_words) | key_skills
        filtered_skills = dict(Counter(filtered_skills))
        statistic_skills = get_dict(filtered_skills, statistic_skills)

        name = data.get("name")
        employer_name = data.get("employer", {}).get("name")
        published_at = data.get("published_at").split("T")[0]
        area_name = (data.get("area", {}).get("name"))
        type_name = data.get("type", {}).get("name")
        address_raw = data.get("address", "")
        address_raw = address_raw.get("raw", "") if address_raw else area_name
        experience_name = data.get("experience", {}).get("name")
        schedule_name = data.get("schedule", {}).get("name")
        has_test = "Да" if data.get("has_test") else "Нет"
        alternate_url = data.get("alternate_url")
        salary = data.get("salary") if data.get("salary") else 0
        if salary:
            from_salary = salary.get("from") or 0
            to_salary = salary.get("to") or 0
            currency = data.get("salary").get("currency")
            salary = (f"От {from_salary} до {to_salary} {currency}")
        vacancy_data = [
            name,
            employer_name,
            published_at,
            area_name,
            salary,
            address_raw,
            experience_name,
            type_name,
            schedule_name,
            has_test,
            alternate_url,
            skills,
            words,
        ]
        return vacancy_data, statistic_skills
    else:
        print(f"Запрос на поиск вакансии не выполнен с кодом ответа: {response.status_code}")
        if vacancy_id not in MISSED_VACANCY:
            MISSED_VACANCY.append(vacancy_id)
        return vacancy_data, statistic_skills


def get_vacancies(keyword, exp, sched, area):
    global MISSED_VACANCY
    url = SEARCH_VACANCY_URL
    page = 0
    statistic_skills = {}
    all_vacances = 0
    big_data = []
    while all_vacances < 2000:
        time.sleep(1)
        params = {
            "text": keyword,
            "per_page": 50,
            "page": page,
            "search_field": "name",
        }
        if exp != "Empty":
            params["experience"] = exp
        if sched != "Empty":
            params["schedule"] = sched
        if area != "Empty":
            params["area"] = area
        
        headers = {
            "User-Agent": "Your User Agent",
        }

        response = requests.get(url, params=params, headers=headers)

        if response.status_code == 200:
            data = response.json()
            vacancies = data.get("items", [])
            num_vacancies = len(vacancies)
            all_vacances += num_vacancies
            words = set()

            if num_vacancies > 0:
                for i, vacancy in enumerate(vacancies):
                    # Получение информации о вакансии
                    vacancy_id = vacancy.get("id")
                    vacancy_title = vacancy.get("name")
                    skills, statistic_skills = get_vacancy_data(
                        vacancy_id, words, statistic_skills
                    )
                    if skills:
                        output.put_text(f"ID: {vacancy_id}")
                        output.put_text(f"Title: {vacancy_title}")
                        output.put_text("skills: ", skills)
                        big_data.append(skills)
                    output.put_text("")
                    if i < num_vacancies - 1:
                        output.put_text("---------")  # Разделительная линия
                page += 1
            else:
                output.put_text("No vacancies found.")
                break

        else:
            output.put_text(f"Запрос не выполнен с кодом ответа: {response.status_code}")
            break
    checked_vacancy = []
    output.put_text(f"Осталось непроверенных вакансий, {len(MISSED_VACANCY)}")
    while len(MISSED_VACANCY) != 0:
        time.sleep(5)
        for vacancy_id in MISSED_VACANCY:
            skills, statistic_skills = get_vacancy_data(
                vacancy_id, words, statistic_skills
            )
            if skills:
                big_data.append(skills)
                checked_vacancy.append(vacancy_id)
        output.put_text("---------")
        MISSED_VACANCY = [x for x in MISSED_VACANCY if x not in checked_vacancy]
        output.put_text(f"Осталось непроверенных вакансий, {len(MISSED_VACANCY)}")
        print(f"Осталось непроверенных вакансий, {len(MISSED_VACANCY)}")
        print(f"Всего вакансий, {len(big_data)}")

    statistic_skills = dict(
        sorted(statistic_skills.items(), key=lambda x: x[1], reverse=True)
    )
    crete_xls(big_data, statistic_skills, keyword)
    return None




def search_vacancies():
    experince =[i for i in EXPERIENCE.keys()]
    schedule =[i for i in SCHEDULE.keys()] 
    area =[i for i in AREA.keys()]
    keyword = input.input("Укажите название вакансии:", type=input.TEXT)
    exp = select("Выберите опыт работы", options=experince)
    sched = select("Выберите опыт работы", options=schedule)
    area = select("Выберите опыт работы", options=area)
    exp = EXPERIENCE[exp]
    sched =SCHEDULE[sched]
    area = AREA[area]
    output.clear()
    output.put_text("Поиск вакансий...")
    get_vacancies(keyword, exp, sched, area)


