from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

User = get_user_model()

class Command(BaseCommand):
    help = "Set all user passwords to 'password'"

    def handle(self, *args, **kwargs):
        for user in User.objects.all():
            user.set_password("password")
            user.save()

        self.stdout.write(self.style.SUCCESS("All passwords set to 'password'"))