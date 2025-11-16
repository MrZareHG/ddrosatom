from django import forms
from .models import News, Event, KnowledgeBase, Comment, EventParticipation


class NewsForm(forms.ModelForm):
    class Meta:
        model = News
        fields = ['title', 'content', 'excerpt', 'cover_image', 'nko', 'city', 'is_featured', 'allow_comments']
        widgets = {
            'content': forms.Textarea(attrs={'rows': 6}),
            'excerpt': forms.Textarea(attrs={'rows': 3}),
            'title': forms.TextInput(attrs={'placeholder': 'Заголовок новости'}),
        }

    def clean_title(self):
        title = self.cleaned_data.get('title')
        if len(title) < 10:
            raise forms.ValidationError("Заголовок должен содержать минимум 10 символов")
        return title


class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = [
            'title', 'description', 'event_type', 'start_date', 'end_date',
            'registration_deadline', 'city', 'address', 'online', 'online_link',
            'nko', 'max_participants', 'requirements', 'what_to_bring', 'contact_info'
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 5}),
            'start_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'end_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'registration_deadline': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'requirements': forms.Textarea(attrs={'rows': 3}),
            'what_to_bring': forms.Textarea(attrs={'rows': 3}),
        }

    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')
        registration_deadline = cleaned_data.get('registration_deadline')

        if start_date and end_date and start_date >= end_date:
            raise forms.ValidationError("Дата окончания должна быть позже даты начала")

        if registration_deadline and start_date and registration_deadline > start_date:
            raise forms.ValidationError("Дедлайн регистрации не может быть позже начала мероприятия")

        return cleaned_data


class KnowledgeBaseForm(forms.ModelForm):
    class Meta:
        model = KnowledgeBase
        fields = ['title', 'content', 'excerpt', 'category', 'difficulty_level', 'attached_file', 'is_public']
        widgets = {
            'content': forms.Textarea(attrs={'rows': 8}),
            'excerpt': forms.Textarea(attrs={'rows': 3}),
        }


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['text']
        widgets = {
            'text': forms.Textarea(attrs={
                'rows': 3,
                'placeholder': 'Оставьте ваш комментарий...',
                'style': 'resize: vertical;'
            })
        }


class EventParticipationForm(forms.ModelForm):
    class Meta:
        model = EventParticipation
        fields = ['notes']
        widgets = {
            'notes': forms.Textarea(attrs={
                'rows': 3,
                'placeholder': 'Дополнительная информация (необязательно)...'
            })
        }