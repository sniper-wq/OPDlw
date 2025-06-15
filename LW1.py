import requests
from bs4 import BeautifulSoup

# Базовый URL раздела «Новости»
BASE_URL = "https://www.omgtu.ru"

def fetch_titles_from_page(page_number):
    """
    Делаёт HTTP-запрос к странице с номеров пагинации page_number
    и возвращает список заголовков (тексты всех <h3>).
    """
    if page_number == 1:
        url = BASE_URL
    else:
        url = f"{BASE_URL}?PAGEN_1={page_number}"

    response = requests.get(url)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")
    titles = []
    for h3 in soup.find_all("h3"):
        text = h3.get_text(strip=True)
        if text:
            titles.append(text)
    return titles

def fetch_all_news_titles():
    """
    Обходит страницы пагинации, начиная с 1, и собирает заголовки,
    пока на очередной странице находятся новые заголовки.
    """
    all_titles = []
    page = 1

    while True:
        titles = fetch_titles_from_page(page)
        # Если заголовков нет вовсе или мы попали на «лишнюю» страницу – выходим
        if not titles:
            break

        new_only = [t for t in titles if t not in all_titles]
        if not new_only:
            break

        all_titles.extend(new_only)
        print(f"Страница {page}: найдено {len(new_only)} новых заголовков.")
        page += 1

    return all_titles

def save_titles_to_file(titles, filename):
    """
    Записывает все заголовки в текстовый файл, по одному на строку.
    """
    with open(filename, "w", encoding="utf-8") as f:
        for title in titles:
            f.write(title + "\n")

def main():
    print("Собираем все заголовки новостей с omgtu.ru …")
    titles = fetch_all_news_titles()

    if not titles:
        print("Не удалось найти ни одного заголовка.")
        return

    output_file = "omgtu_all_news_titles.txt"
    save_titles_to_file(titles, output_file)
    print(f"\nВсего заголовков: {len(titles)}. Записаны в файл «{output_file}».")

main()