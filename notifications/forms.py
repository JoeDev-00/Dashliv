from django import forms
from .models import NotificationPreference

class NotificationPreferenceForm(forms.ModelForm):
    class Meta:
        model = NotificationPreference
        fields = [
            'email_enabled', 'sms_enabled', 'in_app_enabled',
            'order_status_update', 'delivery_reminder', 'rating_reminder', 'promotional_messages'
        ]
        widgets = {
            'email_enabled': forms.CheckboxInput(),
            'sms_enabled': forms.CheckboxInput(),
            'in_app_enabled': forms.CheckboxInput(),
            'order_status_update': forms.CheckboxInput(),
            'delivery_reminder': forms.CheckboxInput(),
            'rating_reminder': forms.CheckboxInput(),
            'promotional_messages': forms.CheckboxInput(),
        }
