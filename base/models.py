from django.db import models
from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
# from .api.serializers import TeamDetailSerializer
class CustomUser(AbstractUser):
    phone = models.CharField(max_length=10, default="1234567890", unique=True)
    mpin = models.CharField(max_length=5, default="00000")
    state = models.CharField(max_length=100, default="Andhra Pradesh")

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)  # Call the base `save` method first
        if not hasattr(self, 'wallet'):  # Check if wallet already exists
            Wallet.objects.create(user=self)  # Create a new wallet for the user

    def __str__(self) -> str:
        return self.username

class TeamDetail(models.Model):
    team_name = models.CharField(max_length=100, default="Team Name")
    team_leader = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    in_game_name = models.CharField(max_length=100, default="In Game Name")
    phone_number = models.CharField(max_length=10,null=False,blank=False, default="1234567890")
    optional_phone_number = models.CharField(max_length=10,null=True, blank=True, default="1234567890")

    def __str__(self) -> str:
        return self.team_name + self.team_leader.username
     
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
    
    def save(self):
        # Create up to 6 matches
        if not self.pk:
            for i in range(1, 7):
                match_number = str(i)
                Match.objects.create(tournament=self, match_number=match_number)
        super().save()

class Match(models.Model):
    tournament = models.ForeignKey(Tournament, on_delete=models.CASCADE)
    match_number = models.CharField(max_length=100, default="1")

    class Meta:
        unique_together = (('tournament', 'match_number'),)
    
    def __str__(self) -> str:
        return self.tournament.tournament_name +" " + self.match_number
    
    def submit_results(self):
        teams_data = self.tournament.participant_team_name.all()
        for team_data in teams_data:
            team = TeamDetail.objects.get(pk = team_data.id)
            TeamStat.objects.create(team = team, tournament = self.tournament, match_number = self)
        super().save()

class UTRID(models.Model):
    """
    Model to store UTR IDs for transactions.
    """
    utr_id = models.CharField(max_length=255)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.utr_id
    
    def save(self, *args, **kwargs):
        """
        Override the save method to update wallet balance when status changes to "approved".
        """
        transactions = Transaction.objects.filter(transaction_details=self.utr_id)
        for transaction in transactions:
            transaction.status = "Approved"
            if transaction.status != "Approved":
                wallet = transaction.user.wallet
                if transaction.description == "Deposit":
                    wallet.balance += transaction.amount
            transaction.save()
        super().save(*args, **kwargs)

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
    utr_id = models.ForeignKey(UTRID, on_delete=models.CASCADE, blank=True, null=True)

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

class TeamStat(models.Model):
    team = models.ForeignKey(TeamDetail, on_delete=models.CASCADE)
    tournament = models.ForeignKey(Tournament, on_delete=models.CASCADE)
    match_number = models.ForeignKey(Match, on_delete=models.CASCADE) 
    player_1 = models.IntegerField(default=0)
    player_2 = models.IntegerField(default=0)
    player_3 = models.IntegerField(default=0)
    player_4 = models.IntegerField(default=0)
    position_points = models.PositiveIntegerField(default=0)
    booyah = models.PositiveIntegerField(default=0)
    matches_played = models.PositiveIntegerField(default=0)

    class Meta:
        unique_together = (('team', 'tournament', 'match_number'),)

    def __str__(self):
        return f"{self.team.team_name} {self.tournament.tournament_name} {self.match_number.match_number}"

    @classmethod
    def aggregate_stats(cls, tournament):
        team_stats = cls.objects.filter(tournament=tournament)
        match_numbers = set(team_stat.match_number for team_stat in team_stats)
        aggregated_stats = {}

        for match_number in match_numbers:
            match_stats = team_stats.filter(match_number=match_number)
            aggregated_stats[match_number.match_number] = {
                'player_1': sum(match_stat.player_1 for match_stat in match_stats),
                'player_2': sum(match_stat.player_2 for match_stat in match_stats),
                'player_3': sum(match_stat.player_3 for match_stat in match_stats),
                'player_4': sum(match_stat.player_4 for match_stat in match_stats),
                'position_points': sum(match_stat.position_points for match_stat in match_stats),
                'matches_played': len(match_stats)
            }

        return aggregated_stats