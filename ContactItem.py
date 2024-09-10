class ContactItem:
    def __init__(self, url="", emails=None, phones=None, facebook=None, twitter=None, instagram=None, linkedin=None, youtube=None, tiktok=None, contact_sources=None):
        self.url = url
        self.emails = emails or []
        self.phones = phones or []
        self.facebook = facebook or []
        self.twitter = twitter or []
        self.instagram = instagram or []
        self.linkedin = linkedin or []
        self.youtube = youtube or []
        self.tiktok = tiktok or []
        self.contact_sources = contact_sources or []
        
    def __str__(self):
        return f"URL: {self.url}\n" \
               f"Emails: {', '.join(self.emails)}\n" \
               f"Phones: {', '.join(self.phones)}\n" \
               f"Facebook: {', '.join(self.facebook)}\n" \
               f"Twitter: {', '.join(self.twitter)}\n" \
               f"Instagram: {', '.join(self.instagram)}\n" \
               f"LinkedIn: {', '.join(self.linkedin)}\n" \
               f"YouTube: {', '.join(self.youtube)}\n" \
               f"Tiktok: {', '.join(self.tiktok)}\n" \
               f"Contact_sources: {', '.join(self.contact_sources)}"

    def concatenate_lists(self, other_contact):
        self.emails = list(set(self.emails + other_contact.emails))
        self.phones = list(set(self.phones + other_contact.phones))
        self.facebook = list(set(self.facebook + other_contact.facebook))
        self.twitter = list(set(self.twitter + other_contact.twitter))
        self.instagram = list(set(self.instagram + other_contact.instagram))
        self.linkedin = list(set(self.linkedin + other_contact.linkedin))
        self.youtube = list(set(self.youtube + other_contact.youtube))
        self.tiktok = list(set(self.tiktok + other_contact.tiktok))
        self.contact_sources = list(set(self.contact_sources + other_contact.contact_sources))

    def is_empty(self):    
        """
        This function checks if the object has any non-empty attributes.

        Args:
        obj: The object to be checked.

        Returns:
        True if all attributes are empty, False otherwise.
        """
        # Check each attribute if it's empty or not
        return ((self.emails is None or not self.emails) and
            (self.phones is None or not self.phones) and
            (self.facebook is None or not self.facebook) and
            (self.twitter is None or not self.twitter) and
            (self.instagram is None or not self.instagram) and
            (self.linkedin is None or not self.linkedin) and
            (self.youtube is None or not self.youtube) and
            (self.tiktok is None or not self.tiktok) and
            (self.contact_sources is None or not self.contact_sources))
    
    def add_contact_sources(self):
        if self.is_empty():
            self.contact_sources = [f"{self.url} ==> {not self.is_empty()}"]
        else:
            self.contact_sources = [f"{self.url} ==> {not self.is_empty()}"]