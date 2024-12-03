from django.db import models
from django.conf import settings
from datetime import date

class TimestampModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)

    class Meta:
        abstract = True

class Respect(TimestampModel):
    name = models.CharField(max_length=10)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']

class Relation(TimestampModel):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']

class Pastorate(TimestampModel):
    pastorate_name = models.CharField(max_length=100)
    pastorate_short_name = models.CharField(max_length=10)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    def __str__(self):
        return self.pastorate_name

class Church(TimestampModel):
    church_name = models.CharField(max_length=100)
    abode = models.CharField(max_length=100)
    short_name = models.CharField(max_length=10)
    pastorate = models.ForeignKey(Pastorate, on_delete=models.CASCADE)

    def __str__(self):
        return self.church_name

class Area(TimestampModel):
    church = models.ForeignKey(Church, on_delete=models.CASCADE)
    area_name = models.CharField(max_length=100)
    area_id = models.CharField(max_length=20, unique=True)

    def __str__(self):
        return f"{self.area_name} ({self.area_id})"

    class Meta:
        ordering = ['area_id']
        verbose_name_plural = 'Areas'

class Fellowship(TimestampModel):
    area = models.ForeignKey(Area, on_delete=models.CASCADE)
    fellowship_name = models.CharField(max_length=100)
    fellowship_id = models.CharField(max_length=20, unique=True)
    address = models.TextField(blank=True)

    def __str__(self):
        return f"{self.fellowship_name} ({self.fellowship_id})"

    class Meta:
        ordering = ['fellowship_id']
        verbose_name_plural = 'Fellowships'

class Family(TimestampModel): 
    family_id = models.CharField(max_length=20)
    area = models.ForeignKey(Area, on_delete=models.CASCADE)
    fellowship = models.ForeignKey(Fellowship, on_delete=models.CASCADE)
    respect = models.ForeignKey(Respect, on_delete=models.PROTECT)
    initial = models.CharField(max_length=10)
    family_head = models.CharField(max_length=100)
    mobile = models.CharField(max_length=15)
    email = models.EmailField()
    address = models.TextField()
    prayer_points = models.TextField()

    def __str__(self):
        return f"{self.family_head}'s Family"

    def get_church(self):
        return self.area.church

    @classmethod
    def get_next_number(cls, area):
        # Get the last family in this area
        last_family = cls.objects.filter(
            area=area
        ).order_by('-family_id').first()

        if last_family:
            try:
                # Extract the numeric part from the last family ID
                # Format: AREA-XXX where XXX is the family number
                parts = last_family.family_id.split('-')
                if len(parts) >= 2:
                    last_number = int(parts[-1])
                    next_number = last_number + 1
                else:
                    next_number = 1
            except (ValueError, IndexError):
                next_number = 1
        else:
            next_number = 1

        return next_number

    class Meta:
        unique_together = ['family_id', 'area']
        verbose_name_plural = 'Families'

class Member(TimestampModel):
    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other')
    ]

    family = models.ForeignKey(Family, on_delete=models.CASCADE)
    member_id = models.CharField(max_length=30, unique=True)  # Increased length for new format
    aadhar_number = models.CharField(max_length=12, blank=True)
    respect = models.ForeignKey(Respect, on_delete=models.PROTECT)
    initial = models.CharField(max_length=10, blank=True)
    name = models.CharField(max_length=100)
    relation = models.ForeignKey(Relation, on_delete=models.PROTECT)
    sex = models.CharField(max_length=1, choices=GENDER_CHOICES)
    dob = models.DateField(null=True, blank=True)
    dom = models.DateField(null=True, blank=True)
    working = models.CharField(max_length=100, blank=True)
    working_place = models.CharField(max_length=100, blank=True)
    baptised = models.BooleanField(default=False)
    date_of_bap = models.DateField(null=True, blank=True)
    conformed = models.BooleanField(default=False)
    date_of_conf = models.DateField(null=True, blank=True)
    death = models.BooleanField(default=False)
    date_of_death = models.DateField(null=True, blank=True)
    image = models.ImageField(upload_to='member_images/', null=True, blank=True)
    spouse = models.OneToOneField('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='spouse_of')

    def __str__(self):
        return self.name

    @property
    def age(self):
        if self.dob:
            today = date.today()
            return today.year - self.dob.year - ((today.month, today.day) < (self.dob.month, self.dob.day))
        return None

    @property
    def marriage_years(self):
        if self.dom:
            today = date.today()
            return today.year - self.dom.year - ((today.month, today.day) < (self.dom.month, self.dom.day))
        return None

    @classmethod
    def get_next_number(cls, family):
        # Get the last member in this family
        last_member = cls.objects.filter(
            family=family
        ).order_by('-member_id').first()

        if last_member:
            try:
                # Get the last two digits after the last hyphen
                last_number = int(last_member.member_id.split('-')[-1])
                next_number = last_number + 1
            except (ValueError, IndexError):
                next_number = 2  # Start with 02 if there's an error, since 01 is for family head
        else:
            # First member (family head) gets number 01
            next_number = 2  # Start with 02 for new members since 01 is reserved for family head

        return next_number

    @classmethod
    def generate_member_id(cls, family, is_head=False):
        if is_head:
            member_number = 1  # Family head always gets 01
        else:
            member_number = cls.get_next_number(family)
        
        return f"{family.family_id}-{member_number:02d}"
