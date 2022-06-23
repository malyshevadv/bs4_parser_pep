# Проект парсинга pep

# Описание
Парсер документации Python. Запуск пасера проиизводится через командную строку

# Аргументы:
usage: main.py [-h] [-c] [-o {pretty,file}]
               {whats-new,latest-versions,download,pep}

positional arguments:
  {whats-new,latest-versions,download}
                        Режимы работы парсера

optional arguments:
  -h, --help            show this help message and exit
  -c, --clear-cache     Очистка кеша
  -o {pretty,file}, --output {pretty,file}
                        Дополнительные способы вывода данных


### Технологии
- Python 3.7
- Beautiful Soup 4.9.3
- Requests-cache 0.6.3

### Авторы
Дарья Малышева
