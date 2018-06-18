import os
import shutil
import zipfile

from django.http import JsonResponse
from django.shortcuts import render
from codeCount import settings


# Create your views here.


def index(request):
    if request.method == 'POST':
        file_obj = request.FILES.get('tp')
        file_name = file_obj.name
        file_size = file_obj.size
        with open(file_name, 'wb') as f:
            for line in file_obj.chunks():
                f.write(line)

        # zip的文件路径
        zip_path = os.path.join(settings.BASE_DIR, file_name)
        print(zip_path)
        z = zipfile.ZipFile(zip_path, 'r')
        # 解压路径
        extract_path = os.path.join(settings.BASE_DIR, 'zip')
        z.extractall(extract_path)
        z.close()
        # code_count(extract_path)
        code_sum, code_lines, comment_lines, blank_lines = code_count(extract_path)

        code_details = {
            'size': file_size,
            'code_sum': code_sum,
            'code_lines': code_lines,
            'comment_lines': comment_lines,
            'blank_lines': blank_lines
        }

        return render(request, 'code_lines.html', {'code': code_details})

    return render(request, 'index.html')


# ajax 异步请求
def get_code_ajax(request):
    if request.method == 'POST':
        file_obj = request.FILES.get('tp')
        file_name = file_obj.name
        file_size = file_obj.size
        with open(file_name, 'wb') as f:
            for line in file_obj.chunks():
                f.write(line)

        # zip的文件路径
        zip_path = os.path.join(settings.BASE_DIR, file_name)
        print(zip_path)
        z = zipfile.ZipFile(zip_path, 'r')
        # 解压路径
        extract_path = os.path.join(settings.BASE_DIR, 'zip')
        z.extractall(extract_path)
        z.close()
        # code_count(extract_path)
        code_sum, code_lines, comment_lines, blank_lines = code_count(extract_path)

        code_details = {
            'file_size': file_size,
            'code_sum': code_sum,
            'code_lines': code_lines,
            'comment_lines': comment_lines,
            'blank_lines': blank_lines
        }
        return JsonResponse(code_details)
    return render(request, 'index2.html')

# 统计代码
def code_count(path):
    """
    统计代码
    :param path:
    :return:
    """
    print(path)
    # 统计代码行
    code_sum = 0  # python 文件总行数
    code_lines = 0  # 代码行数
    comment_lines = 0  # 注释行数
    blank_lines = 0  # 空行数

    # 遍历文件夹
    for root, dirs, files in os.walk(path):
        # 循序判断文件
        for file_name in files:
            # 文件的完成路径
            file_path = os.path.join(root, file_name)
            # 分割路径 获取文件类型
            fname, fename = os.path.splitext(file_path)
            # 判断是否 .py

            if fename == '.py':
                # yes 统计代码行
                with open(file_path, 'r', encoding='utf-8') as f:
                    lines = f.readlines()

                    # 统计文件总行数
                    code_sum += len(lines)

                    tmp_comment = 0
                    flag = 0  # 0 非注释块  1 注释块

                    for line in lines:

                        # 去掉每行开头空白
                        line = line.strip()

                        # 判断当前模式 1
                        if tmp_comment:
                            # 判断注释块 是否结束
                            if line.endswith('"""') or line.endswith("'''"):
                                tmp_comment += 1
                                flag = 0
                                comment_lines += tmp_comment
                                tmp_comment = 0
                                continue
                            # 注释块没结束
                            tmp_comment += 1

                        else:
                            # 首先判断注释块
                            if line.startswith('"""') or line.startswith("'''"):
                                tmp_comment += 1
                                flag = 1
                                continue

                            if line == '':  # 判断空行
                                blank_lines += 1
                                continue

                            elif line.startswith("#"):  # 判断单行注释
                                comment_lines += 1
                                continue
                            else:
                                code_lines += 1  # 代码行

    # 删除文件夹
    shutil.rmtree(path)
    return code_sum, code_lines, comment_lines, blank_lines
