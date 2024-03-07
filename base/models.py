from django.db import models
from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.utils import timezone

class CustomUser(AbstractUser):
    phone = models.CharField(max_length=10, default="1234567890", unique=True)
    mpin = models.CharField(max_length=5, default="00000")
    groups = None
    user_permissions = None

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)  # Call the base `save` method first
        if not hasattr(self, 'wallet'):  # Check if wallet already exists
            Wallet.objects.create(user=self)  # Create a new wallet for the user

    def __str__(self) -> str:
        return self.username

class TeamDetail(models.Model):
    team_name = models.CharField(max_length=100, default="Team Name")
    team_leader = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    phone_number = models.CharField(max_length=10,null=False,blank=False, default="1234567890")
    optional_phone_number = models.CharField(max_length=10,null=True, blank=True, default="1234567890")
        
class Tournament(models.Model):
    tournament_name = models.CharField(max_length=100, default="Tournament Name")
    slots_available = models.PositiveIntegerField(default=12)
    slots_total = models.PositiveIntegerField(default=12)
    room_id = models.CharField(max_length=100, default="Your Room ID will appear 5 mins before the tournament starts")
    room_password = models.CharField(max_length=100, default="Your Room Password will appear 5 mins before the tournament starts")
    entry_fee = models.DecimalField(max_digits=5, decimal_places=0, default=0)
    prize_pool = models.DecimalField(max_digits=10, decimal_places=0, default=0)
    First_prize = models.DecimalField(max_digits=10, decimal_places=0, default=0)
    Second_prize = models.DecimalField(max_digits=10, decimal_places=0, default=0)
    Third_prize = models.DecimalField(max_digits=10, decimal_places=0, default=0)
    Fourth_prize = models.DecimalField(max_digits=10, decimal_places=0, default=0)
    participants = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name="participants", blank=True)
    registration_time = models.DateTimeField(default=timezone.now())
    tournament_time = models.DateTimeField(default=timezone.now())
    participant_team_name = models.ManyToManyField(TeamDetail, related_name="participant_team_name", blank=True)

    def __str__(self) -> str:
        return self.tournament_name 

class Matches(models.Model):
    tournament = models.ForeignKey(Tournament, on_delete=models.CASCADE)
    match_number = models.CharField(max_length=100, default="Match Number")

    class Meta:
        unique_together = (('tournament', 'match_number'),)

class UTRID(models.Model):
    """
    Model to store UTR IDs for transactions.
    """
    utr_id = models.CharField(max_length=255)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.utr_id

class Transaction(models.Model):
    """
    Model to represent a financial transaction.
    """
    STATUS_CHOICES = (("Pending", "Pending"), ("Rejected", "Rejected"), ("Approved", "Approved"))
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10,decimal_places=0)
    description = models.CharField(max_length=255)
    timestamp = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=10, default="Pending", choices=STATUS_CHOICES)
    transaction_details = models.CharField(max_length=255, blank=True)
    utr_id = models.ForeignKey(UTRID, on_delete=models.SET_NULL, null=True, blank=True)  # Optional UTR ID

    def __str__(self):
        return f"{self.user.username} {self.user.phone} {self.status} {self.description}"

    def save(self, *args, **kwargs):
        """
        Override the save method to update wallet balance when status changes to "approved".
        """
        if self.status == 'Approved' and self.pk:  # Avoid unnecessary updates on initial creation
            wallet = self.user.wallet
            if self.description == "Deposit":
                wallet.balance += self.amount
            if self.description == "Withdrawal":
                wallet.balance -= abs(self.amount)  # Use absolute value for negative amount
            wallet.save()

        if self.utr_id and self.utr_id.utr_id == self.transaction_details:
            self.status = "Approved"
            if self.status != "Approved":  # Check if status wasn't already updated (prevents double update)
                wallet = self.user.wallet
                if self.description == "Deposit":
                    wallet.balance += self.amount
                #For withdrawals, requests should be approved manually
                wallet.save()

        super().save(*args, **kwargs)

class Wallet(models.Model):
    """
    Model to represent a user's wallet.
    """
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, primary_key=True)
    balance = models.DecimalField(max_digits=10, decimal_places=0, default=0)

    def __str__(self):
        return f"Wallet for {self.user.username}"

    def add_transaction(self, amount, transaction_id, description="Deposit"):
        """
        Adds a transaction to the wallet and updates the balance.
        """
        transaction = Transaction.objects.create(
            user=self.user, amount=amount, description=description, transaction_details=transaction_id
        )
        return transaction

    def subtract_transaction(self, amount, description="Withdrawal"):
        """
        Subtracts a transaction from the wallet and updates the balance.
        Raises an error if the amount exceeds the balance.
        """
        if amount > self.balance:
            raise ValueError("Insufficient funds")
        transaction = Transaction.objects.create(
            user=self.user, amount=-amount, description=description
        )
        return transaction
