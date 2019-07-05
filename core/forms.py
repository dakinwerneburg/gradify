from django import forms

from .models import CourseWork, Course


class CourseWorkCreateForm(forms.ModelForm):

    class Meta:
        model = CourseWork
        fields = [
            'course',
            'title',
            'description',
            'max_points',
            'dueDate',
            'type',
        ]
        widgets = {
            'course': forms.Select(attrs={'class': 'form-control'}),
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control'}),
            'max_points': forms.NumberInput(attrs={'class': 'form-control', 'value': 0}),
            'dueDate': forms.DateTimeInput(attrs={'class': 'form-control', 'required': True}),
            'type': forms.Select(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        self.fields['course'] = forms.ModelChoiceField(queryset=Course.objects.filter(ownerId=user.email))


class CourseCreateForm(forms.ModelForm):

    class Meta:
        model = Course
        fields = [
            'name',
            'section',
            'descriptionHeading',
            'description',
            'room',
            'alternateLink',
            'startDate',
            'endDate',
        ]


class CourseWorkListForm(forms.Form):
    assignments = forms.MultipleChoiceField(
        widget=forms.CheckboxSelectMultiple,
    )