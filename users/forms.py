from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User, ClientProfile, DeliveryPersonProfile

class UserRegisterForm(UserCreationForm):
    email = forms.EmailField()
    phone_number = forms.CharField(max_length=15, required=False)
    user_type = forms.ChoiceField(choices=User.USER_TYPE_CHOICES)
    
    class Meta:
        model = User
        fields = ['username', 'email', 'phone_number', 'user_type', 'password1', 'password2']

class UserUpdateForm(forms.ModelForm):
    email = forms.EmailField()
    phone_number = forms.CharField(max_length=15, required=False)
    
    class Meta:
        model = User
        fields = ['username', 'email', 'phone_number', 'first_name', 'last_name']

class ClientProfileForm(forms.ModelForm):
    class Meta:
        model = ClientProfile
        fields = ['company_name']

class DeliveryProfileForm(forms.ModelForm):
    class Meta:
        model = DeliveryPersonProfile
        fields = ['vehicle_type', 'license_number']

class ProfileUpdateForm(forms.ModelForm):
    """
    Formulaire dynamique qui s'adapte au type d'utilisateur
    """
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super(ProfileUpdateForm, self).__init__(*args, **kwargs)
        
        if self.user and self.user.user_type == 'client':
            self.fields['company_name'] = forms.CharField(max_length=100, required=False)
        elif self.user and self.user.user_type == 'delivery':
            self.fields['vehicle_type'] = forms.CharField(max_length=50)
            self.fields['license_number'] = forms.CharField(max_length=50)
    
    class Meta:
        model = User
        fields = ['profile_image', 'address']
