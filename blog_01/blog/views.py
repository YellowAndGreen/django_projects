from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView

from .models import Post


# def post_list(request):
#     object_list = Post.published.all()
#     paginator = Paginator(object_list, 3)  # 3 posts in each page
#     page = request.GET.get('page')         # 获得当前页数
#     try:
#         posts = paginator.page(page)       # 当前页的post
#     except PageNotAnInteger:
#         # If page is not an integer deliver the first page
#         posts = paginator.page(1)
#     except EmptyPage:
#         # If page is out of range deliver last page of results
#         posts = paginator.page(paginator.num_pages)
#     return render(request,
#                   'blog/post/list.html',
#                   {'page': page,
#                    'posts': posts})


def post_detail(request, year, month, day, post):
    post = get_object_or_404(Post, slug=post,            # 做匹配
                             status='published',
                             publish__year=year,
                             publish__month=month,
                             publish__day=day)
    return render(request,
                  'blog/post/detail.html',
                  {'post': post})


class PostListView(ListView):
    queryset = Post.published.all()
    # 默认的上下文名称为object_list
    context_object_name = 'posts'
    paginate_by = 3
    # 传给模版的名称为page_obj
    template_name = 'blog/post/list.html'
