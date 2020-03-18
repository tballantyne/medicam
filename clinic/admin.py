from django.contrib import admin
from clinic.models import Doctor, Language, SelfCertificationQuestion

class DoctorAdmin(admin.ModelAdmin):
	list_display=('name', 'verified', 'get_languages', 'in_session')
	list_filter=('verified', 'languages')
	readonly_fields=('ip_address', 'last_online', 'self_certification_questions', 'in_session')

	def get_languages(self, obj):
		return ", ".join([l.name for l in obj.languages.all()])
	get_languages.short_description = "Languages"

admin.site.register(Doctor, DoctorAdmin)
admin.site.register(Language)
admin.site.register(SelfCertificationQuestion)
