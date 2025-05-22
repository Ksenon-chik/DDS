import unittest
from django.urls import reverse
from django.test import Client, TestCase
from django.contrib.auth.models import User
from dds_app.models import Item, Category, ExchangeProposal


class DDSAppTestCase(TestCase):

    def setUp(self):
        self.client = Client()
        self.user1 = User.objects.create_user(username='u1', password='pass')
        self.user2 = User.objects.create_user(username='u2', password='pass')
        self.category = Category.objects.create(name='CatX')
        self.client.login(username='u1', password='pass')

    def test_html_item_crud_and_search(self):
        # Создание объявления
        data = {
            'title': 'NewItem',
            'description': 'Desc',
            'category_name': self.category.name,
            'condition_text': 'new',
        }
        resp = self.client.post(reverse('ad_create'), data)
        self.assertEqual(resp.status_code, 200)
        item = Item.objects.get(title='NewItem')
        self.assertEqual(item.owner.username, 'u1')
        self.assertEqual(item.category.name, 'CatX')
        self.assertEqual(item.condition, 'new')

        # Поиск
        resp = self.client.get(reverse('index') + '?q=NewItem')
        self.assertContains(resp, 'NewItem')

        # Попытка редактировать чужое объявление
        item2 = Item.objects.create(
            owner=self.user2,
            title='X', description='Y',
            category=self.category, condition='used'
        )
        resp = self.client.post(reverse('ad_update', args=[item2.pk]), {
            'title': 'X2', 'description': 'Y2',
            'category_name': self.category.name,
            'condition_text': 'new'
        })
        self.assertEqual(resp.status_code, 302)
        item2.refresh_from_db()
        self.assertEqual(item2.title, 'X')  # не изменился

        # Удаление
        resp = self.client.post(reverse('ad_delete', args=[item.pk]))
        self.assertEqual(resp.status_code, 302)
        self.assertFalse(Item.objects.filter(pk=item.pk).exists())

    def test_html_proposal_crud(self):
        # Создание объявлений
        item1 = Item.objects.create(owner=self.user1, title='I1', description='D',
                                    category=self.category, condition='new')
        item2 = Item.objects.create(owner=self.user2, title='I2', description='D',
                                    category=self.category, condition='new')

        # Создание предложения
        resp = self.client.post(reverse('proposal_create', args=[item2.pk]), {
            'ad_sender': item1.pk, 'comment': 'Swap?'
        })
        self.assertEqual(resp.status_code, 200)
        proposals = ExchangeProposal.objects.filter(ad_sender=item1, ad_receiver=item2)
        self.assertTrue(proposals.exists())
        prop = proposals.first()
        self.assertEqual(prop.status, 'pending')

        # Обновление статуса от user2
        self.client.logout()
        self.client.login(username='u2', password='pass')
        resp = self.client.post(reverse('proposal_update_status', args=[prop.pk]), {
            'status': 'accepted'
        })
        self.assertEqual(resp.status_code, 302)
        prop.refresh_from_db()
        self.assertEqual(prop.status, 'accepted')
