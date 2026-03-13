from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from decimal import Decimal
from .models import (
    CrisisRequest, VolunteerProfile, Assignment, CommunityChannel,
    AIChatMessage, UserLocationPing, NGOProfile, ResourceType, ResourceInventory,
    Shelter, EmergencyBeacon, Donation, DisasterType
)
from .utils import compute_priority_score
from django.core.management import call_command
from users.models import Profile


User = get_user_model()


class PriorityAndAssignmentTests(TestCase):
    def test_compute_priority_score_basic(self):
        req = CrisisRequest(urgency='critical', is_verified=True, resources_required='water food medical')
        score = compute_priority_score(req)
        self.assertIsInstance(score, float)
        self.assertGreaterEqual(score, 0.0)
        self.assertLessEqual(score, 100.0)

    def test_assignment_command_assigns(self):
        # create a volunteer user and profile
        u = User.objects.create_user('vol1', 'vol1@example.com', 'pass')
        # Profile may be auto-created by signals, so update/create safely.
        vp, _ = VolunteerProfile.objects.get_or_create(user=u)
        vp.latitude = 12.9716
        vp.longitude = 77.5946
        vp.available = True
        vp.save(update_fields=['latitude', 'longitude', 'available'])

        # create a crisis request near the volunteer
        cr = CrisisRequest.objects.create(urgency='critical', is_verified=True, latitude=12.9718, longitude=77.5949, resources_required='oxygen')
        # compute score and save to ensure priority >= threshold
        cr.priority_score = 95.0
        cr.save()

        # run management command
        call_command('assign_pending')

        cr.refresh_from_db()
        self.assertTrue(cr.assignments.exists())
        ass = cr.assignments.first()
        self.assertIsInstance(ass, Assignment)
        vp.refresh_from_db()
        self.assertFalse(vp.available)


class NGOReportLifecycleTests(TestCase):
    def setUp(self):
        self.ngo_user = User.objects.create_user('ngo_reports', 'ngo_reports@example.com', 'pass123')
        Profile.objects.update_or_create(user=self.ngo_user, defaults={'role': 1})
        self.ngo_profile = NGOProfile.objects.create(
            user=self.ngo_user,
            organization_name='Report Relief',
            contact_person='Lead',
            phone='9999999999',
            email='reports@example.com',
            address='Relief Base',
            service_areas='City',
            active=True,
        )

        self.volunteer_user = User.objects.create_user('vol_reports', 'vol_reports@example.com', 'pass123')
        Profile.objects.update_or_create(user=self.volunteer_user, defaults={'role': 2})
        self.volunteer_profile = VolunteerProfile.objects.create(
            user=self.volunteer_user,
            affiliated_ngo=self.ngo_profile,
            available=True,
            primary_skill='general',
        )

        self.disaster_type = DisasterType.objects.create(name='Flood', category='natural')
        self.crisis_request = CrisisRequest.objects.create(
            assigned_ngo=self.ngo_profile,
            disaster_type=self.disaster_type,
            status='verified',
            people_affected=25,
            urgency='high',
            name='Family Support',
            address='River Road',
        )

    def test_assignment_creation_moves_request_to_allocated_and_reports_it_active(self):
        self.client.login(username='ngo_reports', password='pass123')

        response = self.client.post(reverse('ngo-create-assignment'), {
            'request': self.crisis_request.id,
            'volunteer': self.volunteer_profile.id,
            'notes': 'Dispatch for rescue',
        })

        self.assertEqual(response.status_code, 302)
        self.crisis_request.refresh_from_db()
        self.assertEqual(self.crisis_request.status, 'allocated')

        report_response = self.client.get(reverse('ngo-reports'))
        self.assertEqual(report_response.status_code, 200)
        self.assertEqual(report_response.context['stats']['in_progress'], 1)
        self.assertEqual(report_response.context['stats']['pending'], 0)

    def test_completed_assignment_updates_request_and_report_totals(self):
        assignment = Assignment.objects.create(
            request=self.crisis_request,
            volunteer=self.volunteer_profile,
            status='accepted',
        )
        Donation.objects.create(
            donor=self.ngo_user,
            request=self.crisis_request,
            donation_type='money',
            amount=Decimal('500.00'),
        )

        self.client.login(username='vol_reports', password='pass123')
        response = self.client.post(reverse('volunteer-update-assignment', kwargs={'assignment_id': assignment.id}), {
            'status': 'completed',
            'notes': 'Support completed',
            'hours_spent': '4',
        })

        self.assertEqual(response.status_code, 302)
        assignment.refresh_from_db()
        self.crisis_request.refresh_from_db()
        self.volunteer_profile.refresh_from_db()

        self.assertEqual(self.crisis_request.status, 'completed')
        self.assertEqual(self.volunteer_profile.tasks_completed, 1)
        self.assertEqual(self.volunteer_profile.total_hours_volunteered, 4)

        self.client.login(username='ngo_reports', password='pass123')
        report_response = self.client.get(reverse('ngo-reports'))
        self.assertEqual(report_response.status_code, 200)
        self.assertEqual(report_response.context['stats']['completed'], 1)
        self.assertEqual(report_response.context['stats']['success_rate'], 100.0)
        self.assertEqual(report_response.context['stats']['total_donations'], Decimal('500.00'))

    def test_reports_resync_stale_completed_request_status(self):
        Assignment.objects.create(
            request=self.crisis_request,
            volunteer=self.volunteer_profile,
            status='completed',
            completed=True,
        )

        self.client.login(username='ngo_reports', password='pass123')
        report_response = self.client.get(reverse('ngo-reports'))

        self.assertEqual(report_response.status_code, 200)
        self.crisis_request.refresh_from_db()
        self.assertEqual(self.crisis_request.status, 'completed')
        self.assertEqual(report_response.context['stats']['completed'], 1)
        self.assertEqual(report_response.context['stats']['pending'], 0)


