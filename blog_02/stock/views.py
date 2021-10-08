from django.shortcuts import render
import baostock as bs
import pandas as pd
import json
from datetime import datetime
from .forms import StockQueryForm


def test(request):
    query = False
    cd = False
    code = "1"
    if request.method == 'POST':
        # Form was submitted
        form = StockQueryForm(request.POST)
        # 表单不合法则直接报form.errors，因此不需要其他处理

        if form.is_valid():
            # Form fields passed validation
            # 将表单数据转换为一致的格式，删除没有验证通过的部分
            cd = form.cleaned_data
            # 返回的是json格式，必须取出
            code = cd["code"]
            query = True
    else:
        query = False
        cd = False
        form = StockQueryForm()
    return render(request, 'stock/index.html', {"code": code, 'form': form, "query": query})
