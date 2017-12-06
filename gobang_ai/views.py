import os

from django.http import JsonResponse
from django.shortcuts import render
import json
import numpy as np
from functools import reduce


def send_chessboard(request):
    """
    返回最佳的走步
    :param request:
    :return:
    """
    # 获得棋盘矩阵
    chess_box = np.array(json.loads(request.POST['chessBox']))
    # 获得record_data数据
    record_data = read_res_file()
    # 匹配最接近的局势
    sorted_indices = get_similarity_chess(chess_box, record_data)

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


def get_similarity_chess(chess_box, record_data):
    # 获取棋盘的有效位置
    top, left, bottom, right = get_chess_rectangle(chess_box)
    # 获取所有的棋盘变形
    slide_transitions = get_all_chess_transition(chess_box, top, left, bottom, right)
    slide_transitions_size = len(slide_transitions)
    # 获取numpy的训练集二维矩阵
    record_chess = np.array([np.array(reduce(lambda x, y: x+y, rd[0])) for rd in record_data])
    record_chess_size = record_chess.shape[0]
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
    return min_variances.argsort()


def get_chess_rectangle(chess_box):
    # 获取有效部分上左下右，的起始/终止位置
    top = left = bottom = right = -1
    for i in range(15):
        if sum(chess_box[i, :]) and top == -1:
            top = i
        if sum(chess_box[:, i]) and left == -1:
            left = i
        if sum(chess_box[14 - i, :]) and bottom == -1:
            bottom = 14 - i
        if sum(chess_box[:, 14 - i]) and right == -1:
            right = 14 - i
        if top is not -1 and left is not -1 and bottom is not -1 and right is not -1:
            break
    return top, left, bottom, right


def get_all_chess_transition(chess_box, top, left, bottom, right):
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


