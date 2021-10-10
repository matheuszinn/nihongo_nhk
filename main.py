import os
import requests
from bs4 import BeautifulSoup
from rich import console

from time import sleep

import urllib.request

from rich.markdown import Markdown
from rich.live import Live
from rich.panel import Panel
from rich.progress import Progress, BarColumn, TextColumn
from rich.table import Table
from rich.progress import (
    BarColumn,
    DownloadColumn,
    Progress,
    TextColumn,
    TransferSpeedColumn
) 

from rich.console import Console
from rich.panel import Panel

intro = """
 ███    ██ ██ ██   ██  ██████  ███    ██  ██████   ██████          ███    ██ ██   ██ ██   ██
 ████   ██ ██ ██   ██ ██    ██ ████   ██ ██       ██    ██         ████   ██ ██   ██ ██  ██
██ ██  ██ ██ ███████ ██    ██ ██ ██  ██ ██   ███ ██    ██         ██ ██  ██ ███████ █████
 ██  ██ ██ ██ ██   ██ ██    ██ ██  ██ ██ ██    ██ ██    ██         ██  ██ ██ ██   ██ ██  ██
 ██   ████ ██ ██   ██  ██████  ██   ████  ██████   ██████  ███████ ██   ████ ██   ██ ██   ██

                                                    by matheuszinn
"""

console = Console()

with console.screen():
    console.print(Panel(intro), justify="center")
    sleep(2)

def get_titles(urls: list, console: Console):

    def extract(url: str):

        soup = BeautifulSoup(requests.get(url).content, 'html.parser')

        h1 = soup.find('h1', {
        'class': 'lesson-title'
        })

        em = h1.find('em')
        em_text = em.string if em is not None else None

        num =  soup.find('div', {
            'class': 'cando-block',
        }).find('p', {
            'class': 'num'
        }).string.replace('#','')

        title = f'{num}- {str(h1.contents[0]).strip()}' if em is None else f'{num}- {em_text} {str(h1.contents[2]).strip()}'

        console.log(f'Found {title}')
        return title 
        
    return [extract(x) for x in urls]


correct_num = lambda x: x if x >=10 else "0"+str(x)

title_urls = [f'https://www.nhk.or.jp/lesson/pt/lessons/{correct_num(x)}.html' for x in range(1, 49)]
downloads_urls = [
    (f'https://www.nhk.or.jp/lesson/pt/mp3/audio_lesson_{correct_num(x)}.mp3',
    f'https://www.nhk.or.jp/lesson/pt/pdf/textbook_lesson_{correct_num(x)}.pdf')
    for x in range(1, 49)
    ]

with console.status('Fetching titles...') as status:
    sleep(0.5)
    titles_list = get_titles(title_urls, console)

    console.print(Panel.fit('Fetched all files.'))
    console.print(Panel.fit('Starting to download the files.'))

    status.update('Downloading files.')
    console.rule('[bold white]Downloading')

job_progress = Progress(
TextColumn('[bold red]{task.fields[filename]}', justify='right'),    
BarColumn(bar_width=None),
    "[progress.percentage]{task.percentage:>3.1f}%",
    "*",
    DownloadColumn(),
    "*",
    TransferSpeedColumn(),
    "*",
)


job1 = job_progress.add_task("",filename='teste')

total = len(title_urls) * 2
overall_progress = Progress()
overall_task = overall_progress.add_task("", total=int(total))

progress_table = Table.grid()
progress_table.add_row(
    Panel.fit(
        overall_progress, title="All Downloads", border_style="green", padding=(0, 2)
    ),
    Panel.fit(job_progress, title='Current Download', border_style="red", padding=(0, 1)),
)

def update_progress(block_num, block_size, total_size):
    job_progress.update(job1, total=int(total_size), advance=block_num * block_size)
    
    if job_progress.tasks[0].completed:
        job_progress.stop()

with Live(progress_table, refresh_per_second=10):

    opener=urllib.request.build_opener()
    opener.addheaders=[('User-Agent','Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1941.0 Safari/537.36')]
    urllib.request.install_opener(opener)


    os.mkdir('./downloads')
    os.chdir('./downloads')

    for i in range(len(titles_list)):
        os.mkdir(f'./{titles_list[i]}')
        os.chdir(f'./{titles_list[i]}')

        for j in range(2):
            filename = downloads_urls[i][j].split(r'/')[-1]
            job_progress.update(job1, filename=filename)
            urllib.request.urlretrieve(downloads_urls[i][j], filename, update_progress)

            overall_progress.console.log(f'[bold blue]Downloaded {filename}')
            job_progress.reset(job1)
            overall_progress.advance(overall_task)

        os.chdir('../')

console.print(Panel("""All the files were downloaded at [bold yellow]./downloads\n[bold white]勉強頑張って!"""), justify= 'center')