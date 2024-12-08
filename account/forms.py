from django import forms
from .models import CustomerProfile, ProviderProfile


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
        
class ProviderProfileForm(forms.ModelForm):
    class Meta:
        model = ProviderProfile
        fields = ["official_name", 
                 "name",
                 "social_code",
                 "country",
                 "province",
                 "city",
                 "address",
                 "phone_number",
                 "phone_number2",]