import requests
import json
import csv

from selenium import webdriver
from selenium.webdriver.firefox.options import Options

# Fill in these with your own values!
cookies = {
    '__cfduid': '',
    'cookieAlert': 'true',
    '_ga': '',
    'Jbl_PersonId': '',
    'MoodleSession': '',
    'ASP.NET_SessionId': ''
}

def main():

    jbl_base_url = 'http://navigate2.jblearning.com'
    course_block_url = 'http://navigate2.jblearning.com/course/view.php?id=51018'

    options = Options()
    options.headless = True
    driver = webdriver.Firefox(options=options)

    driver.get(jbl_base_url)

    for key in cookies.keys():
        cookie = {'name': key, 'value': cookies[key]}
        driver.add_cookie(cookie)

    chapters = get_flashcard_urls(driver, course_block_url)

    for chapter in chapters:
        chapter['questions'] = get_flashcards(driver, cookies, chapter['url'])

    for chapter in chapters:
        with open(f'{chapter["chapter"]}.csv', 'w', newline='') as results_csv:
            csv_writer = csv.writer(results_csv, delimiter=' ',
                                    quotechar='|', quoting=csv.QUOTE_MINIMAL)
            csv_writer.writerow(['Question', 'Answer'])
            for question in chapter['questions']:
                csv_writer.writerow([question['question'], question['answer']])

    with open('results.csv', 'w') as results_csv:

        csv_writer = csv.writer(results_csv, delimiter=' ',
                                quotechar='|', quoting=csv.QUOTE_MINIMAL)
        csv_writer.writerow(['Chapter', 'Question', 'Answer'])

        for chapter in chapters:
            for question in chapter['questions']:
                csv_writer.writerow([chapter['chapter'], question['question'], question['answer']])

    json_obj = json.dumps(chapters)

    with open('results.json', 'w') as results_json:
        results_json.write(json_obj)

    driver.quit()


def get_flashcard_urls(driver: webdriver, base_url: str):
    """
    :param base_url:
    :param driver:
    :param cookies:
    :return: List of dict of the form:
    [{'chapter' : 'Chapter 7 Lifting and Moving', 'url' : 'https://full_url'}, ...]
    """
    driver.get(base_url)

    chapter_list = []
    flashcard_lis = driver.find_elements_by_xpath(".//li[@class='activity flashcard modtype_flashcard ']")
    for li in flashcard_lis:
        # Make flashcards interactable
        id = li.get_attribute('id')
        script = f"document.getElementById('{id}').style.display='block';"
        driver.execute_script(script)

        # Get the chapter names from uncle h3 (neighbor element of parent ul)
        chapter_title = li.find_element_by_xpath("../../h3[@class='chapter_title']").text

        # Get the link to flashcards
        flashcard_url = li.find_element_by_xpath(".//a").get_attribute('href')

        chapter_list.append({'chapter': chapter_title, 'url': flashcard_url})

    return chapter_list


def get_flashcards(driver: webdriver, cookies: dict, flashcards_url: str):
    """
    Get the actual flashcards content for the given chapter
    :param driver:
    :param cookies:
    :param flashcards_url:
    :return: List of the form
    [ {'question': 'Question?', 'answer': 'Answer'}, ...]
    """

    driver.get(flashcards_url)

    # <input name="hdnIndtructionUrl" type="hidden" id="hdnIndtructionUrl" value="InstructionsTryOut.aspx?P2=21953&amp;msg=a&amp;RIDs=10000404752&amp;theme=IrisBlue">
    id_element: str = driver.find_element_by_id('hdnIndtructionUrl').get_attribute('value')
    form_id = id_element[id_element.find('P2=') + 3: id_element.rfind(
        '&msg=a')]  # https://stackoverflow.com/questions/1732348/regex-match-open-tags-except-xhtml-self-contained-tags/

    # Make all questions interactable
    question_divs = driver.find_elements_by_xpath(".//div[@type='Question']")
    for div in question_divs:
        id = div.get_attribute('id')
        script = f"document.getElementById('{id}').style.display='table-cell';"
        driver.execute_script(script)

    question_list = []

    # questions = soup.find_all('td', class_='clsTdTest')
    questions = driver.find_elements_by_xpath(".//td[@class='clsTdTest']")
    for question in questions:
        id = question.get_attribute('id')
        text = question.text
        div = question.find_elements_by_tag_name('input')
        if div:
            id = div[0].get_attribute('id')
            name = id + '_1'  # TODO this will probably not work on some pages
            #name = div[0].get_attribute('name')

            answer_cookies = cookies

            answer_headers = {
                'Host': 'assessments-navigate2.jblearning.com',
                'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:74.0) Gecko/20100101 Firefox/74.0',
                'Accept': 'application/json, text/javascript, */*; q=0.01',
                'Accept-Language': 'en-US,en;q=0.5',
                'Accept-Encoding': 'gzip, deflate',
                'Content-Type': 'application/json; charset=utf-8',
                'X-Requested-With': 'XMLHttpRequest',
                'Content-Length': '204',
                'Origin': 'http://assessments-navigate2.jblearning.com',
                'Connection': 'close',
                'DNT': '1',
            }

            data = {
                "questionInfo":
                    {"ChoiceValues": ["<![CDATA[asd]]>"],
                     "ChoiceIds": [name]
                     },
                "QGUID": id,
                "assessmentid": int(form_id),
                "AssessmentVersionNo": "1.0"
            }

            response = requests.post(
                'http://assessments-navigate2.jblearning.com/FlashCard/TryOut.aspx/EvaluateEachItemAndGetResult',
                headers=answer_headers, cookies=answer_cookies, json=data, verify=False)

            # {"d":{"__type":"Saras.TestDelivery.BusinessObject.Response.UserResponseEvaluateStatus","IsCorrect":false,"UserResponse":null,"CorrectChoices":"8990ebdf-c2b5-4991-b03e-41956003a141_1#,adolescent","CorrectFeedback":". ","ChoiceStatus":":8990ebdf-c2b5-4991-b03e-41956003a141_1#0","TimeSpent":null}}
            correct = response.json()['d']['CorrectChoices'].split('#,')[1]

            question_list.append({'question': text, 'answer': correct})
            print(f'{text},{correct}')

    return question_list


if __name__ == '__main__':
    main()
