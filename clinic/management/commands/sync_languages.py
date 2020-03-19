from clinic.models import Language
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from django.utils.translation import get_language_info

class Command(BaseCommand):
	def handle(self, *args, **kwargs):
		for tag, name in settings.LANGUAGES:
			info = get_language_info(tag)
			Language.objects.get_or_create(ietf_tag=tag, name=name)
