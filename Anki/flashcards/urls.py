from django.urls import path

from flashcards.views import *

app_name = 'flashcards'
urlpatterns = [
    path('dashboard/', index, name='dashboard'),
    # path('<slug:category_slug>/', views.product_list, name="product_list_by_category"),
    path('<int:pk>', CardDetailView.as_view(), name='card_detail'),
    path('next/', nextcardview, name='next'),
    path("recite/<int:card_id>/<int:rank>", cardreciteview, name="recite"),
    path("recitedata/", recitedatadisplay, name="display"),
    path('search/', search, name='search'),
    path('undo/<int:card_id>', undo, name='undo'),
    path('login/', user_login, name='login'),
]
