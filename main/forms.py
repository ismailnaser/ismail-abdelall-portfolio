from django import forms


class ContactForm(forms.Form):
    name = forms.CharField(
        max_length=120,
        widget=forms.TextInput(
            attrs={
                "class": "form-input",
                "placeholder": "Name",
                "data-placeholder-ar": "الاسم",
            }
        ),
    )
    email = forms.EmailField(
        widget=forms.EmailInput(
            attrs={"class": "form-input", "placeholder": "Email", "data-placeholder-ar": "البريد"}
        ),
    )
    message = forms.CharField(
        widget=forms.Textarea(
            attrs={
                "class": "form-input form-textarea",
                "rows": 5,
                "placeholder": "Message",
                "data-placeholder-ar": "الرسالة",
            }
        ),
    )
