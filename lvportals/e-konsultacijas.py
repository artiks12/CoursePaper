import requests
from pyquery import PyQuery as pq
from lxml import etree
import urllib
from datetime import datetime
import json

def get_datetime(date_string: str):
    if date_string == '' or date_string == None: return None
    parts1 = date_string.split('.')
    parts2 = parts1[1].split(',')

    day = int(parts1[0])
    year = int(parts2[1])
    month = -1
    
    if parts2[0].strip() == 'janvārī': month = 1
    if parts2[0].strip() == 'februārī': month = 2
    if parts2[0].strip() == 'martā': month = 3
    if parts2[0].strip() == 'aprīlī': month = 4
    if parts2[0].strip() == 'maijā': month = 5
    if parts2[0].strip() == 'jūnijā': month = 6
    if parts2[0].strip() == 'jūlijā': month = 7
    if parts2[0].strip() == 'augustā': month = 8
    if parts2[0].strip() == 'septembrī': month = 9
    if parts2[0].strip() == 'oktobrī': month = 10
    if parts2[0].strip() == 'novembrī': month = 11
    if parts2[0].strip() == 'decembrī': month = 12

    return datetime(year=year, month=month, day=day).strftime('%Y-%m-%d')

def get_html_content(url):
    try:
        # Send a GET request to the initial URL
        response = requests.get(url)
        # Ensure the request was successful
        response.raise_for_status()
        
        # Set the encoding to UTF-8 (often necessary for correct decoding)
        response.encoding = 'utf-8'
        
        # Print the final URL after redirection
        final_url = response.url
        #print(f"Final URL after redirection: {final_url}")
        
        # Return the HTML content of the final URL
        return response.text, final_url
    
    except requests.exceptions.RequestException as e:
        #print(f"An error occurred: {e}")
        return None, None

# Example usage:
base_url = "https://lvportals.lv/e-konsultacijas/"

try:
    f = open('config.json')
    config = json.load(f)
    start = int(config['start'])
    count = int(config['count'])
    group_length = int(config['groupSize'])
    f.close()
except:
    start = 1
    count = 1000
    group_length = 10

all_entries = []
unanswered_entries = []
program_start = datetime.now()
# Open the file in UTF-8 mode
for i in range(start, start+count):
    entry = {}
    entry['Numurs'] = i
    html_content, final_url = get_html_content(base_url + str(i))
    if html_content:
        entry['URL'] = final_url
        # Write raw HTML content with UTF-8 encoding to the file
        all_content = pq(html_content)
        
        topic_tag = all_content('div.data.section.eKonsultacijas')
        entry['Tēma'] = topic_tag.text()[6:]

        main_tag = all_content('div.articleContent')
        entry['Nosaukums'] = main_tag('h1').text()

        content_tag = main_tag('div.eKonsultacijas')
        
        question_tag = content_tag('div.blockContainer.noBottom.articleQuestion')
        entry['JautājumaDatums'] = get_datetime(question_tag('div.blockData div.smallText').text())
        entry['JautājumaAutors'] = question_tag('div.blockData div.author').text()
        entry['Jautājums'] = question_tag('div.article').text()
        entry['JautājumaHTML'] = question_tag('div.article').html()

        answer_tag = content_tag('div.blockContainer.noBottom.articleAnswer')
        entry['AtbildesDatums'] = get_datetime(answer_tag('div.smallText').text())
        entry['AtbildesAutors'] = answer_tag('div.authors div div.text a').text()
        entry['AtbildesAutoraInfo'] = answer_tag('div.authors div div.text div').text()
        entry['Atbilde'] = answer_tag('div.article.stickyHeight').text()
        entry['AtbildesHTML'] = answer_tag('div.article.stickyHeight').html()
    
        if entry['AtbildesDatums'] == None: unanswered_entries.append(entry)
        else: all_entries.append(entry)
    
    if i % group_length == 0 and i != 0:
        with open(f'dati/dati_{i-group_length+1}_{i}.json', 'w', encoding='utf-8') as f:
            json.dump(all_entries, f, ensure_ascii=False, indent=4)
            all_entries = []

if len(unanswered_entries) > 0:
    temp = []
    with open(f'dati/neatbildētie.json', encoding='utf-8') as f:
        temp = json.load(f)
    temp.extend(unanswered_entries)
    with open(f'dati/neatbildētie.json', 'w', encoding='utf-8') as f:
        json.dump(temp, f, ensure_ascii=False, indent=4)

print(f'Program ran for this long: {datetime.now() - program_start}')

f = open('config.json','w')
config['start'] = start+count
json.dump(config, f, ensure_ascii=False, indent=4)
f.close()