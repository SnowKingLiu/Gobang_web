import os
import json
from functools import reduce

from django.http import JsonResponse
from django.shortcuts import render

# Create your views here.
import numpy as np

from train.record import Record


def send_train_chessboard(request):
    # 获得棋盘矩阵
    original_chess_box = np.array(json.loads(request.POST['chessBox']))
    # 落子办法
    plan = json.loads(request.POST['plan'])
    # 落子角色
    user = int(request.POST['user'])
    if user is not 1 and user is not -1:
        return JsonResponse({})
    # 获得record_data数据
    # record_data = read_res_file()
    record_obj = Record()
    record_data = record_obj.get_record()
    # 查找是否已存在此训练数据
    status = get_same_chess(original_chess_box, record_data)
    my_plan = "{},{}".format(*plan)
    if status:
        # 如果黑棋
        if user is 1:
            # 如果走的是已经走过的
            if my_plan in record_data[status][1][0]:
                # 总数加一
                record_data[status][1][0][my_plan][0] += 1
            else:
                # 新建走位
                record_data[status][1][0][my_plan] = [1, 0, 0]
        # 如果白棋
        elif user is -1:
            # 如果走的是已经走过的
            if my_plan in record_data[status][1][1]:
                # 总数加一
                record_data[status][1][1][my_plan][0] += 1
            else:
                # 新建走位
                record_data[status][1][1][my_plan] = [1, 0, 0]
    else:
        # 新建一行数据并返回行数
        status = record_obj.add_status(original_chess_box.tolist(), my_plan, user)
    # 更新本局局势
    record_obj.add_this_game([status, user, my_plan])
    # 更新record
    record_obj.update_record(record_data)
    # 判断输赢
    win = game_over(original_chess_box, user, plan)
    if win:
        record_obj.update_win_indexes(win)
        record_obj.write_to_file()
        record_obj.clean()
    return JsonResponse({})


def read_res_file():
    """
    获得record_data数据
    :return:
    """
    if not os.path.exists("static/file/record.txt"):
        # 新建该文件
        fp = open("static/file/record.txt", mode="w")
        fp.close()
        return []
    else:
        # 以只读的方式打开文件，若不存在则新建
        fp = open("static/file/record.txt", mode="r")
        # load record data数据
        record_data = [json.loads(rd) for rd in fp.readlines()]
        return record_data


def get_same_chess(chess_box, record_data):
    # 获取棋盘的有效位置
    top, left, bottom, right = get_chess_rectangle(chess_box)
    # 获取所有的棋盘变形
    slide_transitions = get_all_chess_transition(chess_box, top, left, bottom, right)
    slide_transitions_size = len(slide_transitions)
    # 获取numpy的训练集二维矩阵
    record_chess = np.array([reduce(lambda x, y: x+y, rd[0]) for rd in record_data])
    record_chess_size = record_chess.shape[0]
    if record_chess_size == 0:
        return False
    # 行是训练集的数量，列是变形的种类总数。
    record_variances = np.zeros([record_chess_size, slide_transitions_size])
    # 循环棋盘变形
    # for a_chess in slide_transitions:
    for i in range(slide_transitions_size):
        # 使用K-MEAN算法
        diff_mat = np.tile(slide_transitions[i], (record_chess_size, 1)) - record_chess
        # 获取各项的差的平方
        sq_diff_mat = diff_mat ** 2
        # 若无axis参数代表全部相加，axis=0代表按照列相加，axis=1代表按照行相加，返回总数一个行向量（一维数组）
        sq_distance = sq_diff_mat.sum(axis=1)
        # 开根号
        distance = sq_distance ** 0.5
        record_variances[:, i] = distance

    # 这里代表获取最小的序列
    min_variances = record_variances.min(axis=1)
    min_sort = min_variances.argsort()
    if min(min_variances) == 0:
        return int(min_sort[0])
    else:
        return False


def get_chess_rectangle(chess_box):
    # 获取有效部分上左下右，的起始/终止位置
    top = left = bottom = right = -1
    for i in range(15):
        if np.any(chess_box[i, :]) and top is -1:
            top = i
        if np.any(chess_box[:, i]) and left is -1:
            left = i
        if np.any(chess_box[14 - i, :]) and bottom is -1:
            bottom = 14 - i
        if np.any(chess_box[:, 14 - i]) and right is -1:
            right = 14 - i
        if top is not -1 and left is not -1 and bottom is not -1 and right is not -1:
            break
    return top, left, bottom, right


def get_all_chess_transition(chess_box, top, left, bottom, right):
    if top == -1:
        return [np.zeros(225)]
    height = bottom - top + 1
    wide = right - left + 1
    # 截取有效区域
    valid_region = chess_box[top:bottom + 1, left:right + 1]
    # 滑动变换位置
    slide_transitions = []
    for j in range(15 - height):
        for i in range(15 - wide):
            original_mat = np.zeros([15, 15])
            original_mat[j:j + height, i:i + wide] = valid_region
            slide_transitions.append(original_mat.flatten("F"))
            slide_transitions.append(original_mat.T.flatten("F"))
            # 逆时针转90度
            mat = np.rot90(original_mat, 1)
            slide_transitions.append(mat.flatten("F"))
            slide_transitions.append(mat.T.flatten("F"))
            # 再逆时针转90度
            mat = np.rot90(mat, 1)
            slide_transitions.append(mat.flatten("F"))
            slide_transitions.append(mat.T.flatten("F"))
            # 再逆时针转90度
            mat = np.rot90(mat, 1)
            slide_transitions.append(mat.flatten("F"))
            slide_transitions.append(mat.T.flatten("F"))
    return slide_transitions


def game_over(original_chess_box, user, plan):
    """
    四个方向判断游戏是否结束
    :param original_chess_box:
    :param user:
    :param plan:
    :return: 若黑白有一方赢了就返回黑1，白-1，否则返回0
    """
    final_chess_box = original_chess_box
    final_chess_box[plan[0], plan[1]] = user
    # 横向
    for i in range(15):
        for j in range(11):
            if final_chess_box[i, j] != 0:
                if final_chess_box[i, j] == final_chess_box[i, j + 1] == final_chess_box[i, j + 2] \
                        == final_chess_box[i, j + 3] == final_chess_box[i, j + 4]:
                    return final_chess_box[i, j]
    # 纵向
    for i in range(11):
        for j in range(15):
            if final_chess_box[i, j] != 0:
                if final_chess_box[i, j] == final_chess_box[i + 1, j] == final_chess_box[i + 2, j] \
                        == final_chess_box[i + 3, j] == final_chess_box[i + 4, j]:
                    return final_chess_box[i, j]
    # 正斜向
    for i in range(11):
        for j in range(11):
            if final_chess_box[i, j] != 0:
                if final_chess_box[i, j] == final_chess_box[i + 1, j + 1] == final_chess_box[i + 2, j + 2] \
                        == final_chess_box[i + 3, j + 3] == final_chess_box[i + 4, j + 4]:
                    return final_chess_box[i, j]
    # 反斜向
    for i in range(11):
        for j in range(11):
            if final_chess_box[i, j + 4] != 0:
                if final_chess_box[i, j + 4] == final_chess_box[i + 1, j + 3] == final_chess_box[i + 2, j + 2] \
                        == final_chess_box[i + 3, j + 1] == final_chess_box[i + 4, j]:
                    return final_chess_box[i, j]

    return 0


