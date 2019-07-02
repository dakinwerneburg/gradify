from django import forms

from .models import Course


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
        # widgets = {
        #     'name': forms.Select(attrs={'class': 'form-control'}),
        #     'section': forms.TextInput(attrs={'class': 'form-control'}),
        #     'descriptionHeading': forms.Textarea(attrs={'class': 'form-control'}),
        #     'descriptionHeading': forms.Textarea(attrs={'class': 'form-control'}),
        #     'max_points': forms.NumberInput(attrs={'class': 'form-control', 'value': 0}),
        #     'dueDate': forms.DateTimeInput(attrs={'class': 'form-control', 'required': True}),
        #     'type': forms.Select(attrs={'class': 'form-control'}),
        # }


        
