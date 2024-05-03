import requests
from bs4 import BeautifulSoup
import time
import numpy as np

def fetch_all_match_urls():
    # VLR.gg URL 
    base_url = 'https://www.vlr.gg'
    match_link_array = np.zeros(0)
    end_of_website = False
    page_num = 1

    while True:
        if end_of_website == True:
            break
        # Construct URL for matches page
        match_page_url = f'{base_url}/matches/results/?page={page_num}'

        print(f'Current page is {page_num}')
        time.sleep(1)

        # Send a GET request to matches page
        response = requests.get(match_page_url)

        # Check if request was successful
        if response.status_code == 200:
            # Parse HTML content
            parsed_content = BeautifulSoup(response.content, 'html.parser')

            # Find HTML elements containing match URLs
            match_links = parsed_content.find_all('a', class_=['wf-module-item', 'match-item'])

            # Extract match URLs and add them to the array
            for link in match_links:
                match_link_array = np.append(match_link_array, base_url + link['href'])
            
            # Find current page button
            current_page_element = parsed_content.find('span', class_=['btn', 'mod-page', 'mod-active'])
            page_num = int(current_page_element.get_text())

            # Find page buttons with url
            page_element_url = parsed_content.find_all('a', class_=['btn', 'mod-page'])

            i = 1
            num_page_elements = len(page_element_url)
            # Check if there is a next page
            for link in page_element_url:
                # Check if link is a page number
                try:
                    url_page_num = int(link['href'].split('=')[-1])
                except ValueError:
                # Element checked and is not next page
                    i += 1
                    continue
                
                # Element is next page. Go to next page
                if url_page_num - 1 == page_num:
                    page_num += 1
                    break
                # If there are elements
                elif i == num_page_elements:
                    end_of_website = True
                    print('Reached end of website.')
                    break
                # Element is not next page
                else:
                    i += 1
                    continue
        else:
            print(f"Failed to retrieve data from {match_page_url}. Status code: {response.status_code}")
            break
    
    return match_link_array

def write_match_urls_to_file(match_urls):
    with open('C:\\Users\\Simen\\Desktop\\valorant-rankings\\match_urls.txt', 'w') as infile:
        for link in match_urls:
            infile.write(f'{link}\n')

match_urls = fetch_all_match_urls()
write_match_urls_to_file(match_urls=match_urls)