from search_engine import search_vacancies
from pywebio import start_server

if __name__ == '__main__':
    start_server(search_vacancies, port=8080)