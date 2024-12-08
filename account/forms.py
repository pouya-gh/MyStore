from django import forms
from .models import CustomerProfile


class CustomerProfileForm(forms.ModelForm):
    class Meta:
        model = CustomerProfile
        fields = ["social_code", 
                 "birth_date",
                 "country",
                 "province",
                 "city",
                 "address",
                 "phone_number",
                 "phone_number2",]