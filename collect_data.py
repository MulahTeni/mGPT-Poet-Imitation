import requests
from bs4 import BeautifulSoup
from datasets import Dataset
import os
import logging

logging.basicConfig(filename='app.log', filemode='a+', format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)


def get_page_data(pref, session, url, page, class_name, count):
    """
    get all text from the urls in the given web page
    """
    full_url = f'{url}{page}'
    print(full_url)
    try:
        response = session.get(full_url)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        poem_containers = soup.find_all('div', class_='category-poem box')
        logging.info(f'New page link: {full_url}')
        print(f'New page link: {full_url}')
        
    except Exception as e:
        logging.error(f'Error connecting to main link {full_url}: {e}')
        return [], count

    poems = []
    for container in poem_containers:
        links = container.find('div', class_=class_name).find_all('a')
        for link in links:
            href = link.get('href')
            if href:
                try:
                    full_link = f'{pref}{href}'
                    if full_link == url:
                        continue
                    link_response = session.get(full_link)
                    link_soup = BeautifulSoup(link_response.content, 'html.parser')
                    
                except Exception as e:
                    logging.error(f'Error connecting to sub link {full_link}: {e}')
                    continue

                content_div = link_soup.find('div', class_='pd-text')
                if content_div:
                    text = content_div.text.strip()
                    poems.append(text)
                else:
                    logging.error(f'Error getting poem from link {full_link}')
                    continue
                logging.info(f'Processing poem {count}: {full_link}')
                print(f'Processing poem {count}: {full_link}')
                count += 1

    return poems, count



def get_all_data(pref, url, class_name, page_prefix, page_count):
    """
        get poets all texts and store them
    """
    all_data = []
    
    with requests.Session() as session:
        count = 1
        for i in range(1, page_count + 1):
            page_data, count = get_page_data(pref, session, url, f'{page_prefix}{i}', class_name, count)
            all_data.extend(page_data)
            
    return all_data


def save_data(poet, data):
    """
        save collected data to disk as datasetDict
    """
    poem_count = len(data)
    poet_len = [poet] * poem_count
    poet_dataset = Dataset.from_dict({'poet': poet_len, 'poem': data})
    path = f"collected_data/{poet}_dataset"
    os.makedirs(os.path.dirname(path), exist_ok = True)
    poet_dataset.save_to_disk(path)


if __name__ == '__main__':
    poets_pages = {
        'necip-fazil-kisakurek': 34,
        'pir-sultan-abdal': 40
    }
    pref = "https://www.antoloji.com"
    class_name = 'poem-title-pop'
    page_prefix = '?sayfa='
    
    for poet, page_count in poets_pages.items():
        url = f"{pref}/{poet}/"
        all_pages_data = get_all_data(pref, url, class_name, page_prefix, page_count)
        if not all_pages_data:
            logging.error(f'Error all_pages_data is null')
            print(f'Error all_pages_data is null')
            continue
        save_data(poet, all_pages_data)