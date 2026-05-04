from django import forms
from .models import Resume


class ResumeUploadForm(forms.ModelForm):
    """简历上传表单"""

    class Meta:
        model = Resume
        fields = ['file']
        widgets = {
            'file': forms.FileInput(attrs={
                'accept': '.pdf,.doc,.docx',
                'class': 'form-control'
            })
        }

    def clean_file(self):
        """验证文件格式"""
        file = self.cleaned_data.get('file')
        if file:
            # 检查文件扩展名
            if not file.name.lower().endswith(('.pdf', '.doc', '.docx')):
                raise forms.ValidationError('仅支持PDF和Word格式')

            # 检查文件大小（限制10MB）
            if file.size > 10 * 1024 * 1024:
                raise forms.ValidationError('文件大小不能超过10MB')

        return file


class ResumeEditForm(forms.ModelForm):
    """简历编辑表单"""
    class Meta:
        model = Resume
        fields = ['name', 'gender', 'age', 'phone', 'email', 'education', 'school', 'major', 'work_years']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '请输入姓名'}),
            'gender': forms.Select(attrs={'class': 'form-control'}, choices=[
                ('', '请选择'),
                ('男', '男'),
                ('女', '女'),
            ]),
            'age': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '请输入年龄', 'min': '18', 'max': '100'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '请输入电话'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': '请输入邮箱'}),
            'education': forms.Select(attrs={'class': 'form-control'}, choices=[
                ('', '请选择'),
                ('高中', '高中'),
                ('专科', '专科'),
                ('本科', '本科'),
                ('硕士', '硕士'),
                ('博士', '博士'),
            ]),
            'school': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '请输入毕业院校'}),
            'major': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '请输入专业'}),
            'work_years': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '请输入工作年限', 'min': '0', 'max': '50'}),
        }
        labels = {
            'name': '姓名',
            'gender': '性别',
            'age': '年龄',
            'phone': '电话',
            'email': '邮箱',
            'education': '学历',
            'school': '毕业院校',
            'major': '专业',
            'work_years': '工作年限',
        }