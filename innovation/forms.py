from django import forms
from .models import InnovationProject


class InnovationProjectForm(forms.ModelForm):
    class Meta:
        model  = InnovationProject
        fields = ['title', 'description', 'problem_solved', 'technologies',
                  'project_type', 'categories', 'cover_image', 'document',
                  'demo_url', 'repository_url', 'institution']
        widgets = {
            'title':          forms.TextInput(attrs={'class': 'form-control'}),
            'description':    forms.Textarea(attrs={'class': 'form-control', 'rows': 5}),
            'problem_solved': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'technologies':   forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Python, React, Django'}),
            'project_type':   forms.Select(attrs={'class': 'form-select'}),
            'categories':     forms.CheckboxSelectMultiple(),
            'demo_url':       forms.URLInput(attrs={'class': 'form-control'}),
            'repository_url': forms.URLInput(attrs={'class': 'form-control'}),
            'institution':    forms.TextInput(attrs={'class': 'form-control'}),
        }
