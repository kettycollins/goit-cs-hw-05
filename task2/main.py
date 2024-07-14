import requests
from collections import defaultdict
import matplotlib.pyplot as plt
from bs4 import BeautifulSoup
import concurrent.futures
import re

def fetch_text(url):
    """
    Завантажує текст із заданої URL-адреси, вилучаючи HTML-теги.
    """
    try:
        response = requests.get(url)
        response.raise_for_status()  # Перевірка на помилки HTTP
        soup = BeautifulSoup(response.text, 'html.parser')
        # Вилучення тексту статті без HTML-тегів і атрибутів
        text = soup.get_text()
        return text
    except requests.RequestException as e:
        print(f"Проблема з відкриттям {url}: {e}")
        return None

def map_function(text):
    """
    Розбиває текст на слова і повертає список пар (слово, 1).
    """
    words = re.findall(r'\b\w+\b', text.lower())
    return [(word, 1) for word in words]

def shuffle_function(mapped_values):
    """
    Групує значення за ключами.
    """
    shuffled = defaultdict(list)
    for key, value in mapped_values:
        shuffled[key].append(value)
    return shuffled.items()

def reduce_function(shuffled_values):
    """
    Сумує значення для кожного ключа.
    """
    reduced = {}
    for key, values in shuffled_values:
        reduced[key] = sum(values)
    return reduced

def map_reduce(text):
    """
    Виконує MapReduce на заданому тексті.
    """
    # Крок 1: Мапінг
    with concurrent.futures.ThreadPoolExecutor() as executor:
        mapped_values = list(executor.map(map_function, [text]))[0]

    # Крок 2: Shuffle
    shuffled_values = shuffle_function(mapped_values)

    # Крок 3: Редукція
    reduced_values = reduce_function(shuffled_values)

    return reduced_values

def visualize_top_words(word_counts, top_n=10):
    """
    Візуалізує топ-слова за частотою використання.
    """
    sorted_words = sorted(word_counts.items(), key=lambda x: x[1], reverse=True)
    top_words = []
    count = 0
    for word, freq in sorted_words:
        if word.isalpha():  # Враховуємо лише слова, що складаються лише з літер
            top_words.append((word, freq))
            count += 1
        if count >= top_n:
            break

    words, counts = zip(*top_words)

    plt.figure(figsize=(10, 6))
    plt.bar(words, counts)
    plt.xlabel('Words')
    plt.ylabel('Counts')
    plt.title(f'Top {top_n} Words by Frequency')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()

    # Виведення топ-слів у текстовому форматі
    print(f"\nТоп-{top_n} найвикористовуваних слів:")
    for word, count in top_words:
        print(f"{word}: {count}")

def main():
    while True:
        url = input("Введіть URL для аналізу або 'e' для виходу: ")
        if url.lower() == 'e':
            print("Вихід з програми.")
            break

        text = fetch_text(url)
        if text is None:
            continue

        result = map_reduce(text)

        while True:
            try:
                top_n = input("Введіть кількість найпоширеніших слів для виведення: ")
                if top_n.lower() == 'e':
                    print("Вихід з програми.")
                    exit()
                top_n = int(top_n)
                if top_n <= 0:
                    raise ValueError("Кількість слів має бути більше 0")
                if top_n > len(result):
                    raise ValueError(f"Недостатньо слів для виведення {top_n} найпоширеніших")
                break
            except ValueError as e:
                print(f"Помилка: {e}")
                if isinstance(e, ValueError) and 'invalid literal' in str(e):
                    print("Будь ласка, уведіть ціле число.")
                elif isinstance(e, ValueError) and 'not integer' in str(e):
                    print("Ви ввели не ціле число, уведіть ціле число.")

        visualize_top_words(result, top_n)

if __name__ == "__main__":
    main()
