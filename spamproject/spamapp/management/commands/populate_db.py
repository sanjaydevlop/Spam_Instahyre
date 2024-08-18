from django.core.management.base import BaseCommand
from faker import Faker
from spamapp.models import User, Contact, SpamReport  # Adjust according to your app name
from django.contrib.auth.hashers import make_password


class Command(BaseCommand):
    help = 'Populate the database with random sample data'

    def handle(self, *args, **kwargs):
        fake = Faker()

        # Create sample users
        for _ in range(50):  # Adjust the number of users as needed
            User.objects.create(
                name=fake.name(),
                phone_number=fake.phone_number(),
                email=fake.email(),
                password=make_password(fake.password())
            )

        # Create sample contacts
        users = User.objects.all()
        for _ in range(100):  # Adjust the number of contacts as needed
            user = fake.random.choice(users)
            Contact.objects.create(
                created_by=user,
                contact_name=fake.name(),
                contact_phone_number=fake.phone_number()
            )

        user_phone_numbers = User.objects.values_list('phone_number', flat=True)
        contact_phone_numbers = Contact.objects.values_list('contact_phone_number', flat=True)

        # Combine and deduplicate phone numbers
        all_phone_numbers = set(user_phone_numbers) | set(contact_phone_numbers)

        for _ in range(30):  # Adjust the number of spam reports as needed
            phone_number = fake.random.choice(list(all_phone_numbers))
            SpamReport.objects.create(
                phone_number=phone_number,
                is_spam=True
            )

        self.stdout.write(self.style.SUCCESS('Successfully populated the database with sample data'))
