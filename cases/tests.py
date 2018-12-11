from django.test import TestCase
from cases.ebayapi import EbayApi

# Create your tests here.
class FindItemsTest(TestCase):
    def setUp(self):
        self.ea = EbayApi()
    
    # test if the method accepts an eBay site not correctly formatted
    def test_bad_ebay_site(self):
        wrong_site = 'PK'
        with self.assertRaises(EbayBadSite):
            self.ea.find_items(ebay_site=wrong_site, keywords="baby oil")
    
#     # test a page higer than the 100th limit allowed
#     def test_wrong_page(self):
#         wrong_page = 203
#         self.assertRaises(EbayPageOutOfLimit)
#     
#     # test input without seller id nor keywords
#     def test_missing_input(self):
#         self.assertRaises(EbayMissingInput)
#         
#     # test if loading more than 20 items
#     def test_too_many_items(self):
#         self.assertRaises(EbayTooManyItems)