from django import forms
# from django.forms import ClearableFileInput
from .models import UploadPdf

class FileUpload(forms.ModelForm):
    class Meta:
        model = UploadPdf
        fields = ['imageupload']
        # widgets = {
        #     'fileupload': ClearableFileInput(attrs={'multiple': True}),
        # }