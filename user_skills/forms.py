from django import forms
from .models import SkillRating, UserReport


class Add_New_Data(forms.Form):
    category = forms.CharField(
        max_length=100,
        required=True,
        widget=forms.TextInput(
            attrs={
                'class': 'form-control-sm',
                'placeholder': 'Enter category'}),
        label='Category')

    subcategory = forms.CharField(
        max_length=100,
        required=True,
        widget=forms.TextInput(
            attrs={
                'class': 'form-control-sm',
                'placeholder': 'Enter subcategory'}),
        label='Subcategory')

    skill_name = forms.CharField(
        max_length=100,
        required=True,
        widget=forms.TextInput(
            attrs={
                'class': 'form-control-sm',
                'placeholder': 'Enter skill name'}),
        label='Skill Name')


class SkillRatingForm(forms.ModelForm):
    class Meta:
        model = SkillRating
        fields = ['rating']  # You can add other fields as needed

    # You can also customize the widget if you need to
    rating = forms.ChoiceField(
        choices=[(i, str(i)) for i in range(1, 6)],  # Choices for 1 to 5 stars
        widget=forms.RadioSelect,
    )


class ReportIssueForm(forms.ModelForm):
    class Meta:
        model = UserReport  # Define the model here
        # Only the 'report' field needs to be filled by the user
        fields = ['report']
        widgets = {
            'report': forms.Textarea(
                attrs={
                    'placeholder': 'Describe the issue...',
                    'rows': 5,
                    'cols': 40}),
        }
        labels = {
            'report': 'Your Report',
        }
