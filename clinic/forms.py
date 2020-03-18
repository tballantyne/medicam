from django import forms
from django.core.exceptions import ValidationError
from django.forms import ModelForm
from django.forms.widgets import CheckboxSelectMultiple
from clinic.models import Doctor, SelfCertificationQuestion

class DoctorForm(ModelForm):
	class Meta:
		model = Doctor
		fields = ['name', 'credentials', 'languages', 'self_certification_questions']
		widgets = {
			'languages': CheckboxSelectMultiple(),
			'self_certification_questions': CheckboxSelectMultiple(),
		}

	def clean_credentials(self):
		f = self.cleaned_data.get('credentials')
		if f.size > 20 * 1024 * 1024:
			raise ValidationError("Proof of credentials must be less than 20MB.")
		return f

	def clean_self_certification_questions(self):
		answered = self.cleaned_data.get('self_certification_questions')
		unanswered_count = SelfCertificationQuestion.objects.exclude(id__in=answered.values_list('id', flat=True)).count()
		if unanswered_count > 0:
			raise ValidationError("You must confirm all items.")
		return answered
