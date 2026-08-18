from django import forms
from .models import ResearchPaper, ResearchProject


class ResearchPaperForm(forms.ModelForm):
    class Meta:
        model  = ResearchPaper
        fields = ['title', 'abstract', 'keywords', 'categories', 'file', 'doi',
                  'journal_name', 'publication_year', 'pages', 'language']
        widgets = {
            'title':            forms.TextInput(attrs={'class': 'form-control'}),
            'abstract':         forms.Textarea(attrs={'class': 'form-control', 'rows': 5}),
            'keywords':         forms.TextInput(attrs={'class': 'form-control'}),
            'categories':       forms.CheckboxSelectMultiple(),
            'doi':              forms.TextInput(attrs={'class': 'form-control'}),
            'journal_name':     forms.TextInput(attrs={'class': 'form-control'}),
            'publication_year': forms.NumberInput(attrs={'class': 'form-control'}),
            'pages':            forms.TextInput(attrs={'class': 'form-control'}),
            'language':         forms.TextInput(attrs={'class': 'form-control'}),
        }


class ResearchProjectForm(forms.ModelForm):
    class Meta:
        model  = ResearchProject
        fields = ['title', 'description', 'objectives', 'methodology', 'categories',
                  'institution', 'start_date', 'end_date', 'is_public']
        widgets = {
            'title':       forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'objectives':  forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'methodology': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'categories':  forms.CheckboxSelectMultiple(),
            'institution': forms.TextInput(attrs={'class': 'form-control'}),
            'start_date':  forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'end_date':    forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }
