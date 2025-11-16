from django import forms
from .models import NKO, NKOMembership


class NKOForm(forms.ModelForm):
    class Meta:
        model = NKO
        fields = [
            'name', 'description', 'mission', 'category',
            'email', 'phone', 'website', 'city', 'address',
            'logo', 'cover_image'
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
            'mission': forms.Textarea(attrs={'rows': 3}),
            'address': forms.Textarea(attrs={'rows': 2}),
        }

    def clean_website(self):
        website = self.cleaned_data.get('website')
        if website and not website.startswith(('http://', 'https://')):
            website = 'https://' + website
        return website


class NKOMembershipForm(forms.ModelForm):
    class Meta:
        model = NKOMembership
        fields = ['responsibilities', 'skills']
        widgets = {
            'responsibilities': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Чем готовы помочь?'}),
            'skills': forms.TextInput(attrs={'placeholder': 'Навыки, опыт, образование...'}),
        }