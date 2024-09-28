import requests
from bs4 import BeautifulSoup
import common_module

source_id = "Eastern District of Oklahoma Local Bankruptcy Rules"

# same_rules = []
allowed_rules = common_module.return_lists('links.txt')
ignore_rules = common_module.return_lists('skip.txt')

sheet_links = {'Local Bankruptcy Rules': 'https://www.okeb.uscourts.gov/local-rules-interactive-version#Rule%201001-1'}
rule_id_start = "Rule 1001-1"
rule_id_end = "Rule 9076-1"

for name, main_link in sheet_links.items():
    try:
        response = requests.get(main_link)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')
        a_elements = soup.find_all('a', {"id": True})

        rules = []

        for a_tag in a_elements:
            try:
                rule_id = a_tag['id']
                rule_name = a_tag.get_text()
                h4_elements = []
                next_element = a_tag.find_next()
                while next_element:
                    if next_element.name == 'a' and 'id' in next_element.attrs:
                        # Stop when encountering the next A tag with "id"
                        break
                    if next_element.name == 'h4':
                        h4_elements.append(next_element.get_text())
                    next_element = next_element.find_next()

                rule_info = {
                    'rule_id': rule_id,
                    'rule_name': rule_name,
                    'h4_elements': h4_elements,
                }

                rules.append(rule_info)

            except Exception as a_element_error:
                common_module.append_error(source_id, a_element_error)

        # Print the extracted information for existing rules
        for i, rule in enumerate(rules):
            if i<len(rules)-1:
                if rule_id_start <= rule['rule_id'] <= rule_id_end:
                    print(f"Rule ID: {rule['rule_id']}")
                    print(f"Rule Name: {rule['rule_name']}")
                    print("H4 Elements:")
                    for i,h4 in enumerate(rule['h4_elements']):
                        if i<len(rule['h4_elements'])-1:
                            print(h4)
                    print("\n")

                    # Save the information as an HTML file
                    cleaned_rule_text = common_module.clean_rule_title(rule_name)
                    if cleaned_rule_text in ignore_rules:
                        continue
                    else:
                        next_rule_name = rules[i + 1]['rule_name'] if i + 1 < len(rules) else ""
                        output_fileName = common_module.ret_file_name_full(source_id, name, rule['rule_name'] + " " + next_rule_name, '.html')
                        if output_fileName:
                            with open(output_fileName, 'w', encoding='utf-8') as f:
                                f.write(f"<h2>{rule['rule_name']}</h2>\n")
                                for i, h4 in enumerate(rule['h4_elements']):
                                    if i < len(rule['h4_elements']) - 1:
                                        f.write(f"<h4>{h4}</h4>\n")

                    if cleaned_rule_text in allowed_rules:
                        pass
                    else:
                        common_module.append_new_rule(source_id, rule['rule_name'] )

    except Exception as sheet_links_error:
        common_module.append_error(source_id, sheet_links_error)
