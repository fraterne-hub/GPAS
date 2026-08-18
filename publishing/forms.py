from django import forms
from .models import Publication, Review


class PublicationSubmitForm(forms.ModelForm):
    class Meta:
        model  = Publication
        fields = ['title', 'abstract', 'keywords', 'pub_type', 'journal',
                  'subjects', 'manuscript', 'language', 'pages', 'isbn', 'doi']
        widgets = {
            'title':      forms.TextInput(attrs={'class': 'form-control'}),
            'abstract':   forms.Textarea(attrs={'class': 'form-control', 'rows': 5}),
            'keywords':   forms.TextInput(attrs={'class': 'form-control'}),
            'pub_type':   forms.Select(attrs={'class': 'form-select'}),
            'journal':    forms.Select(attrs={'class': 'form-select'}),
            'subjects':   forms.CheckboxSelectMultiple(),
            'language':   forms.TextInput(attrs={'class': 'form-control'}),
            'pages':      forms.TextInput(attrs={'class': 'form-control'}),
            'isbn':       forms.TextInput(attrs={'class': 'form-control'}),
            'doi':        forms.TextInput(attrs={'class': 'form-control'}),
        }


class ReviewForm(forms.ModelForm):
    class Meta:
        model  = Review
        fields = ['recommendation', 'comments_to_author', 'comments_to_editor']
        widgets = {
            'recommendation':      forms.Select(attrs={'class': 'form-select'}),
            'comments_to_author':  forms.Textarea(attrs={'class': 'form-control', 'rows': 5}),
            'comments_to_editor':  forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
        }
