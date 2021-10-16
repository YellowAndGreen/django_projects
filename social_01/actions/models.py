from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType


# Create your models here.
class Action(models.Model):
    user = models.ForeignKey("auth.User", related_name="action", db_index=True, on_delete=models.CASCADE)
    # 定义用户操作的动词
    verb = models.CharField(max_length=255)
    created = models.DateTimeField(auto_now_add=True, db_index=True)
    # 指向ContentType模型
    target_ct = models.ForeignKey(ContentType, blank=True, null=True, related_name="target_obj",
                                  on_delete=models.CASCADE)
    # 保存相关对象的primary key
    target_id = models.PositiveIntegerField(null=True, blank=True, db_index=True)
    # GenericForeignKey不会在数据库中创建字段
    target = GenericForeignKey("target_ct", "target_id")

    class Meta:
        ordering = ("-created",)
