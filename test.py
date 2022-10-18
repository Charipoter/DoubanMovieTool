from head import *


def get_cmts_html(page):
    header = {'User-Agent': str(random.choice(user_agents)),
              'Host': 'movie.douban.com',
              'Cookie': cookie
              }
    url = r'https://movie.douban.com/subject/{}/comments?start={}&limit=20&status=P&sort=new_score'.format(35427471, page)
    html = bs(requests.get(url, headers=header).text, 'html.parser')
    print(html.prettify())

get_cmts_html(2000)

