# GadgetResearcherBot  
Telegram bot for electronics price comparison  

---

## Описание проекта  
**GadgetResearcherBot** — это Telegram-бот, который помогает пользователям находить и сравнивать цены на электронику из шести популярных магазинов:  
- [BigGeek](https://biggeek.ru/)  
- [Nistone](https://nistone.ru/)  
- [Apple Market](https://apple-market.ru/)  
- [Apple i-точка](https://appl-i-tochka.ru/)  
- [Megafon](https://moscow.shop.megafon.ru/)  
- [Store 77](https://store77.net/)  

Бот позволяет пользователям:  
- Ввести название товара для поиска.  
- Выбрать магазин или провести поиск сразу по всем.  
- Сравнить результаты и выбрать наиболее выгодное предложение.  

---

## Функционал бота  

1. **Поиск товара**  
   - Пользователь вводит название товара, который хочет найти.  
   - Бот запускает парсинг данных с выбранных сайтов и извлекает информацию о названии и цене товаров.  

2. **Выбор формата отображения результатов**  
   - Пользователь может:  
     - Просмотреть полный список найденных товаров.  
     - Показать 5 самых дешевых товаров.  
     - Найти самый дешевый товар.  

3. **Повторный поиск**  
   - После выполнения запроса бот предлагает начать новый поиск или завершить сессию.  

---

## Используемые библиотеки  

Проект использует следующие библиотеки:  

- **`selenium`**: Для автоматизации взаимодействия с веб-сайтами.  
- **`undetected-chromedriver`**: Для обхода защит от ботов на сайтах.  
- **`python-telegram-bot`**: Для создания Telegram-бота и взаимодействия с API Telegram.  
- **`aiogram`**: Для асинхронного управления логикой Telegram-бота с использованием FSM.  
- **`setuptools`**: Для настройки и управления зависимостями проекта.  
- **`webdriver_manager`**: Для автоматической установки и управления веб-драйверами.  
- **`pytest`**: Для тестирования модулей и функций бота.  
- **`pytest-asyncio`**: Для создания и выполнения асинхронных тестов.  

---

## Сценарий взаимодействия с пользователем (UI)  

1. **Старт**  
   - Пользователь запускает бота.  
   - Бот отправляет приветственное сообщение с кратким описанием функционала.  

2. **Ввод названия товара**  
   - Бот запрашивает название товара, который пользователь хочет найти.  

3. **Выбор магазина**  
   - Пользователь выбирает один из шести магазинов или поиск сразу по всем.  

4. **Поиск товара**  
   - Бот извлекает данные с выбранных сайтов, используя парсинг.  

5. **Отображение результатов**  
   - Пользователь выбирает формат отображения:  
     - Полный список найденных товаров.  
     - Пять самых дешевых товаров.  
     - Самый дешевый товар.  

6. **Повторный поиск или завершение**  
   - Пользователь может начать новый поиск или завершить сеанс.  

---

## Структура проекта  

```plaintext
bot/
├── .venv/                     # Виртуальная среда для изоляции зависимостей
├── GadgetResearcher/          # Основная директория проекта
│   ├── __pycache__/           # Скомпилированные файлы Python
│   ├── .pytest_cache/         # Кэш файлов тестов
│   ├── .gitignore             # Настройки исключений для Git
│   ├── apple_i_tochka.py      # Парсер для сайта Apple i-точка
│   ├── apple_market.py        # Парсер для сайта Apple Market
│   ├── biggeek.py             # Парсер для сайта BigGeek
│   ├── LICENSE                # Лицензия проекта
│   ├── main.py                # Основной файл с логикой бота
│   ├── megafon.py             # Парсер для сайта Megafon
│   ├── nistone.py             # Парсер для сайта Nistone
│   ├── requirements.txt       # Файл с зависимостями проекта
│   ├── store77.py             # Парсер для сайта Store 77
└── __pycache__/               # Дополнительные скомпилированные файлы Python
```
---

## Роли и задачи  

### 1. Парсер (BigGeek, Nistone, Store 77)  
**Сухомлина Ксения** (tg: [@kejros](https://t.me/kejros))  
- Использовала **`selenium`** и **`undetected-chromedriver`** для извлечения данных с сайтов.  
- Разработала функции для получения информации о товарах (название, цена).  
- Настроила обработку исключений и логирование для повышения устойчивости работы.  

### 2. Парсер (Apple Market, Apple i-точка, Megafon)  
**Ленькова Ульяна** (tg: [@uliana_sof_25](https://t.me/uliana_sof_25))  
- Реализовала парсинг данных с сайтов с помощью **`selenium`** и **`webdriver_manager`**.  
- Настроила обработку данных для корректной интеграции с ботом.  
- Использовала **`undetected-chromedriver`** для обхода защит на сайтах.  
- Добавила обработку ошибок и контроль изменений структуры страниц сайтов.  

### 3. Разработчик Telegram-бота  
**Нефедов Дмитрий** (tg: [@nefedovdima](https://t.me/nefedovdima))  
- Разработал Telegram-бота с использованием **`aiogram`** и **`python-telegram-bot`**.  
- Реализовал сценарии взаимодействия с пользователем, включая FSM для управления состояниями.  
- Организовал логику получения данных от парсеров и их отображения в удобном формате.  
- Покрыл функционал бота тестами с помощью **`pytest`** и **`pytest-asyncio`**.  

---

## Установка и запуск  

### Установка зависимостей  
1. Клонируйте репозиторий:  
   ```bash
   git clone https://github.com/your_username/GadgetResearcherBot.git
   cd GadgetResearcher
```
2. Установите зависимости:  
   ```bash
   pip install -r requirements.txt
```
3. Убедитесь, что у вас установлен Python версии 3.8 или выше. Для проверки версии используйте:
```bash
python --version
```
4. Убедитесь, что у вас установлен браузер Google Chrome, и его версия совместима с последним chromedriver, который автоматически загружается с помощью webdriver_manager.
