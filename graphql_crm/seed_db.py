# seed_db.py
import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "graphql_crm.settings")
django.setup()

from crm.models import Customer, Product

Customer.objects.all().delete()
Product.objects.all().delete()

Customer.objects.create(name="John", email="john@example.com", phone="+1234567890")
Customer.objects.create(name="Jane", email="jane@example.com")

Product.objects.create(name="Phone", price=199.99, stock=25)
Product.objects.create(name="Tablet", price=299.99, stock=15)

print("Database seeded!")
