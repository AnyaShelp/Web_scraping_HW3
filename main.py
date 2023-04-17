import json
import requests
from bs4 import BeautifulSoup
import unicodedata

url = 'https://spb.hh.ru/search/vacancy?text=python&area=1&area=2'
headers = {'Accept': '*/*', 'User-Agent': 'Mozilla'}

symbol_list = []
link_list = []
link_sorted = []
salary_list = []
company_vacancy_name_list = []
city_list = []
information_list = []


def get_link():
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, 'lxml')
    vacancies = soup.find_all('a', class_='serp-item__title')
    for vacancy in vacancies:
        link = vacancy['href']
        link_list.append(link)
        response_link = requests.get(link, headers=headers)
        link_parsed = BeautifulSoup(response_link.text, 'lxml')
        descriptions = link_parsed.find('div', {'data-qa': 'vacancy-description'})
        if descriptions.find('Django' or 'Flask') in descriptions:
            return link_sorted


def get_salary():
    for link in link_sorted:
        salary_link = requests.get(link, headers=headers)
        salary_parsed = BeautifulSoup(salary_link.text, 'lxml')
        salary = salary_parsed.find('span', class_="bloko-header-section-2 bloko-header-section-2_lite")
        if not salary:
            continue
        salary_text = salary.text
        salary = unicodedata.normalize('NFKD', salary_text)
        salary_list.append(salary)
    return salary_list


def get_company_vacancy_name():
    for link in link_sorted:
        company_vacancy_name_link = requests.get(link, headers=headers)
        company_vacancy_name_parsed = BeautifulSoup(company_vacancy_name_link.text, 'lxml')
        company_vacancy_name_2 = company_vacancy_name_parsed.find('a', class_="bloko-link bloko-link_kind-tertiary")
        if not company_vacancy_name_2:
            continue
        company_vacancy_name = company_vacancy_name_2['href']
        company_vacancy_name_href = f'https://spb.hh.ru{company_vacancy_name}'
        company_vacancy_name_link_2 = requests.get(company_vacancy_name_href, headers=headers)
        company_vacancy_name_parsed_2 = BeautifulSoup(company_vacancy_name_link_2.text, 'lxml')
        company_vacancy_name_2 = company_vacancy_name_parsed_2.find('span', class_="company-header-title-name")
        if not company_vacancy_name_2:
            continue
        company_name_2_text = company_vacancy_name_2.text
        company_name_normalized = unicodedata.normalize('NFKD', company_name_2_text)
        company_vacancy_name.append(company_name_normalized)
    return company_vacancy_name_list


def get_city():
    for link in link_sorted:
        city_link = requests.get(link, headers=headers)
        city_parsed = BeautifulSoup(city_link.text, 'lxml')
        city = city_parsed.find('p', {'data-qa': 'vacancy-view-location'})
        if not city:
            city = city_parsed.find('span', {'data-qa': 'vacancy-view-raw-address'})
            if not city:
                continue
        city_text = city.text
        city_list.append(city_text)
    return city_list


def get_information(links_, salaries, companies_names, locations):
    all_information = zip(links_, salaries, companies_names, locations)
    for link, salary, company_vacancy_name, city in all_information:
        information_dict = {'link': link, 'salary': salary, 'company_name': company_vacancy_name, 'location': city}
        information_list.append(information_dict)
    return information_list


get_link()
get_salary()
get_company_vacancy_name()
get_city()
get_information(link_sorted, salary_list, company_vacancy_name_list, city_list)

with open('information.json', 'w', encoding='utf-8') as data:
    json.dump(information_list, data, indent=2, ensure_ascii=False)
