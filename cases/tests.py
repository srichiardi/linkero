from django.test import TestCase

# Create your tests here.
class FindItemsTest(TestCase):
    def setUp(self):
        self.ea = EbayApi()
    
    # test if the method accepts an eBay site not correctly formatted
    def test_bad_ebay_site(self):
        wrong_site = 'PK'
        self.assertRaises(EbayBadsite)
    
    # test a page higer than the 100th limit allowed
    def test_wrong_page(self):
        wrong_page = 203
        self.assertRaises(EbayPageOutOfLimit)
    
    # test input without seller id nor keywords
    def test_missing_input(self):
        self.assertRaises(EbayMissingInput)
        
    # test if loading more than 20 items
    def test_too_many_items(self):
        self.assertRaises(EbayTooManyItems)