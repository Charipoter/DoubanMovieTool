import threading
from head import *


class MyFigure(FigureCanvas, ):  # matplotlib画图类
    def __init__(self, movie_cmts_rate, width=5, height=4, dpi=100):
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        super(MyFigure, self).__init__(self.fig)
        self.axes = self.fig.add_subplot()
        self.draw_group = [lambda: self.plot(),  # 画图函数接口变量
                           lambda: self.scatter(),
                           lambda: self.bar(),
                           lambda: self.pie()
                           ]
        self.movie_cmts_rate = movie_cmts_rate
        self.x = ['五星', '四星', '三星', '二星', '一星']
        self.y = [float(i[0: len(i) - 1]) for i in self.movie_cmts_rate]

    def plot(self):
        self.axes.plot(self.x, self.y)

    def scatter(self):
        self.axes.scatter(self.x, self.y)

    def bar(self):
        self.axes.bar(self.x, self.y, width=0.3)

    def pie(self):
        self.axes.pie(self.y, labels=self.x, autopct='%1.1f%%', shadow=True, startangle=150, labeldistance=1.2,
                      radius=1.2)

    def cmts_rate_draw(self, n=0):  # 统一画图函数接口
        self.draw_group[n]()


class Init_Window(QtWidgets.QWidget, Ui_Form):  # 继承父类，初始化成员
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.listModel = QStringListModel()
        self.movie_list = []
        self.listModel.setStringList(self.movie_list)
        self.request_result = None  # 统一电影结果json格式
        self.movie_id = None
        self.movie_html = None
        self.isShow = None  # 是否上映
        self.isError = None  # 是否搜索无结果
        self.movie_cmts_rate = None
        self.Fig = None  # 画图
        self.step = 0  # 是否第一次进入画图界面
        self.page = 0  # 评论界面页数
        self.movie_rank_list = None
        self.word_cloud_type = 0
        # 电影展示界面接口变量
        self.set_movie_select_list_group = [lambda: self.set_search_result(), lambda: self.set_rank_result()]
        # 避免重复电影操作
        self.movie_id_save1 = None
        self.movie_id_save2 = None
        self.movie_id_save3 = None
        # 视频播放
        self.player = QMediaPlayer()
        self.player.setVideoOutput(self.player_window)
        self.user_words = {}  # 词云用户添加词


