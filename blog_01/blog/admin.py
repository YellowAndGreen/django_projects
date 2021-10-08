from django.contrib import admin
from .models import Post


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    # 实例列表
    list_display = ('title', 'slug', 'author', 'publish', 'status')
    # 右侧筛选栏
    list_filter = ('status', 'created', 'publish', 'author')
    # 搜索栏
    search_fields = ('title', 'body')
    # 在添加新post时，自动以title填充slug
    prepopulated_fields = {'slug': ('title',)}
    raw_id_fields = ('author',)
    date_hierarchy = 'publish'
    ordering = ('status', 'publish')
