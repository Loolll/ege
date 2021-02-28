import bs4
import requests
import os
import json


def wrapper_over_requests_get():
    #TODO. Need to save memory.
    pass



DEFAULTS = {'russian': set(str(x) for x in range(1, 27))}


def default_or_not(subject, number):
    """ Determines whether to treat as a special case or not. Returns (None, None) if not """
    if number in DEFAULTS[subject]:
        return None, None
    return subject, number


def html_in_text_with_new_line_support(html: bs4.BeautifulSoup):
    """ Parses new line tags in \n. And returns text """
    return html.get_text(separator="\n")


def parse_tasks(link: str, subject=None, number=None):
    """ Link to tasks page. """
    subject, number = default_or_not(subject, number)
    if subject is None and number is None:
        for page in range(1, 100):
            html = requests.get(link, params={"page": page}).text
            html = bs4.BeautifulSoup(html, features='lxml')
            tasks = html.find_all(name="div", attrs={"class": "problem_container"})
            for task in tasks:
                id = task.find(name="span", attrs={"class": "prob_nums"}).find(name="a").text
                question = html_in_text_with_new_line_support(task.find(name="div", attrs={"class": "pbody"}))
                answer = task.find(name="div", attrs={"class": "answer"}).text
                solution = html_in_text_with_new_line_support(task.find(
                    name="div", attrs={"class": "nobreak solution"}))
                yield {"id": id, "question": question, "answer": answer, "solution": solution}
            if not len(tasks):
                break


def subject_to_link(path="start_links"):
    """ Returns dict {"$subject": "$link", ...} """
    output = {}
    with open(path) as file:
        for line in file.readlines():
            if len(line) > 5:
                pair = line.split(" >>> ")
                output.update(dict([(pair[0], pair[1].replace('\n', ''))]))
    return output


def parse_link_to_tasks(start_link):
    """ Returns dict {"$task_number": ["$link1", "$link2", ...} """
    output = {}
    for theme in range(1, 1000):
        link = f"{start_link}test?theme={theme}"
        html = requests.get(link).text
        if len(html) < 130000:
            continue
        html = bs4.BeautifulSoup(html, features='lxml')
        number = ''.join([x for x in html.find(
            name="span", attrs={"class": "prob_nums"}).text.split("№")[0][8:].strip()])
        if number not in output:
            output[number] = []
        output[number].append(link)
    return output


def links_refresh():
    """ Refreshes links to cur subject numbers """
    subjects = subject_to_link()
    for subject in subjects:
        link = subjects[subject]
        links = parse_link_to_tasks(link)
        with open(f"links/{subject}.json", 'w') as file:
            file.write(json.dumps(links, sort_keys=True))


def tasks_refresh():
    """ Refreshes tasks from already existed links in links/$subject.json """
    subjects = {}
    walk = list(os.walk('links'))[0]
    for path in walk[2]:
        numbers: str
        with open(f'links/{path}') as file:
            numbers = file.read()
        subjects[path[:-5]] = json.loads(numbers)
    for subject in subjects.keys():
        for number in subjects[subject].keys():
            tasks = []
            for link in subjects[subject][number]:
                for task in parse_tasks(link=link, subject=subject, number=number):
                    tasks.append(task)
            subjects[subject][number] = tasks
        with open(f'data/{subject}.json', 'w') as file:
            file.write(json.dumps(subjects[subject], sort_keys=True))


def get_tasks(subject, number, nums=None):
    #TODO
    if nums is None:
        nums = 10
    data = {}
    with open(f"data/{subject}.json") as file:
        data = json.loads(file.read())
    data = data[number]
    for i in range(nums):
        print(data[i])


if __name__ == '__main__':
    #links_refresh()
    #tasks_refresh()
    get_tasks('russian', '5')
