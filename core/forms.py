from django import forms

from .models import CourseWork, Course


class CourseWorkCreateForm(forms.ModelForm):

    class Meta:
        model = CourseWork
        fields = [
            'course',
            'title',
            'description',
            'maxPoints',
            'dueDate',
            'workType',
        ]
        widgets = {
            'course': forms.Select(attrs={'class': 'form-control'}),
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control'}),
            'maxPoints': forms.NumberInput(attrs={'class': 'form-control', 'value': 0}),
            'dueDate': forms.DateTimeInput(attrs={'class': 'form-control', 'required': True}),
            'workType': forms.Select(attrs={'class': 'form-control'}),
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
