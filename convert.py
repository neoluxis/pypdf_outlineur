import yaml
import os
import pdfplumber
from PyPDF2 import PdfReader, PdfWriter

def load_tasks(path):
    with open(path) as f:
        y = yaml.load(f.read(), Loader=yaml.FullLoader)
    return y['tasks']

def print_tasks(tasks):
    print("---------------- tasks --------------")
    print("=====================================")
    print(" PDF\t|   Outline\t|   Output")
    print("-------------------------------------")
    for task in tasks:
        if task['override'] == True:
            task['output'] = task['pdf']
        else:
            task['output'] = "results/" + task['pdf'].split('/')[-1]
            os.makedirs('results', exist_ok=True)
        print(f"  {task['pdf']}\t|   {task['outline']}\t|   {task['output']}")
    print("=====================================")

def load_outline(path):
    with open(path) as f:
        y = yaml.load(f.read(), Loader=yaml.FullLoader)
    return y

def add_outline(writer, outline, recurse, max_recurse, bias, nobias, parent=None):
    if recurse > max_recurse:
        raise Exception("Recursion too deep!")
    for title, page in outline['toc'].items():
        if type(page) is not dict:
            writer.add_outline_item(title, (page if title in nobias else page + bias)-1, parent=parent)
        else:
            outline_ptr = writer.add_outline_item(title, (page['pn'] if title in nobias else page['pn'] + bias)-1, parent=parent)
            writer = add_outline(writer, page, recurse+1, max_recurse, bias, nobias, outline_ptr)
    return writer


def run_task(task):
    print(f"{task['pdf']} + {task['outline']} --> {task['output']}")
    print(f"Reading PDF from {task['pdf']}")
    reader = PdfReader(task['pdf'])
    writer = PdfWriter()
    for page in reader.pages:
        writer.add_page(page)
    print("Finish reading")
    print(f"Reading outline from {task['outline']}")
    outline = load_outline(task['outline'])
    recurse = 0
    max_recurse = outline['max_recurse']
    bias = outline['bias']
    writer = add_outline(writer, outline, recurse, max_recurse, bias, outline['nobias'])
    print(f"Writing to {task['output']}")
    with open(task['output'], 'wb') as f:
        writer.write(f)
    print(f"Finished {task['pdf']}")

def main():
    tasks = load_tasks('tasks.yaml')
    print_tasks(tasks)
    for task in tasks:
        run_task(task)

if __name__ == '__main__':
    main()
