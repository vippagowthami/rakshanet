"""
Management command to populate initial disaster types and resource types
"""
from django.core.management.base import BaseCommand
from raksha.models import DisasterType, ResourceType, EmergencyContact


class Command(BaseCommand):
    help = 'Populates initial disaster types, resource types, and emergency contacts'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Populating initial data...'))

        # Disaster Types
        disaster_types = [
            ('Flood', 'natural', 'Major flooding, water logging', 1.5),
            ('Earthquake', 'natural', 'Seismic activity, building collapse', 2.0),
            ('Cyclone', 'natural', 'Strong winds, heavy rainfall', 1.8),
            ('Drought', 'natural', 'Water scarcity, crop failure', 1.2),
            ('Landslide', 'natural', 'Soil erosion, mudslide', 1.5),
            ('Fire', 'man_made', 'Building fire, forest fire', 1.6),
            ('Industrial Accident', 'man_made', 'Chemical spill, explosion', 1.7),
            ('Road Accident', 'man_made', 'Vehicle collision, casualties', 1.3),
            ('Pandemic', 'health', 'Disease outbreak, epidemic', 1.9),
            ('Medical Emergency', 'health', 'Mass casualty, health crisis', 1.5),
            ('Conflict', 'conflict', 'Violence, civil unrest', 1.8),
            ('Building Collapse', 'man_made', 'Structural failure', 1.7),
            ('Gas Leak', 'man_made', 'Toxic gas exposure', 1.6),
            ('Tsunami', 'natural', 'Tidal wave, coastal flooding', 2.0),
            ('Heat Wave', 'natural', 'Extreme temperature', 1.2),
        ]

        for name, category, description, severity in disaster_types:
            disaster, created = DisasterType.objects.get_or_create(
                name=name,
                defaults={
                    'category': category,
                    'description': description,
                    'severity_multiplier': severity
                }
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f'Created disaster type: {name}'))

        # Resource Types
        resource_types = [
            ('Drinking Water', 'food', 'liters', 'Potable water for consumption'),
            ('Food Packets', 'food', 'packets', 'Ready-to-eat meals'),
            ('Rice', 'food', 'kg', 'Raw rice'),
            ('Wheat', 'food', 'kg', 'Wheat flour'),
            ('First Aid Kit', 'medical', 'units', 'Basic medical supplies'),
            ('Medicines', 'medical', 'units', 'Essential medicines'),
            ('Blankets', 'shelter', 'units', 'Warm blankets'),
            ('Tents', 'shelter', 'units', 'Emergency shelter tents'),
            ('Clothing', 'shelter', 'units', 'Basic clothing'),
            ('Tarpaulin Sheets', 'shelter', 'units', 'Waterproof sheets'),
            ('Rescue Equipment', 'rescue', 'units', 'Search and rescue tools'),
            ('Life Jackets', 'rescue', 'units', 'Flotation devices'),
            ('Boats', 'rescue', 'units', 'Rescue boats'),
            ('Mobile Phones', 'communication', 'units', 'Communication devices'),
            ('Radios', 'communication', 'units', 'Emergency radios'),
            ('Vehicles', 'transport', 'units', 'Transportation vehicles'),
            ('Fuel', 'transport', 'liters', 'Diesel/Petrol'),
            ('Cash', 'financial', 'INR', 'Financial aid'),
            ('Flashlights', 'other', 'units', 'Emergency lighting'),
            ('Batteries', 'other', 'units', 'Power source'),
            ('Water Purification Tablets', 'food', 'packets', 'Water treatment'),
            ('Hygiene Kits', 'other', 'units', 'Sanitation supplies'),
            ('Baby Food', 'food', 'packets', 'Infant nutrition'),
            ('Glucose', 'medical', 'packets', 'Energy supplement'),
            ('Stretchers', 'medical', 'units', 'Patient transport'),
        ]

        for name, category, unit, description in resource_types:
            resource, created = ResourceType.objects.get_or_create(
                name=name,
                defaults={
                    'category': category,
                    'unit_of_measurement': unit,
                    'description': description
                }
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f'Created resource type: {name}'))

        # Emergency Contacts
        emergency_contacts = [
            ('National Emergency Number', 'emergency', '112', '', True),
            ('Police', 'police', '100', '', True),
            ('Fire', 'fire', '101', '', True),
            ('Ambulance', 'medical', '102', '', True),
            ('Disaster Management', 'disaster', '108', '', True),
            ('Women Helpline', 'emergency', '1091', '', True),
            ('Child Helpline', 'emergency', '1098', '', True),
            ('Senior Citizen Helpline', 'emergency', '14567', '', True),
            ('Road Accident Emergency Service', 'emergency', '1073', '', True),
            ('Railway Accident Emergency Service', 'emergency', '1072', '', True),
        ]

        for name, category, number, alt_number, available_247 in emergency_contacts:
            contact, created = EmergencyContact.objects.get_or_create(
                name=name,
                phone_number=number,
                defaults={
                    'category': category,
                    'alternate_number': alt_number,
                    'available_247': available_247,
                    'languages_supported': 'English, Hindi'
                }
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f'Created emergency contact: {name} - {number}'))

        self.stdout.write(self.style.SUCCESS('\n✅ Initial data population completed!'))
        self.stdout.write(self.style.WARNING('\nNext steps:'))
        self.stdout.write('1. Create NGO profiles in admin panel')
        self.stdout.write('2. Add shelters for different areas')
        self.stdout.write('3. Configure safety tips for each disaster type')
        self.stdout.write('4. Set up user accounts with appropriate roles')
