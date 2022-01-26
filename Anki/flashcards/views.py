import json
import random

from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404, redirect
# Create your views here.
from django.views.generic.detail import DetailView
from django.views.generic.list import ListView
from readmdict import MDX

from .forms import *
from .models import *
from .web_query import find_synonym


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
    form = SearchForm()
    type_proportion = {
        'cihui': len(Card.objects.filter(group__startswith='词汇')),
        'duanyu': len(Card.objects.filter(group__startswith='短语')),
        'bianxi': len(Card.objects.filter(group__startswith='辨析'))
    }

    return render(request, 'flashcards/anki.html',
                  {'len': len(cards),
                   'type_proportion': type_proportion,
                   'lenlist': len(WordList.objects.all()),
                   'form': form, },

                  )


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
        filename = "flashcards/static/dict/剑桥高阶.mdx"
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


def create_wordlist(request):
    cd = {"query": 'list'}
    form = SearchForm(request.GET)
    if form.is_valid():
        cd = form.cleaned_data
    # 找到最近的三个复习data并累计，生成一个字典
    rank_sum_dict = map(lambda card: {'id': card.id, 'rank_sum': sum(
        sorted([Recitedata.rank for Recitedata in card.recitedata.order_by('-date')], reverse=True)[0:3])
    if len(card.recitedata.all()) > 2
    else sum([Recitedata.rank for Recitedata in card.recitedata.order_by('-date')])}
                        , Card.objects.all())
    # 按rank排序，取前五十个值
    # 不知道为什么id列表总为空
    # id_list = [dic['id'] for dic in sorted(list(rank_sum_dict), key=lambda dic: dic['rank_sum'], reverse=True)[0:50]]
    # id_list = list(
    #     map(lambda dic: dic['id'], sorted(list(rank_sum_dict), key=lambda dic: dic['rank_sum'], reverse=True)[0:50]))
    # print(id_list)
    sort_list = sorted(list(rank_sum_dict), key=lambda dic: dic['rank_sum'], reverse=True)[0:50]
    wordlist = WordList(owner=request.user, name=cd['query'], wordlist=json.dumps(sort_list)
                        , len_list=len(sort_list))
    wordlist.save()


@login_required
def recite_wordlist(request, wordlist_id, progress, rank):
    wordlist = WordList.objects.filter(id=wordlist_id)[0]
    # json解析单词列表id
    id_list = list(map(lambda dic: dic['id'], json.loads(wordlist.wordlist)))
    if progress != 0:
        # 获取当前card实例
        current_card = get_object_or_404(Card, id=id_list[progress])
        # 创建并保存记忆数据
        recitedata = Recitedata(rank=rank, card=current_card)
        recitedata.save()

        # 计算完成度
        wordlist.progress = progress + 1
        percentage = int((wordlist.progress / wordlist.len_list)*100)

        # 更新进度
        wordlist.save()
    else:
        # 判断是刚进入还是进入后第一次提交卡片，若提交，则更新进度
        if rank > 0:
            # 计算完成度
            percentage = int((wordlist.progress / wordlist.len_list)*100)
            wordlist.progress = progress + 1
            # 更新进度
            wordlist.save()
        else:
            percentage = 0
    # 获取下一个单词
    next_word = get_object_or_404(Card, id=id_list[progress])

    return render(request, 'flashcards/recite_wordlist.html',
                  {
                      "percentage": percentage,
                      'object': next_word,
                      'progress': wordlist.progress,
                      'wordlist_id': wordlist_id,
                  })
