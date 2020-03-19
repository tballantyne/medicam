from django.db import models
import uuid

class Participant(models.Model):
	uuid = models.UUIDField(unique=True, default=uuid.uuid4, editable=False)
	created = models.DateTimeField(auto_now_add=True)
	last_updated = models.DateTimeField(auto_now=True)
	ip_address = models.GenericIPAddressField()
	twilio_jwt = models.TextField(blank=True, null=True, editable=False)

	class Meta:
 		abstract = True

class Language(models.Model):
	ietf_tag = models.CharField(max_length=5)
	name = models.CharField(max_length=30)

	class Meta:
		ordering = ['name']

	def __str__(self):
		return self.name

class SelfCertificationQuestion(models.Model):
	sort_order = models.PositiveIntegerField()
	text = models.TextField()

	class Meta:
		ordering = ('sort_order',)

	def __str__(self):
		return self.text

def upload_filename(instance, filename):
	ext = filename.split('.')[-1]
	return 'credentials/{}.{}'.format(instance.uuid, ext)

class Doctor(Participant):
	name = models.CharField(max_length=70)
	credentials = models.FileField(upload_to=upload_filename)
	verified = models.BooleanField(default=False)
	languages = models.ManyToManyField(Language)
	last_online = models.DateTimeField(blank=True, null=True)
	self_certification_questions = models.ManyToManyField(SelfCertificationQuestion)

	def __str__(self):
		return self.name

	@property
	def patient(self):
		try:
			return self.patient_set.get(session_started__isnull=False, session_ended__isnull=True)
		except Patient.DoesNotExist:
			return None

	@property
	def in_session(self):
		return self.patient_set.filter(session_started__isnull=True, session_ended__isnull=False).count() > 0

class Patient(Participant):
	language = models.ForeignKey(Language, models.PROTECT)
	doctor = models.ForeignKey(Doctor, models.PROTECT, blank=True, null=True)
	session_started = models.DateTimeField(blank=True, null=True)
	session_ended = models.DateTimeField(blank=True, null=True)
	notes = models.TextField(blank=True)

	@property
	def in_session(self):
		return hasattr(self, 'doctor') and self.session_started and not self.session_ended
