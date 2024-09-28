import requests
from bs4 import BeautifulSoup
import common_module

source_id = "District of Puerto Rico Local Bankruptcy Rules"

sheet_links = {'Local Bankruptcy Rules': 'https://www.prb.uscourts.gov/?q=court-info/local-rules-and-orders/local-rules'}

for name, main_link in sheet_links.items():
    try:
        response = requests.get(main_link)
        soup = BeautifulSoup(response.content, 'html.parser')
        all_links = soup.find('span',class_='field-content').find('a')
        text = all_links.get_text(strip=True)
        link_url = all_links.get("href")
        pdf_response = requests.get(link_url)
        output_fileName = common_module.ret_file_name_full(source_id, name, text, '.pdf')
        with open(output_fileName, 'wb') as pdf_file:
            pdf_file.write(pdf_response.content)
        print(f"Downloaded: {output_fileName}")
    except Exception as sheet_links_error:
        common_module.append_error(source_id, sheet_links_error)