from celery import task
from django.core.mail import send_mail
from cases.ebayapi import EbayApi
from cases.models import EbayItem


@task()
def send_ebay_listing_report(to_email='s.richiardi@gmail.com', query_id=None):
    ea = EbayApi()
    list_of_items = [332094821083, 232698814292, 263757357723]
    j_items = ea.get_multiple_items(items_list=list_of_items)
    # assuming j_items['Ack'] == 'Success'
    for item in j_items['Item']:
        item['lnkr_query_id'] = query_id
        e_item = EbayItem(**item)
        e_item.save()
    send_mail('first email from Linkero', 'this is the first email that linkero sends, aren\' you proud?', 'LinkeroReports@linkero.ie', ['s.richiardi@gmail.com'], fail_silently=False)
    