from django import forms

class AddTorrentForm(forms.Form):
    #title = forms.CharField(max_length=200)
    file = forms.FileField()
