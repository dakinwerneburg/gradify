from django import forms

from .models import CourseWork, Course, StudentSubmission


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
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control'}),
            'maxPoints': forms.NumberInput(attrs={'class': 'form-control', 'value': 0, 'min': 0}),
            'dueDate': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'date', 'required': True}),
            'workType': forms.Select(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        self.fields['course'] = forms.ModelChoiceField(queryset=Course.objects.filter(owner=user))
        self.fields['course'].widget.attrs = {'class': 'form-control'}


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
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'required': True}),
            'section': forms.TextInput(attrs={'class': 'form-control'}),
            'descriptionHeading': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control'}),
            'room': forms.TextInput(attrs={'class': 'form-control'}),
            'alternateLink': forms.TextInput(attrs={'class': 'form-control'}),
            'startDate': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'date'}),
            'endDate': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'date'}),
        }


class CourseWorkDeleteForm(forms.Form):
    assignments = forms.MultipleChoiceField(
        widget=forms.CheckboxSelectMultiple,
    )


class CourseWorkUpdateForm(forms.ModelForm):

    class Meta:
        model = CourseWork
        fields = [
            'title',
            'description',
            'maxPoints',
            'dueDate',
            'workType',
        ]
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control'}),
            'maxPoints': forms.NumberInput(attrs={'class': 'form-control'}),
            'dueDate': forms.DateInput(attrs={'class': 'form-control', 'type': 'date', 'required': True}),
            'workType': forms.Select(attrs={'class': 'form-control'}),
        }


class StudentSubmissionUpdateForm(forms.ModelForm):
    class Meta:
        model = StudentSubmission
        fields = [
            'assignedGrade'
        ]


class StudentSubmissionCreateForm(forms.ModelForm):
    class Meta:
        model = StudentSubmission
        fields = [
            'student',
            'coursework',
            'assignedGrade'
        ]
