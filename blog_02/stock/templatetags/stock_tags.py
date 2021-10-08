from django import template
from django.db.models import Count
from django.utils.safestring import mark_safe
import markdown
import baostock as bs
import pandas as pd
import json
from datetime import datetime

register = template.Library()


@register.inclusion_tag('stock/k-line.html')
def show_latest_posts(code="sz.000725"):
    lg = bs.login()
    # 显示登陆返回信息
    print('login respond error_code:' + lg.error_code)
    print('login respond  error_msg:' + lg.error_msg)
    rs = bs.query_history_k_data_plus(code,
                                      "date,code,open,high,low,close,preclose,volume,amount,adjustflag,turn,"
                                      "tradestatus,pctChg,isST",
                                      start_date='2019-01-01', end_date='2019-12-31',
                                      frequency="d", adjustflag="3")
    print('query_history_k_data_plus respond error_code:' + rs.error_code)
    print('query_history_k_data_plus respond  error_msg:' + rs.error_msg)
    data_list = []
    while (rs.error_code == '0') & rs.next():
        # 获取一条记录，将记录合并在一起
        data_list.append(rs.get_row_data())
    result = pd.DataFrame(data_list, columns=rs.fields)
    # [open,close,low,high]
    data_stock = []
    for i in range(len(result["open"])):
        data_stock.append(
            [datetime.strftime(datetime.strptime(result["date"][i], "%Y-%m-%d"), "%Y/%m/%d"), float(result["open"][i]),
             float(result["close"][i]), float(result["high"][i]), float(result["low"][i])])

    return {'data_stock': json.dumps(list(data_stock))
            }
