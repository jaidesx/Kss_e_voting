from django.db import models


class Election(models.Model):
    title = models.CharField(max_length=200, unique=True)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=False, help_text="Only one election can be active at a time.")
    is_demo = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        # Enforce single active election
        if self.is_active:
            Election.objects.exclude(pk=self.pk).update(is_active=False)
        
        # When creating a new demo election, delete all other demo elections
        if self.is_demo and not self.pk:
            Election.objects.filter(is_demo=True).delete()
            
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.title} (Demo)" if self.is_demo else self.title


class Post(models.Model):
    election = models.ForeignKey(Election, on_delete=models.CASCADE, related_name='posts', null=True, blank=True)
    title = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    required_selections = models.PositiveIntegerField(
        default=1,
        help_text="Number of candidates that must be selected for this position."
    )

    class Meta:
        unique_together = ('election', 'title')

    def is_voter_eligible(self, voter):
        """Check if a voter is eligible to vote for this post.
        No rules = open to all voters.
        """
        eligible_houses = self.eligible_houses.all()
        if not eligible_houses.exists():
            return True
        if not voter.house:
            return False
        return eligible_houses.filter(house=voter.house).exists()

    def __str__(self):
        return f"{self.title} ({self.election.title})"


class EligibleHouse(models.Model):
    HOUSE_CHOICES = [
        ('AGAKHAN', 'Agakhan'),
        ('AFRICA', 'Africa'),
        ('KAKUNGULU', 'Kakungulu'),
        ('LUWANGULA', 'Luwangula'),
    ]

    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='eligible_houses')
    house = models.CharField(max_length=50, choices=HOUSE_CHOICES)

    class Meta:
        unique_together = ('post', 'house')
        verbose_name = 'Eligible House'
        verbose_name_plural = 'Eligible Houses'

    def __str__(self):
        return f"{self.get_house_display()} → {self.post.title}"

