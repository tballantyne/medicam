from clinic.forms import DoctorForm
from clinic.models import Doctor, Language, Patient
from datetime import datetime, timedelta
from django.conf import settings
from django.db import transaction
from django.shortcuts import redirect, render
from ipware import get_client_ip
from twilio.jwt.access_token import AccessToken
from twilio.jwt.access_token.grants import VideoGrant

SIX_MONTHS = 15552000
ONE_MONTH = 2629800

def index(request):
	doctor_id = request.COOKIES.get('doctor_id')
	if doctor_id:
		return redirect('consultation')
	else:
		return render(request, 'clinic/index.html')

def volunteer(request):
	if request.method == 'POST':
		form = DoctorForm(request.POST, request.FILES)
		if form.is_valid():
			doctor = form.save(commit=False)
			doctor.ip_address = get_client_ip(request)[0]
			doctor.save()
			form.save_m2m()
			response = redirect('consultation')
			response.set_cookie('doctor_id', doctor.uuid, max_age=SIX_MONTHS)
			return response
	else:
		form = DoctorForm()

	return render(request, 'clinic/volunteer.html', {'form': form})

def disclaimer(request):
	patient_id = request.COOKIES.get('patient_id')
	if patient_id:
		return redirect('consultation')

	if request.method == 'POST':
		lang = Language.objects.get(ietf_tag=request.LANGUAGE_CODE)
		patient = Patient(ip_address=get_client_ip(request)[0], language=lang)
		patient.save()
		response = redirect('consultation')
		response.set_cookie('patient_id', patient.uuid, max_age=ONE_MONTH)
		return response
	else:
		return render(request, 'clinic/disclaimer.html')

def consultation(request):
	doctor_id = request.COOKIES.get('doctor_id')
	if doctor_id:
		try:
			doctor = Doctor.objects.get(uuid=doctor_id)
		except Doctor.DoesNotExist:
			response = redirect('consultation')
			response.delete_cookie('doctor_id')
			return response
		return consultation_doctor(request, doctor)

	patient_id = request.COOKIES.get('patient_id')
	if patient_id:
		try:
			patient = Patient.objects.get(uuid=patient_id)
		except Patient.DoesNotExist:
			response = redirect('consultation')
			response.delete_cookie('patient_id')
			return response
		return consultation_patient(request, patient)

	return redirect('disclaimer')

def get_twilio_jwt(identity, room):
	token = AccessToken(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_API_KEY, settings.TWILIO_API_SECRET, identity=identity)
	token.add_grant(VideoGrant(room=room))
	return token.to_jwt().decode('utf-8')

@transaction.atomic
def consultation_doctor(request, doctor):
	if not doctor.verified:
		return render(request, 'clinic/unverified.html')

	doctor.last_online = datetime.now()
	doctor.save()

	if not doctor.patient:
		try:
			patient = Patient.objects.order_by('id').get(language__in=doctor.languages.all(), session_started__isnull=True)
			patient.doctor = doctor
			patient.session_started = datetime.now()
			patient.twilio_jwt = get_twilio_jwt(identity=str(patient.uuid), room=str(doctor.uuid))
			patient.save()
			doctor.twilio_jwt = get_twilio_jwt(identity=str(doctor.uuid), room=str(doctor.uuid))
			doctor.save()
			return redirect('consultation')
		except Patient.DoesNotExist:
			return render(request, 'clinic/waiting_doctor.html')

	return render(request, 'clinic/session_doctor.html', context={
		'video_data': {
			'token': doctor.twilio_jwt,
			'room': str(doctor.uuid),
		},
	})

def consultation_patient(request, patient):
	if not patient.in_session:
		return render(request, 'clinic/waiting_patient.html')
	else:
		return render(request, 'clinic/session_patient.html', context={
			'doctor': patient.doctor,
			'video_data': {
				'token': patient.twilio_jwt,
				'room': str(patient.doctor.uuid),
			},
		})

@transaction.atomic
def finish(request):
	response = redirect('index')
	if request.method != 'POST':
		return response

	doctor_id = request.COOKIES.get('doctor_id')
	if doctor_id:
		try:
			doctor = Doctor.objects.get(uuid=doctor_id)
			patient = doctor.patient
			if patient:
				patient.session_ended = datetime.now()
				patient.save()
		except Doctor.DoesNotExist:	
			pass

	patient_id = request.COOKIES.get('patient_id')
	if patient_id:
		try:
			patient = Patient.objects.get(uuid=patient_id)
			patient.session_ended = datetime.now()
			patient.save()
		except Patient.DoesNotExist:
			pass

	return response
