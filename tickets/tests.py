from datetime import datetime
from django.test import TestCase
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.utils.timezone import utc
from .models import Ticket, Tier, Department, Status, TicketComment
from companies.models import Company, Product, ProductVersion
from profiles.models import Profile

class TicketsViewsTestCase(TestCase):

    def setUp(self):
        company = Company.objects.create(name='company', notes='notes')
        department = Department.objects.create(name='department')
        tier = Tier.objects.create(name='tier', department=department)
        tier2 = Tier.objects.create(name='tier2', department=department)
        status = Status.objects.create(name='status')
        status2 = Status.objects.create(name='status2')
        user = User.objects.create_user(username='username', password='password')
        user.is_staff = True
        user.save()
        User.objects.create_user(username='username2', password='password2')
        profile = Profile.objects.create(user=user, company=company)
        product = Product.objects.create(name='product')
        ProductVersion.objects.create(major=1, minor=0, product=product)
        ticket = Ticket.objects.create(
            title='title',
            description='description',
            created_date_time=datetime.utcnow().replace(tzinfo=utc),
            profile_created=profile,
            profile_changed=profile,
            company=company,
            tier=tier,
            status=status,
            product=product,
        )
        TicketComment.objects.create(
            ticket=ticket,
            comment='comment',
            date_time=datetime.utcnow().replace(tzinfo=utc),
            profile=profile,
            is_public=True,
        )
        ticket.tier = tier2
        ticket.status = status2
        ticket.save()
        ticket.tier = tier
        ticket.status = status
        ticket.save()


    def test_index(self):
        resp = self.client.get(reverse('index'))
        self.assertEqual(resp.status_code, 200)


    def test_ticket(self):
        self.client.login(username='username', password='password')
        resp = self.client.get(reverse('ticket', args=[1]))
        self.assertEqual(resp.status_code, 200)
        self.assertIn('company', resp.content)


    def test_ticket_does_not_exist(self):
        self.client.login(username='username', password='password')
        resp = self.client.get(reverse('ticket', args=[100]))
        self.assertEqual(resp.status_code, 404)


    def test_ticket_access_denied_without_login(self):
        resp = self.client.get(reverse('ticket', args=[1]))
        self.assertEqual(resp.status_code, 302)


    def test_company(self):
        self.client.login(username='username', password='password')
        resp = self.client.get(reverse('company', args=[1]))
        self.assertEqual(resp.status_code, 200)
        self.assertIn('company', resp.content)


    def test_company_access_denied_without_login(self):
        resp = self.client.get(reverse('company', args=[1]))
        self.assertEqual(resp.status_code, 302)


    def test_ticket_good_edit(self):
        self.client.login(username='username', password='password')
        ticket = Ticket.objects.get(pk=1)
        self.assertEqual(ticket.tier.pk, 1)
        resp = self.client.post(reverse('ticket', args=[1]), {
                'tier': 1,
                'status': 1,
                'product': 1,
                'assignees': (1),
                'ticket_post': '',
            }
        )
        self.assertEqual(resp.status_code, 302)


    def test_comment_good(self):
        self.client.login(username='username', password='password')
        resp = self.client.post(reverse('ticket', args=[1]), {
                'comment': 'new comment',
                'attachment': '',
                'comment_post': '',
            }
        )
        self.assertEqual(resp.status_code, 302)


    def test_new_ticket(self):
        self.client.login(username='username', password='password')
        resp = self.client.get(reverse('new_ticket'))
        self.assertEqual(resp.status_code, 200)


    def test_new_ticket_good(self):
        self.client.login(username='username', password='password')
        resp = self.client.post(reverse('new_ticket'), {
                'title': 'title',
                'description': 'description',
                'company': 1,
                'tier': 1,
                'status': 1,
                'assignees': (1),
                'product': 1,
            }
        )
        self.assertEqual(resp.status_code, 302)


    def test_company_unicode(self):
        company = Company.objects.get(pk=1)
        self.assertEqual(company.__unicode__(), 'company')


    def test_status_unicode(self):
        status = Status.objects.get(pk=1)
        self.assertEqual(status.__unicode__(), 'status')


    def test_tier_unicode(self):
        tier = Tier.objects.get(pk=1)
        self.assertEqual(tier.__unicode__(), 'tier')


    def test_department_unicode(self):
        department = Department.objects.get(pk=1)
        self.assertEqual(department.__unicode__(), 'department')


    def test_ticket_unicode(self):
        ticket = Ticket.objects.get(pk=1)
        self.assertEqual(ticket.__unicode__(), 'title')


    def test_ticketComment_unicode(self):
        ticketComment = TicketComment.objects.get(pk=1)
        self.assertEqual(ticketComment.__unicode__(), 'comment')


    def test_ticket_absolute_url(self):
        ticket = Ticket.objects.get(pk=1)
        self.assertEqual(ticket.get_absolute_url(), reverse('ticket', args=[ticket.pk]))
