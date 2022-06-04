# main.py
import logging
import re
from urllib.parse import urljoin

import requests_cache
from bs4 import BeautifulSoup
from tqdm import tqdm

from configs import configure_argument_parser, configure_logging
from constants import (BASE_DIR, EXPECTED_STATUS, MAIN_DOC_URL, PEP_DOC_URL,
                       STATUS_LIST)
from outputs import control_output
from utils import find_tag, get_response


def whats_new(session):
    whats_new_url = urljoin(MAIN_DOC_URL, 'whatsnew/')
    response = get_response(session, whats_new_url)
    if response is None:
        return

    soup = BeautifulSoup(response.text, features='lxml')

    main_div = find_tag(soup, 'section', attrs={'id': 'what-s-new-in-python'})
    div_with_ul = find_tag(main_div, 'div', attrs={'class': 'toctree-wrapper'})

    section_by_python = div_with_ul.find_all(
        'li',
        attrs={'class': 'toctree-l1'}
    )

    results = [('Ссылка на статью', 'Заголовок', 'Редактор, Автор')]
    for section in tqdm(section_by_python):
        version_a_tag = section.find('a')

        href = version_a_tag['href']
        version_link = urljoin(whats_new_url, href)

        session = requests_cache.CachedSession()
        response = get_response(session, version_link)
        if response is None:
            continue

        soup = BeautifulSoup(response.text, features='lxml')
        h1 = find_tag(soup, 'h1')
        dl = find_tag(soup, 'dl')
        dl_text = dl.text.replace('\n', ' ')
        results.append((version_link, h1.text, dl_text))
    return results


def latest_versions(session):
    response = get_response(session, MAIN_DOC_URL)
    if response is None:
        return

    soup = BeautifulSoup(response.text, features='lxml')

    sidebar = find_tag(soup, 'div', attrs={'class': 'sphinxsidebarwrapper'})
    ul_tags = sidebar.find_all('ul')

    for ul in ul_tags:
        if 'All versions' in ul.text:
            a_tags = ul.find_all('a')
            break
        else:
            raise Exception('Не найден список c версиями Python')

    results = [('Ссылка на статью', 'Заголовок', 'Редактор, автор')]
    pattern = r'Python (?P<version>\d\.\d+) \((?P<status>.*)\)'
    for a_tag in a_tags:
        text_match = re.search(pattern, a_tag.text)
        if text_match is None:
            version = a_tag.text
            status = ''
        else:
            version = text_match.group('version')
            status = text_match.group('status')
        results.append((a_tag['href'], version, status))
    return results


def download(session):
    downloads_url = urljoin(MAIN_DOC_URL, 'download.html')
    response = get_response(session, downloads_url)
    if response is None:
        return

    soup = BeautifulSoup(response.text, features='lxml')

    main_tag = find_tag(soup, 'div', {'role': 'main'})
    table_tag = find_tag(main_tag, 'table', attrs={'class': 'docutils'})
    pdf_a4_tag = find_tag(
        table_tag,
        'a',
        attrs={'href': re.compile(r'.+pdf-a4\.zip$')}
    )
    archive_url = urljoin(downloads_url, pdf_a4_tag['href'])

    filename = archive_url.split('/')[-1]
    downloads_dir = BASE_DIR / 'downloads'
    downloads_dir.mkdir(exist_ok=True)
    archive_path = downloads_dir / filename

    response = session.get(archive_url)
    with open(archive_path, 'wb') as file:
        file.write(response.content)

    logging.info(f'Архив был загружен и сохранён: {archive_path}')


def pep(session):
    response = get_response(session, PEP_DOC_URL)
    if response is None:
        return

    soup = BeautifulSoup(response.text, features='lxml')

    index_section = find_tag(soup, 'section', attrs={'id': 'numerical-index'})
    tbody = find_tag(index_section, 'tbody')

    section_by_pep = tbody.find_all('tr')

    counting = [0 for i in range(len(STATUS_LIST))]
    counter = 0
    for section in tqdm(section_by_pep):
        pep_status = find_tag(section, 'td')
        preview_status = pep_status.text[1:]

        pep_a_link = find_tag(section, 'a')
        href = pep_a_link['href']
        pep_page_link = urljoin(PEP_DOC_URL, href)

        session = requests_cache.CachedSession()
        response = session.get(pep_page_link)

        local_soup = BeautifulSoup(response.text, features='lxml')
        dl = find_tag(
            local_soup,
            'dl',
            attrs={'class': 'rfc2822 field-list simple'}
        )
        status = dl.find(
            lambda tag: tag.name == 'dt' and re.search('Status', tag.text)
        ).next_sibling.next_sibling

        stat_val = status.text

        if stat_val in STATUS_LIST.keys():
            counting[STATUS_LIST[stat_val]] += 1
        if stat_val not in EXPECTED_STATUS[preview_status]:
            logging.info(f'Несовпадающие статусы: \n{pep_page_link}\n'
                         f'Статус в карточке: {stat_val}\n'
                         'Ожидаемые статусы: '
                         f'{EXPECTED_STATUS[preview_status]}')
        counter += 1

    results = [('Статус', 'Количество')]
    results.extend([(sts, counting[STATUS_LIST[sts]]) for sts in STATUS_LIST])
    results.append(('Total', counter))
    return results


MODE_TO_FUNCTION = {
    'whats-new': whats_new,
    'latest-versions': latest_versions,
    'download': download,
    'pep': pep,
}


def main():
    configure_logging()
    logging.info('Парсер запущен!')

    arg_parser = configure_argument_parser(MODE_TO_FUNCTION.keys())
    args = arg_parser.parse_args()
    logging.info(f'Аргументы командной строки: {args}')

    session = requests_cache.CachedSession()
    if args.clear_cache:
        session.cache.clear()

    parser_mode = args.mode
    if parser_mode == 'pep':
        args.output = 'file'

    results = MODE_TO_FUNCTION[parser_mode](session)
    if results is not None:
        control_output(results, args)
    logging.info('Парсер завершил работу.')


if __name__ == '__main__':
    main()
