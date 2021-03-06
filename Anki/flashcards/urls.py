from django.urls import path

from flashcards.views import *

app_name = 'flashcards'
urlpatterns = [
    path('', index, name='dashboard'),
    # path('<slug:category_slug>/', views.product_list, name="product_list_by_category"),
    path('<int:pk>', CardDetailView.as_view(), name='card_detail'),
    path('next/', nextcardview, name='next'),
    path("recite/<int:card_id>/<int:rank>", cardreciteview, name="recite"),
    path("recitedata/", recitedatadisplay, name="display"),
    path('search/', search, name='search'),
    path('undo/<int:card_id>', undo, name='undo'),
    path('undo_list/<int:card_id>/<int:list_id>/<int:progress>/', undo_list, name='undo_list'),
    path('websearch/', websearch, name='websearch'),
    path('dict/', dict_search, name='dict'),
    path('create_list/', create_wordlist, name='create_list'),
    path('delete_wordlist/<int:wordlist_id>/', delete_wordlist, name='delete_wordlist'),
    path('recite_wordlist/<int:wordlist_id>/<int:progress>/<int:rank>/', recite_wordlist, name='recite_wordlist'),
]
