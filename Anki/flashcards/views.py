from django.shortcuts import render, get_object_or_404, redirect

# Create your views here.
from django.views.generic.detail import DetailView
from django.views.generic.list import ListView
from .models import Card, Recitedata, WordList
from .forms import *
from django.db.models import Q
import random
from django.contrib.auth.decorators import login_required
from .web_query import find_synonym
from django.contrib.auth.mixins import LoginRequiredMixin
from readmdict import MDX
import json


class CardListView(ListView):
    model = Card
    template_name = 'flashcards/list.html'


class CardDetailView(LoginRequiredMixin, DetailView):
    model = Card
    template_name = 'flashcards/back3.html'


# 背诵
@login_required
def cardreciteview(request, card_id, rank):
    # 获取card实例
    card = get_object_or_404(Card, id=card_id)
    # 创建并保存
    recitedata = Recitedata(rank=rank, card=card)
    recitedata.save()
    # 生成随机数并跳转至下一卡片
    card = Card.objects.filter(id=str(random.randrange(1, 7000, 1)))[0]
    return redirect(card.get_absolute_url())


# 下一张卡片
@login_required
def nextcardview(request):
    card = Card.objects.filter(id=str(random.randrange(1, 7000, 1)))[0]
    return redirect(card.get_absolute_url())


# 展示数据
@login_required
def recitedatadisplay(request):
    # 按rank排序，后续改进
    recitedata = Recitedata.objects.order_by("rank")
    # 使用set以防止card重复
    cards = set([data.card for data in recitedata])
    datas = [{'card': card, 'recitedata': card.recitedata.all()} for card in cards]
    return render(request,
                  'flashcards/recitedata.html',
                  {'datas': datas})


@login_required
def search(request):
    cards = []
    cd = {"query": ''}
    form = SearchForm(request.GET)
    if form.is_valid():
        cd = form.cleaned_data
        cards = Card.objects.filter(
            Q(question__icontains=cd['query']) | Q(example__icontains=cd['query']))
    if cd['query'] == '':
        form = SearchForm()
    # 将搜索字段替换为红色
    for card in cards:
        card.question = card.question.replace(cd['query'], "<span id='red'><b>" + cd['query'] + "</b></span>")
        card.example = card.example.replace(cd['query'], "<span id='red'><b>" + cd['query'] + "</b></span>")
    return render(request, 'flashcards/search.html', {'cards': cards, 'searchvalue': cd['query'], 'form': form})


# 首页
@login_required
def index(request):
    cards = Card.objects.all()
    type_proportion = {
        'cihui': len(Card.objects.filter(group__startswith='词汇')),
        'duanyu': len(Card.objects.filter(group__startswith='短语')),
        'bianxi': len(Card.objects.filter(group__startswith='辨析'))
    }

    return render(request, 'flashcards/anki.html',
                  {'len': len(cards),
                   'type_proportion': type_proportion}, )


# 删除背诵记录
@login_required
def undo(request, card_id):
    # 需要撤回的卡片和需要删除背诵记录的卡是一张卡
    card = Card.objects.filter(id=card_id)
    card[0].recitedata.latest('date').delete()

    return redirect(card[0].get_absolute_url())


# 网络搜索
@login_required
def websearch(request):
    cd = {"query": ''}
    form = SearchForm(request.GET)
    if form.is_valid():
        cd = form.cleaned_data
        words = find_synonym(cd['query'])
    else:
        form = SearchForm()
        words = []
    return render(request, 'flashcards/webquery.html',
                  {"words": words, 'searchvalue': cd['query'], 'form': form}, )


@login_required
def dict_search(request):
    cd = {"query": ''}
    form = SearchForm(request.GET)
    if form.is_valid():
        cd = form.cleaned_data
        # 加载mdx文件
        filename = "E:\\All Files\\GoldenDict\\content\\新建文件夹\\剑桥高阶.mdx"
        headwords = [*MDX(filename)]  # 单词名列表
        items = [*MDX(filename).items()]  # 释义html源码列表
        # if len(headwords) == len(items):
        #     print(f'加载成功：共{len(headwords)}条')
        # else:
        #     print(f'【ERROR】加载失败{len(headwords)}，{len(items)}')

        # 查词，返回单词和html文件
        queryWord = cd['query']
        # print(headwords[120:123])
        html_result = ''
        try:
            wordIndex = headwords.index(queryWord.encode())
            word, html = items[wordIndex]
            word, html_result = word.decode(), html.decode()
        except ValueError:
            html_result = 'No Results!'
    else:
        form = SearchForm()
        html_result = ''

    return render(request, 'flashcards/dict.html',
                  {'html_result': html_result, 'form': form, 'searchvalue': cd['query']})


@login_required
def create_wordlist(request):
    cd = {"query": 'list'}
    form = SearchForm(request.GET)
    if form.is_valid():
        cd = form.cleaned_data
    rank = []
    wordlist = WordList(owner=request.user, name=cd['query'], wordlist=rank)
