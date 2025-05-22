from django import forms
from .models import Order, Package
from django.utils import timezone

class PackageForm(forms.ModelForm):
    class Meta:
        model = Package
        fields = ['name', 'description', 'weight', 'size', 'is_fragile', 'requires_signature']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }

class OrderForm(forms.ModelForm):
    scheduled_pickup_time = forms.DateTimeField(
        widget=forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        initial=timezone.now
    )
    
    class Meta:
        model = Order
        fields = [
            'pickup_address', 'delivery_address', 
            'scheduled_pickup_time', 'service_type',
            'has_insurance', 'notes'
        ]
        widgets = {
            'notes': forms.Textarea(attrs={'rows': 3}),
        }
        
    def clean_scheduled_pickup_time(self):
        scheduled_pickup_time = self.cleaned_data.get('scheduled_pickup_time')
        now = timezone.now()
        
        # Vérifier que la date est dans le futur
        if scheduled_pickup_time < now:
            raise forms.ValidationError("La date de prise en charge doit être dans le futur.")
        
        return scheduled_pickup_time