class CommunityAndAITests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user('user1', 'user1@example.com', 'pass123')
        Profile.objects.update_or_create(user=self.user, defaults={'role': 3})
        self.client.login(username='user1', password='pass123')

        self.ngo_channel = CommunityChannel.objects.create(
            name='NGO Ops',
            slug='ngo-ops-test',
            role_scope='ngo',
            is_active=True,
        )
        self.user_channel = CommunityChannel.objects.create(
            name='User Support',
            slug='user-support-test',
            role_scope='user',
            is_active=True,
        )

    def test_user_cannot_post_to_ngo_channel(self):
        response = self.client.post(reverse('post-community-message'), {
            'channel_slug': self.ngo_channel.slug,
            'message': 'Need to post in NGO room',
        })
        self.assertEqual(response.status_code, 302)
        self.assertFalse(self.ngo_channel.messages.exists())

    def test_user_can_post_to_user_channel(self):
        response = self.client.post(reverse('post-community-message'), {
            'channel_slug': self.user_channel.slug,
            'message': 'Family needs water support',
        })
        self.assertEqual(response.status_code, 302)
        self.assertEqual(self.user_channel.messages.count(), 1)

    def test_ai_chat_creates_response_record(self):
        response = self.client.post(reverse('ai-chat-assistant'), {
            'prompt': 'Flood in my area, what should I do first?',
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(AIChatMessage.objects.filter(user=self.user).exists())


class GeoServicesTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user('geo_user', 'geo@example.com', 'pass123')
        Profile.objects.update_or_create(user=self.user, defaults={'role': 3})
        self.client.login(username='geo_user', password='pass123')

        ngo_user = User.objects.create_user('ngo1', 'ngo1@example.com', 'pass123')
        Profile.objects.update_or_create(user=ngo_user, defaults={'role': 1})
        ngo, _ = NGOProfile.objects.update_or_create(
            user=ngo_user,
            defaults={
                'organization_name': 'Rapid Relief',
                'contact_person': 'Lead',
                'phone': '9999999999',
                'email': 'ngo1@example.com',
                'address': 'Central Zone',
                'latitude': 12.9716,
                'longitude': 77.5946,
                'service_areas': 'City',
                'active': True,
            }
        )

        resource_type = ResourceType.objects.create(name='Water Pack', category='food')
        ResourceInventory.objects.create(
            ngo=ngo,
            resource_type=resource_type,
            quantity=120,
            unit='packs',
            location='Warehouse A',
            updated_by=ngo_user,
        )

        Shelter.objects.create(
            name='City Shelter',
            address='Main Road',
            latitude=12.9720,
            longitude=77.5950,
            capacity=100,
            current_occupancy=40,
            contact_number='8888888888',
            facilities='Water,Food',
            status='active',
        )

    def test_geolocation_update_creates_ping(self):
        response = self.client.post(reverse('geo-update'), {
            'latitude': 12.9719,
            'longitude': 77.5949,
            'accuracy': 15,
        })
        self.assertEqual(response.status_code, 200)
        self.assertTrue(UserLocationPing.objects.filter(user=self.user).exists())

    def test_geo_services_returns_prioritized_data(self):
        UserLocationPing.objects.create(user=self.user, latitude=12.9719, longitude=77.5949)
        response = self.client.get(reverse('geo-services'))
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertFalse(data.get('needs_location'))
        self.assertGreaterEqual(len(data.get('services', [])), 1)
        self.assertGreaterEqual(len(data.get('resources', [])), 1)


class SOSBeaconTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user('needhelp', 'needhelp@example.com', 'pass123')
        Profile.objects.update_or_create(user=self.user, defaults={'role': 3})

        self.volunteer_user = User.objects.create_user('vol_sos', 'vol_sos@example.com', 'pass123')
        Profile.objects.update_or_create(user=self.volunteer_user, defaults={'role': 2})

    def test_trigger_sos_creates_beacon(self):
        self.client.login(username='needhelp', password='pass123')
        response = self.client.post(reverse('sos-trigger'), {
            'message': 'Need immediate evacuation support',
        })
        self.assertEqual(response.status_code, 200)
        self.assertTrue(EmergencyBeacon.objects.filter(triggered_by=self.user).exists())

    def test_responder_can_acknowledge_beacon(self):
        beacon = EmergencyBeacon.objects.create(
            triggered_by=self.user,
            message='SOS test',
            status='open',
        )

        self.client.login(username='vol_sos', password='pass123')
        response = self.client.post(reverse('sos-ack', kwargs={'beacon_id': beacon.id}), {
            'action': 'ack',
        })
        self.assertEqual(response.status_code, 200)
        beacon.refresh_from_db()
        self.assertEqual(beacon.status, 'acknowledged')
        self.assertEqual(beacon.acknowledged_by, self.volunteer_user)
