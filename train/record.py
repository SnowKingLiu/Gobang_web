# _*_ coding: utf-8 _*_
# by:Snowkingliu
# 2017/12/7 上午9:50
import json
import os

from Gobang_web import singleton


@singleton
class Record(object):
    def __init__(self):
        # 训练数据
        self.record = []
        # 本局所有走位
        self.this_game = []
        self.ini_record()

    def ini_record(self):
        # 获得record_data数据
        self.read_res_file()

    def read_res_file(self):
        """
        获得record_data数据
        :return:
        """
        if not os.path.exists("static/file/record.txt"):
            # 新建该文件
            fp = open("static/file/record.txt", mode="w")
            fp.close()
            self.record = []
        else:
            # 以只读的方式打开文件，若不存在则新建
            fp = open("static/file/record.txt", mode="r")
            # load record data数据
            self.record = [json.loads(rd) for rd in fp.readlines() if rd is not '\n']

    def get_record(self):
        """
        返回record
        :return:
        """
        return self.record

    def update_record(self, new_record):
        """
        更新record
        :param new_record:
        :return:
        """
        self.record = new_record

    def write_to_file(self):
        """
        更新文件
        :return:
        """
        fp = open("static/file/record.txt", mode="w")
        for a_line in self.record:
            fp.writelines(json.dumps(a_line) + '\n')
        fp.close()

    def add_this_game(self, plans):
        """
        保存本局的所有走位
        :param plans:[(int)status, int(user), (str)plan]
        :return:
        """
        self.this_game.append(plans)

    def update_win_indexes(self, win):
        """
        更新数据的权重
        :param win: 是否赢
        :return:
        """
        this_game_len = len(self.this_game)
        for i in range(this_game_len):
            game = self.this_game[i]
            if game[1] == 1:
                user = 0
            else:
                user = 1
            if win:
                self.record[game[0]][1][user][game[2]][1] += 1 - i / float(this_game_len)
            else:
                self.record[game[0]][1][user][game[2]][2] += 1 - i / float(this_game_len)

    def add_status(self, original_chess_box, my_plan, user):
        """
        新添一行数据
        :param original_chess_box:
        :param my_plan:
        :param user:
        :return:
        """
        # 如果黑棋
        if user is 1:
            new_record = [original_chess_box, [{my_plan: [1, 0, 0]}, {}]]
        else:
            new_record = [original_chess_box, [{}, {my_plan: [1, 0, 0]}]]
        self.record.append(new_record)
        return len(self.record) - 1

    def clean(self):
        """
        清空数据
        :return:
        """
        # 训练数据
        self.record = []
        # 本局所有走位
        self.this_game = []


