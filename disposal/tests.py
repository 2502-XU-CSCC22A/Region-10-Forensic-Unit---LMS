from django.test import TestCase, Client
from django.urls import reverse
from django.utils import timezone
from django.contrib.auth.models import User
from config.models import Asset, AssetStatus, Category, Personnel
from .models import DisposalItem, DisposalActivityLog

class DisposalBranchTests(TestCase):
    def setUp(self):

        self.client = Client()
        self.user = User.objects.create_user(username='admin', password='password123')
        
        self.status_ber = AssetStatus.objects.create(status_id=4, status_name="BER")
        self.status_disposed = AssetStatus.objects.create(status_id=5, status_name="Disposed")

        self.cat_firearms = Category.objects.create(category_name='firearms')
        self.cat_comms = Category.objects.create(category_name='communications')

        self.personnel = Personnel.objects.create(PersonnelID=1, Name="John Doe")

        self.asset_firearm = Asset.objects.create(
            model="Glock 17", 
            serial_no="G123", 
            category=self.cat_firearms, 
            status=self.status_ber
        )
        
        self.asset_radio = Asset.objects.create(
            model="Walkie Talkie", 
            serial_no="W456", 
            category=self.cat_comms, 
            status=self.status_ber
        )

        self.disposal_item = DisposalItem.objects.create(
            asset_ptr=self.asset_radio,
            processed_by=self.personnel,
            disposal_reason="Marked as BER from Communications",
            status_id=4 
        )

        self.client.login(username='admin', password='password123')

    def test_status_card_counts(self):
       
        response = self.client.get(reverse('disposal:disposal_list'))
        self.assertEqual(response.status_code, 200)

        self.assertEqual(response.context['total_ber'], 1)

        self.assertEqual(response.context['comms_ber'], 1)
        self.assertEqual(response.context['firearms_ber'], 0) # Firearm exists but not in DisposalItem table yet

    def test_finalize_removal_soft_delete(self):
        """Test that removing an asset changes status to 5 and logs activity."""
        url = reverse('disposal:finalize_removal', kwargs={'pk': self.disposal_item.pk})
        response = self.client.post(url) 

        self.asset_radio.refresh_from_db()

        self.assertEqual(self.asset_radio.status_id.status_id, 5)

        log_exists = DisposalActivityLog.objects.filter(asset=self.asset_radio, action_type='REMOVE').exists()
        self.assertTrue(log_exists)
        
        self.assertRedirects(response, reverse('disposal:history_log'))

    def test_removal_summary_today(self):
        """Test count of items disposed specifically today."""
        response = self.client.get(reverse('disposal:disposal_list'))
        self.assertEqual(response.context['ber_today_count'], 1)

    def test_pagination_limit(self):
        for i in range(20):
            Asset.objects.create(model=f"Asset {i}", status=self.status_ber, category=self.cat_comms)
            DisposalItem.objects.create(
                asset_ptr=Asset.objects.latest('id'),
                disposal_reason="Testing",
                status_id=4
            )
            
        response = self.client.get(reverse('disposal:disposal_list'))
        # Your paginator is set to 15
        self.assertEqual(len(response.context['disposal_items']), 15)

    def test_search_functionality(self):
        response = self.client.get(reverse('disposal:disposal_list'), {'search': 'Walkie'})
        # Assert that only the Walkie Talkie appears in results
        # (This requires updating your view to handle request.GET.get('search'))
        pass