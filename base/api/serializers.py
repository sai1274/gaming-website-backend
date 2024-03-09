from base.models import CustomUser, Tournament
from rest_framework import serializers

class MatchesSerializer(serializers.Serializer):
    tournament = serializers.PrimaryKeyRelatedField(queryset=Tournament.objects.all())  # Assuming user is a foreign key
    match_number = serializers.CharField(max_length=255)

    def validate(self, attrs):
        # Add custom validation logic here if needed
        return attrs


class UserSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=255)
    email = serializers.EmailField()
    phone = serializers.CharField(max_length=15)
    mpin = serializers.CharField(max_length=6)

    def validate(self, attrs):
        # Add custom validation logic here if needed
        return attrs


class WalletSerializer(serializers.Serializer):
    user = serializers.PrimaryKeyRelatedField(queryset=CustomUser.objects.all())  # Assuming user is a foreign key
    balance = serializers.DecimalField(max_digits=10, decimal_places=2)

    def validate(self, attrs):
        # Add custom validation logic here if needed
        return attrs


class TransactionSerializer(serializers.Serializer):
    user = serializers.PrimaryKeyRelatedField(queryset=CustomUser.objects.all())  # Assuming user is a foreign key
    amount = serializers.DecimalField(max_digits=10, decimal_places=2)
    description = serializers.CharField(max_length=255)
    timestamp = serializers.DateTimeField(read_only=True)
    status = serializers.CharField(max_length=20)
    transaction_details = serializers.CharField(max_length=255)

    def validate(self, attrs):
        # Add custom validation logic here if needed
        return attrs


class TournamentSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    tournament_name = serializers.CharField(max_length=255)
    slots_available = serializers.IntegerField()
    slots_total = serializers.IntegerField()
    room_id = serializers.CharField(max_length=255)
    room_password = serializers.CharField(max_length=255)
    entry_fee = serializers.DecimalField(max_digits=10, decimal_places=2)
    prize_pool = serializers.DecimalField(max_digits=10, decimal_places=2)
    First_prize = serializers.DecimalField(max_digits=10, decimal_places=2)
    Second_prize = serializers.DecimalField(max_digits=10, decimal_places=2)
    Third_prize = serializers.DecimalField(max_digits=10, decimal_places=2)
    Fourth_prize = serializers.DecimalField(max_digits=10, decimal_places=2)
    participants = serializers.PrimaryKeyRelatedField(many=True, queryset=CustomUser.objects.all())
    registration_time = serializers.DateTimeField(read_only=True)
    tournament_time = serializers.DateTimeField()
    participant_team_name = serializers.CharField(max_length=255)

    def validate(self, attrs):
        # Add custom validation logic here if needed
        return attrs


class TeamDetailSerializer(serializers.Serializer):
    team_name = serializers.CharField(max_length=255)
    team_leader = serializers.CharField(max_length=255)
    phone_number = serializers.CharField(max_length=15)
    optional_phone_number = serializers.CharField(max_length=15, required=False)

    def validate(self, attrs):
        # Add custom validation logic here if needed
        return attrs

# Path: api/views.py
# class MatchesSerializer(serializers.Serializer):
    # Todo: Add the model to be serialized here
