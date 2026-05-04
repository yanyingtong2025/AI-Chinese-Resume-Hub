from django import forms
from .models import Job, MatchResult


class JobCreateForm(forms.ModelForm):
    """创建岗位表单"""

    class Meta:
        model = Job
        fields = [
            'title', 'department', 'location', 'salary_min', 'salary_max',
            'education_required', 'work_years_required', 'skills_required',
            'job_description', 'job_requirements'
        ]
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'department': forms.TextInput(attrs={'class': 'form-control'}),
            'location': forms.TextInput(attrs={'class': 'form-control'}),
            'salary_min': forms.NumberInput(attrs={'class': 'form-control'}),
            'salary_max': forms.NumberInput(attrs={'class': 'form-control'}),
            'education_required': forms.Select(attrs={'class': 'form-control'}),
            'work_years_required': forms.NumberInput(attrs={'class': 'form-control'}),
            'skills_required': forms.TextInput(attrs={'class': 'form-control'}),
            'job_description': forms.Textarea(attrs={'class': 'form-control', 'rows': 5}),
            'job_requirements': forms.Textarea(attrs={'class': 'form-control', 'rows': 5}),
        }

    def clean(self):
        """验证薪资范围"""
        cleaned_data = super().clean()
        salary_min = cleaned_data.get('salary_min')
        salary_max = cleaned_data.get('salary_max')

        if salary_min and salary_max and salary_min > salary_max:
            raise forms.ValidationError('最低薪资不能大于最高薪资')

        return cleaned_data


class JobEditForm(JobCreateForm):
    """编辑岗位表单"""
    is_active = forms.BooleanField(required=False, label='启用该岗位')

    class Meta(JobCreateForm.Meta):
        fields = JobCreateForm.Meta.fields + ['is_active']


class MatchFilterForm(forms.Form):
    """匹配结果筛选表单"""
    min_score = forms.FloatField(
        required=False,
        min_value=0,
        max_value=100,
        label='最低分数',
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )
    education = forms.ChoiceField(
        required=False,
        choices=[('', '全部')] + [
            ('博士', '博士'),
            ('硕士', '硕士'),
            ('本科', '本科'),
            ('大专', '大专'),
        ],
        label='学历',
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    min_work_years = forms.IntegerField(
        required=False,
        min_value=0,
        label='最低工作年限',
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )


class MatchStatusUpdateForm(forms.ModelForm):
    """更新匹配状态表单"""
    class Meta:
        model = MatchResult
        fields = ['status', 'hr_notes']
        widgets = {
            'status': forms.Select(attrs={'class': 'form-control'}),
            'hr_notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 4})
        }
