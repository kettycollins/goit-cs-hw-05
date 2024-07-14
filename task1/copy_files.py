import asyncio
import aiofiles
import os
import logging
from pathlib import Path
import argparse

# Налаштування логування
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def copy_file(file_path, destination_dir):
    """
    Асинхронно копіює файл до відповідної папки у цільовій директорії на основі розширення файлу.
    """
    try:
        extension = file_path.suffix[1:]  # отримуємо розширення файлу
        dest_folder = destination_dir / extension  # створюємо шлях до цільової папки
        dest_folder.mkdir(parents=True, exist_ok=True)  # створюємо цільову папку, якщо не існує
        dest_file_path = dest_folder / file_path.name  # шлях до цільового файлу

        async with aiofiles.open(file_path, 'rb') as src_file:
            async with aiofiles.open(dest_file_path, 'wb') as dest_file:
                while True:
                    content = await src_file.read(1024)
                    if not content:
                        break
                    await dest_file.write(content)

        logger.info(f"Copied {file_path} to {dest_file_path}")
    except Exception as e:
        logger.error(f"Error copying {file_path}: {e}")

async def read_folder(source_dir, destination_dir):
    """
    Асинхронно читає всі файли у вихідній папці та її підпапках.
    """
    tasks = []
    for root, dirs, files in os.walk(source_dir):
        for file in files:
            file_path = Path(root) / file
            tasks.append(copy_file(file_path, destination_dir))
    
    await asyncio.gather(*tasks)

def get_destination_dir(root_dir, initial_destination):
    """
    Повертає шлях до цільової папки. Якщо папка існує, запитує користувача ввести нову назву.
    """
    destination_dir = root_dir / initial_destination
    while destination_dir.exists():
        logger.error(f"Цільова папка {destination_dir} вже існує.")
        new_dir_name = input("Введіть нову назву цільової папки або 'e' для виходу: ")
        if new_dir_name.lower() == 'e':
            print("Вихід з програми.")
            exit()
        destination_dir = root_dir / new_dir_name
    return destination_dir

def main():
    parser = argparse.ArgumentParser(description='Асинхронне сортування файлів на основі розширень.')
    parser.add_argument('--source', type=str, default='old', help='Вихідна папка (за замовчуванням "old")')
    parser.add_argument('--destination', type=str, default='new', help='Цільова папка (за замовчуванням "new")')
    
    args = parser.parse_args()

    # Визначення шляхів до вихідної та цільової папок
    root_dir = Path(__file__).parent
    source_dir = root_dir / args.source
    
    # Перевірка, чи існує вихідна папка
    if not source_dir.is_dir():
        logger.error(f"Вихідна папка {source_dir} не існує або не є папкою.")
        return
    
    # Отримання цільової папки, яка не існує
    destination_dir = get_destination_dir(root_dir, args.destination)
    
    # Створення цільової папки
    destination_dir.mkdir(parents=True, exist_ok=True)
    
    # Запуск асинхронної функції read_folder
    asyncio.run(read_folder(source_dir, destination_dir))

if __name__ == "__main__":
    main()
