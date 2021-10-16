import datetime
from django.utils import timezone
from django.contrib.contenttypes.models import ContentType
from .models import Action


# 用于创建用户行为并保存
def create_action(user, verb, target=None):
    # check for any similar action made in the last minute
    # 避免多次点击造成多次记录
    now = timezone.now()
    last_minute = now - datetime.timedelta(seconds=60)
    similar_actions = Action.objects.filter(user_id=user.id,
                                            verb=verb,
                                            created__gte=last_minute)  # gte：大于等于
    # 获取目标对象的ContentType，过滤目标和id(primary key)
    if target:
        target_ct = ContentType.objects.get_for_model(target)
        similar_actions = similar_actions.filter(
            target_ct=target_ct,
            target_id=target.id)
    if not similar_actions:
        # no existing actions found
        action = Action(user=user, verb=verb, target=target)
        action.save()
        return True
    return False