class Main_Function(Init_Window):  # 功能类
    def __init__(self):
        super().__init__()

    def go_current_page2(self):  # 转移到搜索页
        self.movie_id_save1 = self.movie_id
        self.clear_user_words()
        self.stackedWidget.setCurrentIndex(1)

    def back_wordcloud_to_page3(self):  # 词云页转移到电影信息页
        self.movie_id_save2 = self.movie_id
        self.stackedWidget.setCurrentIndex(2)

    def back_cmts_to_page3(self):  # 评论页转移到信息页
        self.page6_init()
        self.stackedWidget.setCurrentIndex(2)

    def back_mpl_to_page3(self):  # 画图页转移到信息页
        self.stackedWidget.setCurrentIndex(2)

    def back_video_to_page3(self):  # 视频页转移到信息页
        self.movie_id_save3 = self.movie_id
        self.close_video()
        self.stackedWidget.setCurrentIndex(2)

    def request_for_search(self):
        user_search = self.search_line.text()
        url = r'https://movie.douban.com/j/subject_suggest?q={}'.format(user_search)
        header = {'User-Agent': str(random.choice(user_agents)),
                  'Host': 'movie.douban.com',
                  'Cookie': cookie
                  }
        try:  # 网络都没连上
            self.request_result = json.loads(requests.get(url, headers=header).text)
        except requests.exceptions.ConnectionError:
            QtWidgets.QMessageBox.about(self, '咋回事啊', '你没网!')

    def go_page2_search(self):  # 通过搜索转移到搜索页
        self.movie_id_save1 = self.movie_id  # 缓存
        self.clear_user_words()
        self.close_video()  # 视频关闭
        self.rank_button_visible_set(False)
        self.page6_init()
        self.request_for_search()
        self.set_movie_select_list(0)
        self.stackedWidget.setCurrentIndex(1)

    def set_movie_select_list_none(self):
        self.listModel.setStringList(["换个试试"])
        self.movie_select_list.setModel(self.listModel)
        self.isError = True

    def set_movie_select_list(self, type):  # 电影名展示界面接口
        self.set_movie_select_list_group[type]()

    def rank_button_set(self, flag):  # 排行相关的按钮设置
        self.show_next_button.setDisabled(flag)
        self.apply_rank_set_button.setDisabled(flag)
        self.choice_rank_start.setDisabled(flag)
        self.choice_rank_finish.setDisabled(flag)

    def set_search_result(self):  # 搜索结果展示
        self.movie_list = []
        flag = False  # 没结果或者结果都不是电影，即调用 self.set_movie_select_list_none()
        if len(self.request_result) == 0:
            return self.set_movie_select_list_none()
        for i, item in enumerate(self.request_result):
            if item['type'] != 'movie':
                continue
            self.movie_list.append("{}.{}".format(i + 1, item['title']))
            flag = True
        if not flag:
            return self.set_movie_select_list_none()
        self.listModel.setStringList(self.movie_list)
        self.movie_select_list.setModel(self.listModel)
        self.isError = False

    def set_rank_result(self):  # 排行结果展示
        self.movie_list = []
        for item in self.request_result:
            self.movie_list.append("{}.{}".format(item['rank'], item['title']))
        self.listModel.setStringList(self.movie_list)
        self.movie_select_list.setModel(self.listModel)
        self.isError = False

    def set_choice_rank_new(self):
        self.rank_button_set(True)
        url = r'https://movie.douban.com/chart'
        header = {'User-Agent': str(random.choice(user_agents)),
                  'Host': 'movie.douban.com',
                  'Cookie': cookie
                  }
        tmp = bs(requests.get(url, headers=header).text, 'html.parser').find('div', 'indent').find_all('a', 'nbg')
        js = []
        i = 1
        for item in tmp:
            name = item.get('title')
            id = re.findall(r'\d*', item.get('href'))[-3]
            js.append({'title': name, 'id': id, 'rank': i})
            i += 1
        self.request_result = js
        self.set_next_button()

    def set_choice_rank_praise(self):
        self.rank_button_set(True)
        url = r'https://movie.douban.com/chart'
        header = {'User-Agent': str(random.choice(user_agents)),
                  'Host': 'movie.douban.com',
                  'Cookie': cookie
                  }
        tmp = bs(requests.get(url, headers=header).text, 'html.parser').find('div', 'movie_top').find('div', 'movie_top').find_all('a')
        js = []
        i = 1
        for item in tmp:
            name = item.string.strip()
            id = re.findall(r'\d*', item.get('href'))[-3]
            js.append({'title': name, 'id': id, 'rank': i})
            i += 1
        self.request_result = js
        self.set_next_button()

    def set_choice_rank_american(self):
        self.rank_button_set(True)
        url = r'https://movie.douban.com/chart'
        header = {'User-Agent': str(random.choice(user_agents)),
                  'Host': 'movie.douban.com',
                  'Cookie': cookie
                  }
        tmp = bs(requests.get(url, headers=header).text, 'html.parser').find('div', 'movie_top').find_all('div','movie_top')[1].find_all('a')
        js = []
        i = 1
        for item in tmp:
            name = item.string.strip()
            id = re.findall(r'\d*', item.get('href'))[-3]
            js.append({'title': name, 'id': id, 'rank': i})
            i += 1
        self.request_result = js
        self.set_next_button()

    # def test2(self, type_name, offset):
    #     self.rank_button_set(False)
    #     type = {'纪录片': '1', '剧情': '11', '喜剧': '24', '动作': '5', '爱情': '13', '科幻': '17', '动画': '25', '悬疑': '10',
    #             '惊悚': '19', '恐怖': '20', '短片': '23', '情色': '6', '同性': '26', '音乐': '14', '歌舞': '7', '家庭': '28',
    #             '儿童': '8',
    #             '传记': '2', '历史': '4', '战争': '22', '犯罪': '3', '西部': '27', '奇幻': '16', '冒险': '15', '灾难': '12',
    #             '武侠': '29',
    #             '古装': '30', '运动': '18', '黑色电影': '31'}
    #     url = r'https://movie.douban.com/j/chart/top_list?type={}&interval_id=100%3A90&action=&start={}&limit={}'.format(
    #         type[type_name], str(self.choice_rank_start.value() + offset - 1), str(self.choice_rank_finish.value()))
    #     header = {'User-Agent': str(random.choice(user_agents)),
    #               'Host': 'movie.douban.com',
    #               'Cookie': cookie
    #               }
    #     self.request_result = json.loads(requests.get(url, headers=header).text)
    #     self.set_back_button()
    #     self.set_next_button()

    def set_choice_rank_class(self, type_name, offset):
        self.rank_button_set(False)
        type = {'纪录片': '1', '剧情': '11', '喜剧': '24', '动作': '5', '爱情': '13', '科幻': '17', '动画': '25', '悬疑': '10',
                '惊悚': '19', '恐怖': '20', '短片': '23', '情色': '6', '同性': '26', '音乐': '14', '歌舞': '7', '家庭': '28',
                '儿童': '8',
                '传记': '2', '历史': '4', '战争': '22', '犯罪': '3', '西部': '27', '奇幻': '16', '冒险': '15', '灾难': '12',
                '武侠': '29',
                '古装': '30', '运动': '18', '黑色电影': '31'}
        url = r'https://movie.douban.com/j/chart/top_list?type={}&interval_id=100%3A90&action=&start={}&limit={}'.format(
            type[type_name], str(self.choice_rank_start.value() + offset - 1), str(self.choice_rank_finish.value()))
        header = {'User-Agent': str(random.choice(user_agents)),
                  'Host': 'movie.douban.com',
                  'Cookie': cookie
                  }
        self.request_result = json.loads(requests.get(url, headers=header).text)
        self.set_back_button()
        self.set_next_button()


    def rank_button_visible_set(self, flag):
        self.label_3.setVisible(flag)
        self.label_4.setVisible(flag)
        self.choice_rank_start.setVisible(flag)
        self.choice_rank_finish.setVisible(flag)
        self.apply_rank_set_button.setVisible(flag)
        self.show_back_button.setVisible(flag)
        self.show_next_button.setVisible(flag)

    def set_choice_rank(self, _=0, offset=0):  # 排名类展示统一接口
        type_name = self.choice_rank_type_list.currentText()
        if type_name == '【分类排行榜】：' or type_name == '【实时榜单】：':
            self.rank_button_set(True)
            self.rank_button_visible_set(False)
            self.set_movie_select_list_none()
        elif type_name == '新片榜':
            self.rank_button_visible_set(False)
            self.set_choice_rank_new()
        elif type_name == '一周口碑榜':
            self.rank_button_visible_set(False)
            self.set_choice_rank_praise()
        elif type_name == '北美票房榜':
            self.rank_button_visible_set(False)
            self.set_choice_rank_american()
        else:
            self.rank_button_visible_set(True)
            self.set_choice_rank_class(type_name, offset)

    def set_choice_rank_next(self):
        self.set_choice_rank(offset=self.choice_rank_finish.value())  # 根据偏移数再次爬取排行信息
        self.choice_rank_start.setValue(self.choice_rank_start.value() + self.choice_rank_finish.value())
        self.set_back_button()

    def set_next_button(self):  # ’下一页‘按钮自检
        if self.request_result:
            self.set_movie_select_list(1)  # 排行的电影名在此处进行放置
        else:
            self.set_movie_select_list_none()
            self.show_next_button.setDisabled(True)

    def set_choice_rank_back(self):
        self.set_choice_rank(offset=-self.choice_rank_finish.value())
        self.choice_rank_start.setValue(self.choice_rank_start.value() - self.choice_rank_finish.value())
        self.set_back_button()

    def set_back_button(self):  # ’上一页‘按钮自检
        if self.choice_rank_start.value() >= self.choice_rank_finish.value() + 1:
            self.show_back_button.setDisabled(False)
        else:
            self.show_back_button.setDisabled(True)

    def page3_button_set(self, flag):  # 如果电影没评论，则这两项功能都关闭
        self.word_cloud_box.setDisabled(flag)
        self.cmts_rate_button.setDisabled(flag)
        self.see_cmts_button.setDisabled(flag)

    def go_page3_movie_analyze(self):  # 转移到电影信息页
        if self.isError:  # 用户可能故意双击非电影选项
            QtWidgets.QMessageBox.about(self, 'error', '大哥，别选这个')
        else:
            index = self.movie_select_list.currentIndex().row()
            self.movie_name.setText('《' + self.request_result[index]['title'] + '》')
            self.movie_id = self.request_result[index]['id']
            self.set_movie_data_all()
            if self.isShow:  # 压根没上映就没这些功能了
                self.page3_button_set(False)
            else:
                self.page3_button_set(True)
            self.progress_bar.setVisible(False)
            self.set_word_cloud_diy_button(False)
            self.stackedWidget.setCurrentIndex(2)

    def get_movie_html(self):
        header = {'User-Agent': str(random.choice(user_agents)),
                  'Host': 'movie.douban.com',
                  'Cookie': cookie
                  }
        url = r'https://movie.douban.com/subject/{}'.format(self.movie_id)
        self.movie_html = bs(requests.get(url, headers=header).text, 'html.parser')

    def set_movie_img(self):  # 展示图片
        img_url = self.movie_html.find('img').get('src')
        res = requests.get(img_url).content
        img = QImage.fromData(res)
        self.movie_image.setPixmap(QPixmap.fromImage(img))
        self.movie_image.setScaledContents(True)

    def set_movie_info_rate(self, movie_cmts):  # 展示星级相关的信息
        self.isShow = True
        self.movie_cmts_rate = [rate.string for rate in movie_cmts.find_all('span', "rating_per")]
        cmts = movie_cmts.find('strong').string
        people = movie_cmts.find('span', property="v:votes").string
        movie_cmts_text = '豆瓣评分：{}\n{}人评价\n5星：{}\n4星：{}\n3星：{}\n2星：{}\n1星：{}\n'.format(cmts, people,
                                                                                       *self.movie_cmts_rate)
        self.movie_info_cmts.setText(movie_cmts_text)

    def set_movie_info(self):  # 展示简介相关的信息
        info_main = self.movie_html.find('div', id='info').text
        try:  # 电影可能没剧情简介
            info_main = info_main + '\n剧情简介:' + self.movie_html.find('span', property="v:summary").text.replace(' ', '')
        except:
            info_main += '\n剧情简介:\n无'
        self.movie_info_main.setText(info_main)
        movie_cmts = self.movie_html.find('div', id="interest_sectl")
        try:  # 电影可能没星级信息
            isShow_txt = movie_cmts.find('div', "rating_sum").string.replace(' ', '').replace('\n', '')
            if isShow_txt == '尚未上映' or isShow_txt == '暂无评分':
                self.isShow = False
                self.movie_info_cmts.setText('尚未上映')
            else:
                self.set_movie_info_rate(movie_cmts)
        except:
            self.set_movie_info_rate(movie_cmts)

    def set_movie_data_all(self):
        if self.movie_id != self.movie_id_save1:  # 选了相同的电影就没必要再 requests 了
            self.get_movie_html()
            self.set_movie_img()
            self.set_movie_info()
        else:
            pass

    def get_cmts_html(self, page=0):
        header = {'User-Agent': str(random.choice(user_agents)),
                  'Host': 'movie.douban.com',
                  'Cookie': cookie
                  }
        url = r'https://movie.douban.com/subject/{}/comments?start={}&limit=20&status=P&sort=new_score'.format(
            self.movie_id, str(page))
        html = bs(requests.get(url, headers=header).text, 'html.parser')
        return html

    def put_cmts_to_file(self):
        self.progress_bar.setVisible(True)
        cmt_text = open(r"cmts.txt", 'w', encoding='utf-8')
        cmt_text.truncate(0)
        page = 0
        bar_value = 0
        for _ in range(10):  # 读10页差不多了
            html = self.get_cmts_html(page)
            cmts = html.find_all('span', 'short')
            for cmt in cmts:
                try:
                    cmt_text.write(cmt.string + '\n')
                except:
                    break
            self.progress_bar.setValue(bar_value)
            bar_value += 10  # 刷新进度条
            page += 20
        cmt_text.close()

    @staticmethod
    def word_washing(dirty_words, user_words={}):  # 清洗评论
        stopwords = {}.fromkeys([line.rstrip() for line in open(r'stopword.txt', 'r', encoding='utf-8')])
        stopwords.update(user_words)
        clean_words = ''
        for word in dirty_words:
            if len(word) > 1 and word not in stopwords:
                clean_words = clean_words + word + ' '
        return clean_words

    def word_cloud(self, isSimple, user_words={}):
        # 重复点击词云按钮;并且选的不是自定义模式;并且上一次是默认默认模式，就没必要再来一次了
        if self.movie_id == self.movie_id_save2 and isSimple and self.word_cloud_type == 0:
            self.stackedWidget.setCurrentIndex(3)
        else:
            self.put_cmts_to_file()
            file = open(r"cmts.txt", 'r', encoding='utf-8')
            cmts = file.read()
            file.close()
            dirty_words = jieba.lcut(cmts)
            clean_words = self.word_washing(dirty_words, user_words)
            words = wordcloud.WordCloud(font_path=r'simhei.ttf', width=977, height=753, background_color='white')
            words.generate(clean_words)
            self.progress_bar.setValue(100)
            words.to_file('word_cloud.jpg')
            img = QPixmap('word_cloud.jpg')
            self.word_cloud_img.setPixmap(img)
            self.word_cloud_img.setScaledContents(True)
            self.progress_bar.setVisible(False)
            self.progress_bar.setValue(0)
            self.stackedWidget.setCurrentIndex(3)

    def add_user_words(self):
        text = self.user_words_add_line.text()
        if text:
            self.user_words[text] = None
            self.user_words_add_line.setText('')
        else:
            pass

    def finish_user_words(self):
        self.word_cloud(False, self.user_words)
        self.set_word_cloud_diy_button(False)
        self.word_cloud_type = 1
        self.word_cloud_box.setCurrentIndex(0)

    def clear_user_words(self):
        self.user_words = {}

    def set_word_cloud_diy_button(self, flag):  # 词云自定义模式按钮
        self.user_words_add_line.setVisible(flag)
        self.add_button.setVisible(flag)
        self.add_finish_button.setVisible(flag)
        self.clear_user_words_button.setVisible(flag)

    def word_cloud_choice(self):  # 词云接口
        index = self.word_cloud_box.currentIndex()
        if index == 0:
            pass
        elif index == 1:
            self.word_cloud(True)
            self.word_cloud_box.setCurrentIndex(0)
            self.word_cloud_type = 0
        elif index == 2:
            self.set_word_cloud_diy_button(True)

    def cmts_rate_show_init(self):  # 画图界面初始化
        self.Fig = MyFigure(self.movie_cmts_rate, width=3, height=2, dpi=100)
        self.Fig.cmts_rate_draw(0)
        self.mpl_img.addWidget(self.Fig)
        self.stackedWidget.setCurrentIndex(4)

    def cmts_rate_show(self):
        self.step += 1
        if self.step == 1:  # 第一次进入此界面就不删
            self.cmts_rate_show_init()
        else:
            sip.delete(self.Fig)
            self.cmts_rate_show_init()

    def cmts_rate_show_changed(self, n):
        sip.delete(self.Fig)
        self.Fig = MyFigure(self.movie_cmts_rate, width=3, height=2, dpi=100)
        self.Fig.cmts_rate_draw(n)
        self.mpl_img.addWidget(self.Fig)
        self.stackedWidget.setCurrentIndex(4)

    def set_short_cmts(self):  # 评论界面初始化，默认展示第一页评论
        cmts_html = self.get_cmts_html(self.page)
        cmts = cmts_html.find('div', 'mod-bd', id='comments').find_all('div', 'comment')
        text = ''
        for tag in cmts:
            text += '"{}"：\n{}\n\n'.format(tag.find('a', '').string, tag.find('span', 'short').string)
        self.cmts_box.setText(text)
        self.stackedWidget.setCurrentIndex(5)

    def previous_cmts_page(self):  # 上一页评论
        if self.page == 0:
            return
        self.page -= 20
        self.set_short_cmts()

    def next_cmts_page(self):  # 下一页评论
        self.page += 20
        self.set_short_cmts()

    def choice_cmts_page(self):
        self.page = (self.which_page_button.value() - 1) * 20
        self.set_short_cmts()

    def page6_init(self):  # 退出评论界面后需要初始化评论界面
        self.page = 0
        self.which_page_button.setValue(1)

    def open_in_browser(self):
        QDesktopServices.openUrl(QUrl(r'https://movie.douban.com/subject/{}'.format(self.movie_id)))

    def get_pre_video_list(self):
        url = r'https://movie.douban.com/subject/{}/trailer#trailer'.format(self.movie_id)
        header = {'User-Agent': str(random.choice(user_agents)),
                  'Host': 'movie.douban.com',
                  'Cookie': cookie
                  }
        pre_video_html = bs(requests.get(url, headers=header).text, 'html.parser').find_all('ul', 'video-list')
        if pre_video_html:
            self.pre_video_url_list = []
            self.pre_video_name_list = []
            for item in pre_video_html:
                pre_video_li = item.find_all('li')
                self.pre_video_url_list += [i.find('a').get('href') for i in pre_video_li]
                self.pre_video_name_list += [i.find_all('a')[1].string.strip() for i in pre_video_li]
            self.pre_video_list = dict(zip(self.pre_video_name_list, self.pre_video_url_list))
        else:
            self.pre_video_url_list = []
            self.pre_video_name_list = []
            self.pre_video_list = {}

    def set_pre_video_name(self):
        name_list = QStringListModel()
        list1 = ['选择一部'] + self.pre_video_name_list
        name_list.setStringList(list1)
        self.choice_pre_video_button.setModel(name_list)

    def set_page7_button(self, flag):
        self.play_button.setDisabled(flag)
        self.pause_button.setDisabled(flag)
        self.continue_button.setDisabled(flag)

    def go_page7_pre_video_show(self):  # 视频界面初始化
        if self.movie_id_save3 != self.movie_id:  # 防止重复
            self.get_pre_video_list()
            self.set_pre_video_name()
            self.set_page7_button(True)
            self.stackedWidget.setCurrentIndex(6)
        else:
            self.stackedWidget.setCurrentIndex(6)

    def choice_pre_video(self):  # 选到了可播放项即按钮可工作
        if self.choice_pre_video_button.currentIndex() != 0:
            self.set_page7_button(False)
        else:
            self.set_page7_button(True)

    @staticmethod
    def get_pre_video(pre_video_url):
        header = {'User-Agent': str(random.choice(user_agents)),
                  'Host': 'movie.douban.com',
                  'Cookie': cookie
                  }
        pre_video = bs(requests.get(pre_video_url, headers=header).text, 'html.parser').find('source').get('src')
        return pre_video

    def pre_video_play(self):
        url = self.get_pre_video(self.pre_video_list[self.choice_pre_video_button.currentText()])
        self.player.setMedia(QMediaContent(QUrl(url)))  # 设定网络流
        self.th = threading.Thread(target=self.create_thread_play())  # 由于视频会占用进程，所以为其新开线程
        self.th.start()
        self.create_thread_play()

    def create_thread_play(self):
        self.player.play()

    def close_video(self):
        self.player.stop()

    def pre_video_pause(self):
        self.player.pause()

    def pre_video_continue(self):
        self.player.play()

    def __del__(self):
        print('closed successfully')


if __name__ == '__main__':

    app = QtWidgets.QApplication(sys.argv)
    splash = QtWidgets.QSplashScreen(QPixmap('splash.png'))
    splash.show()
    app.processEvents()
    my_pyqt_form = Main_Function()
    my_pyqt_form.show()
    splash.finish(my_pyqt_form)
    sys.exit(app.exec_())
