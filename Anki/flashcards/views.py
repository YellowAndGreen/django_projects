from django.shortcuts import render, get_object_or_404, redirect

# Create your views here.
from django.views.generic.detail import DetailView
from django.views.generic.list import ListView
from .models import Card, Recitedata
from .forms import *
from django.db.models import Q
import random
from django.http import HttpResponse
from django.contrib.auth import authenticate, login


class CardListView(ListView):
    model = Card
    template_name = 'flashcards/list.html'


class CardDetailView(DetailView):
    model = Card
    template_name = 'flashcards/back3.html'


# 背诵
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
def nextcardview(request):
    card = Card.objects.filter(id=str(random.randrange(1, 7000, 1)))[0]
    return redirect(card.get_absolute_url())


# 展示数据
def recitedatadisplay(request):
    # 按rank排序，后续改进
    recitedata = Recitedata.objects.order_by("rank")
    # 使用set以防止card重复
    cards = set([data.card for data in recitedata])
    datas = [{'card': card, 'recitedata': card.recitedata.all()} for card in cards]
    return render(request,
                  'flashcards/recitedata.html',
                  {'datas': datas})


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
    return render(request, 'flashcards/search.html', {'cards': cards, 'searchvalue': cd['query'], 'form': form})


# 首页
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
def undo(request, card_id):
    # 需要撤回的卡片和需要删除背诵记录的卡是一张卡
    card = Card.objects.filter(id=card_id)
    card[0].recitedata.latest('date').delete()

    return redirect(card[0].get_absolute_url())


def user_login(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            user = authenticate(request, username=cd['username'], password=cd['password'])
            if user is not None:
                if user.is_active:
                    login(request, user)
                    return HttpResponse('Authenticated successfully!')
                else:
                    return HttpResponse('Disabled Account')
            else:
                return HttpResponse('Invalid Login')
    else:
        form = LoginForm()
    return render(request, 'flashcards/account/login.html', {'form': form})
