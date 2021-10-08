from django import forms


class StockQueryForm(forms.Form):
    # 每个表单字段都有一个相对应的 控件Widget类 ，这个控件类又有对应的HTML表单控件，比如 <input type="text"> 。
    code = forms.CharField(max_length=25)
