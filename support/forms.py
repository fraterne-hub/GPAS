from django import forms
from .models import SupportTicket, TicketMessage


class SupportTicketForm(forms.ModelForm):
    class Meta:
        model  = SupportTicket
        fields = ['subject', 'category', 'priority', 'description', 'attachment']
        widgets = {
            'subject':     forms.TextInput(attrs={'class': 'form-control'}),
            'category':    forms.Select(attrs={'class': 'form-select'}),
            'priority':    forms.Select(attrs={'class': 'form-select'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 5}),
        }


class TicketReplyForm(forms.ModelForm):
    class Meta:
        model  = TicketMessage
        fields = ['message', 'attachment']
        widgets = {
            'message': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
        }
