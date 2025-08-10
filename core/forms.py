from django import forms
from .models import Milestone, Document, ProjectMembership, Project, ROLE_CHOICES
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm

class RegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].help_text = None
        self.fields['password1'].help_text = None
        self.fields['password2'].help_text = None

class LoginForm(forms.Form):
    username = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={
            'placeholder': 'Nazwa użytkownika',
            'class': 'form-control'
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Hasło',
            'class': 'form-control'
        })
    )

class JoinProjectForm(forms.Form):
    project = forms.ModelChoiceField(
        queryset=Project.objects.none(),
        label="Wybierz projekt"
    )
    role = forms.ChoiceField(
        choices=ROLE_CHOICES,
        label="Rola w projekcie"
    )
    note = forms.CharField(
        label="Notatka np. zakres obowiązków",
        required=False,
        widget=forms.Textarea(attrs={'rows': 3})
    )

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        self.fields['note'].widget.attrs.update({'rows': 3})
        self.fields['project'].queryset = Project.objects.filter(is_active=True)

class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = '__all__'
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'end_date': forms.DateInput(attrs={'type': 'date'}),
        }


class MilestoneForm(forms.ModelForm):
    class Meta:
        model = Milestone
        fields = ['title', 'description', 'start_date', 'due_date', 'status', 'responsible']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'due_date': forms.DateInput(attrs={'type': 'date'}),
            'status': forms.Select(),
            'responsible': forms.SelectMultiple(),
        }
        labels = {
            'responsible': 'Osoby odpowiedzialne',
        }

class DocumentForm(forms.ModelForm):
    class Meta:
        model = Document
        fields = ['name', 'file']