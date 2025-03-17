from django import forms
from datetime import datetime

class BaptismRecordForm(forms.Form):
    # Basic Information
    record_number = forms.CharField(
        max_length=10, 
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter record number'})
    )
    baptism_date = forms.DateField(
        required=True,
        input_formats=['%d-%m-%Y', '%d/%m/%Y', '%Y-%m-%d'],
        widget=forms.TextInput(attrs={
            'class': 'form-control datepicker', 
            'placeholder': 'DD-MM-YYYY',
            'autocomplete': 'off'
        })
    )
    birth_date = forms.DateField(
        required=True,
        input_formats=['%d-%m-%Y', '%d/%m/%Y', '%Y-%m-%d'],
        widget=forms.TextInput(attrs={
            'class': 'form-control datepicker', 
            'placeholder': 'DD-MM-YYYY',
            'autocomplete': 'off'
        })
    )
    name = forms.CharField(
        max_length=100, 
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter full name'})
    )
    name_is_tamil = forms.BooleanField(
        required=False,
        initial=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    gender = forms.CharField(
        max_length=100, 
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter gender'})
    )
    gender_is_tamil = forms.BooleanField(
        required=False,
        initial=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    occupation = forms.CharField(
        max_length=100, 
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter occupation'})
    )
    occupation_is_tamil = forms.BooleanField(
        required=False,
        initial=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    
    # Parent Information
    father_name = forms.CharField(
        max_length=100, 
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter father\'s name'})
    )
    mother_name = forms.CharField(
        max_length=100, 
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter mother\'s name'})
    )
    parents_is_tamil = forms.BooleanField(
        required=False,
        initial=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    
    # Godparent Information
    godparent1_name = forms.CharField(
        max_length=100, 
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter godparent\'s name'})
    )
    godparent2_name = forms.CharField(
        max_length=100, 
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter godparent\'s name'})
    )
    godparent3_name = forms.CharField(
        max_length=100, 
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter godparent\'s name'})
    )
    godparents_is_tamil = forms.BooleanField(
        required=False,
        initial=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    
    # Church Information
    church_name = forms.CharField(
        max_length=100, 
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter church name'})
    )
    church_location = forms.CharField(
        max_length=100, 
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter church location'})
    )
    church_is_tamil = forms.BooleanField(
        required=False,
        initial=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    
    # Minister Information
    minister_name = forms.CharField(
        max_length=100, 
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter minister name'})
    )
    minister_title = forms.CharField(
        max_length=100, 
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter title (e.g. Rev.)'})
    )
    minister_is_tamil = forms.BooleanField(
        required=False,
        initial=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    
    # Certification
    certifying_minister = forms.CharField(
        max_length=100, 
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter certifying minister name'})
    )
    church_location_cert = forms.CharField(
        max_length=100, 
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter church location'})
    )
    certification_date = forms.DateField(
        required=True,
        input_formats=['%d-%m-%Y', '%d/%m/%Y', '%Y-%m-%d'],
        widget=forms.TextInput(attrs={
            'class': 'form-control datepicker', 
            'placeholder': 'DD-MM-YYYY',
            'autocomplete': 'off'
        })
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Set initial values for date fields
        today = datetime.today().strftime('%d-%m-%Y')
        if not self.initial.get('certification_date'):
            self.initial['certification_date'] = today 