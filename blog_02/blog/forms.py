from django import forms
from .models import Comment


class EmailPostForm(forms.Form):
    # 每个表单字段都有一个相对应的 控件Widget类 ，这个控件类又有对应的HTML表单控件，比如 <input type="text"> 。
    name = forms.CharField(max_length=25)
    email = forms.EmailField()
    to = forms.EmailField()
    # required非必填
    comments = forms.CharField(required=False,
                               widget=forms.Textarea)


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('name', 'email', 'body')
