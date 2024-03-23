from .serializers import (
    UserSerializer,
    WalletSerializer,
    TransactionSerializer,
    TournamentSerializer,
    TeamDetailSerializer,
    MatchSerializer,
)
from rest_framework.decorators import api_view, permission_classes
from base.models import (
    CustomUser,
    Wallet,
    Transaction,
    Tournament,
    TeamDetail,
    Match,
    TeamStat,
)
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework import status
from django.core.mail import send_mail
from django.contrib.auth import login, logout, get_user_model, authenticate
from rest_framework_simplejwt.tokens import RefreshToken, Token
from rest_framework_simplejwt.exceptions import TokenError
from .permissions import CustomStaffPermission


@api_view(["POST"])
@permission_classes([AllowAny])
def get_new_token(request):
    print(request.data.get("refresh"))
    try:
        print("here")
        refresh_token = request.data.get("refresh")
        print("here")

        token_obj = RefreshToken(refresh_token)
        print("here")
        new_token = token_obj.access_token
        return Response({"token": str(new_token)}, status=status.HTTP_200_OK)
    except TokenError as e:
        return Response(str(e), status=status.HTTP_401_UNAUTHORIZED)


@api_view(["GET"])
@permission_classes([AllowAny])
def tournaments(request):
    if request.method == "GET":
        tournaments = Tournament.objects.all()
        serializer = TournamentSerializer(tournaments, many=True)
        return Response(serializer.data)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def create_team(request):
    serializer = TeamDetailSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response({"team_id": serializer.id}, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["GET", "POST"])
@permission_classes([IsAuthenticated])
def users(request):
    if request.method == "GET":
        users = CustomUser.objects.all()
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data)
    elif request.method == "POST":
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def book_slot(request, pk):
    try:
        tournament = Tournament.objects.get(pk=pk)
    except Tournament.DoesNotExist:
        return Response(
            {"error": "Tournament not found"}, status=status.HTTP_404_NOT_FOUND
        )

    user_wallet = Wallet.objects.get(user=request.user)
    if user_wallet.balance < tournament.entry_fee:
        return Response(
            {"error": "Insufficient balance",
             "balance_amount" : user_wallet.balance,
             "tournament_entry_fee" : tournament.entry_fee,
             "user" : request.user.username}, status=status.HTTP_400_BAD_REQUEST
        )

    if tournament.slots_available < 1:
        return Response(
            {"error": "No slots available"}, status=status.HTTP_400_BAD_REQUEST
        )

    if request.user in tournament.participants.all():
        serializer = TournamentSerializer(tournament)
        return Response(
            {"message": "Slot already booked", "tournament": serializer.data},
            status=status.HTTP_200_OK,
        )

    print(request, dict(request.data))
    team = TeamDetail.objects.create(
        team_leader=request.user,
        team_name=request.data["team_name"],
        in_game_name=request.data["in_game_name"],
        phone_number=request.data["phone_number"],
        optional_phone_number=request.data["optional_phone_number"],
    )
    tournament.participant_team_name.add(team)
    tournament.slots_available -= 1
    tournament.participants.add(request.user)
    transaction = Transaction.objects.create(
        user=request.user,
        amount=tournament.entry_fee,
        description=f"Tournament entry fee, {tournament.tournament_name}",
        status="Approved",
    )
    transaction.save()
    user_wallet.balance -= tournament.entry_fee
    user_wallet.save()
    # Allow subsequent team association (assuming team_id is provided in request):
    if "team_id" in request.POST:  # Check for POST method and team_id
        try:
            team = TeamDetail.objects.get(pk=request.POST["team_id"])

        except (KeyError, TeamDetail.DoesNotExist):
            return Response(
                {"error": "Invalid or non-existent team details provided"},
                status=status.HTTP_400_BAD_REQUEST,
            )

    tournament.save()
    serializer = TournamentSerializer(tournament)
    return Response(
        {"message": "Slot booked successfully", "tournament": serializer.data},
        status=status.HTTP_200_OK,
    )


@api_view(["POST"])
@permission_classes([AllowAny])
def custom_login(request):
    username = request.data.get("username")
    password = request.data.get("password")
    user = authenticate(request, username=username, password=password)

    if user is not None:
        login(request, user)
        refresh = RefreshToken.for_user(user)
        # print("search", str(refresh), str(refresh.access_token))
        mpin = CustomUser.objects.get(username=username).mpin
        return Response(
            {
                "refresh": str(refresh),
                "access": str(refresh.access_token),
                "mpin": mpin,
            },
            status=status.HTTP_200_OK,
        )

    return Response(
        {"error": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED
    )


@api_view(["POST"])
@permission_classes([AllowAny])
def register(request):
    data = request.data
    username = data.get("username")
    password = data.get("password")
    email = data.get("email")
    phone = data.get("phoneNumber")
    mpin = data.get("mpin")
    state = data.get("state")

    if not all([username, password, email, phone, mpin, state]):
        return Response(
            {"error": "All fields are required"}, status=status.HTTP_400_BAD_REQUEST
        )

    CustomUser = get_user_model()
    try:
        user = CustomUser.objects.create_user(
            username=username, password=password, email=email, phone=phone, mpin=mpin
        )
        # send_registration_email(user)  # Call the mail sending function
        print("Registration email sent")
        login(request, user)
        return Response(
            {"message": "Registration successful"}, status=status.HTTP_201_CREATED
        )
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


def send_registration_email(user):
    team_name = "Agent E-Sports"
    message = f"Hello {user.username},\n\nYou have been successfully registered.\n\nThank you for registering with us.\n\nRegards,\nTeam {team_name}"
    subject = "Registration"
    recipient_list = [user.email]
    from_email = None  # Set your email address here
    send_mail(subject, message, from_email, recipient_list, fail_silently=False)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def wallet(request):
    wallet = Wallet.objects.get(user=request.user)
    serializer = WalletSerializer(wallet)
    transactions = Transaction.objects.filter(user=request.user)
    transactions_serializer = TransactionSerializer(transactions, many=True)
    data = {"wallet": serializer.data, "transactions": transactions_serializer.data}
    return Response(data, status=status.HTTP_200_OK)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def deposit(request):
    amount = int(request.data.get("amount"))
    transaction_id = request.data.get("utrid")
    wallet = Wallet.objects.get(user=request.user)
    wallet.add_transaction(amount, transaction_id)
    serializer = WalletSerializer(wallet)
    return Response(serializer.data)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def withdraw(request):
    amount = int(request.data.get("amount"))
    wallet = Wallet.objects.get(user=request.user)
    wallet.subtract_transaction(amount)
    serializer = WalletSerializer(wallet)
    return Response(serializer.data)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def custom_logout(request):
    logout(request)
    return Response({"message": "Logout successful"}, status=status.HTTP_200_OK)


@api_view(["GET"])
def user_info(request):
    user = request.user
    user_data = CustomUser.objects.get(username=user)
    serializer_context = {
        "request": request
    }  # Include request for potential contextual information
    user_serializer = UserSerializer(user_data, context=serializer_context)

    return Response(user_serializer.data, status=status.HTTP_200_OK)


@api_view(["GET"])
def user_tournaments(request):
    user = request.user
    tournaments_participated = Tournament.objects.filter(participants__username=user)

    serializer_context = {"request": request}
    tournaments_serializer = TournamentSerializer(
        tournaments_participated, many=True, context=serializer_context
    )
    return Response(tournaments_serializer.data, status=status.HTTP_200_OK)


@api_view(["GET"])
def match_details(request, pk):
    try:
        tournament = Tournament.objects.get(pk=pk)
        match = tournament.match_set.all()  # Retrieve related Match

        serializer = TournamentSerializer(tournament)
        match_serializer = MatchSerializer(
            match, many=True
        )  # Serialize multiple matches
        participants_team = TeamDetailSerializer(
            tournament.participant_team_name.all(), many=True
        )

        return Response(
            {
                "data": serializer.data,
                "match": match_serializer.data,  # Use serialized match data
                "all_matches": MatchSerializer(
                    Match.objects.all(), many=True
                ).data,  # Serialize all matches separately
                "participants_teams": participants_team.data,
            },
            status=status.HTTP_200_OK,
        )

    except Tournament.DoesNotExist:
        return Response(
            {"error": "Tournament not found"}, status=status.HTTP_404_NOT_FOUND
        )


@api_view(["POST"])
def change_phonenumber(request):
    user = request.user
    new_phone = request.data.get("phoneNumber")
    password = request.data.get("password")
    if not user.check_password(password):
        return Response(
            {"error": "Invalid password"}, status=status.HTTP_400_BAD_REQUEST
        )
    user.phone = new_phone
    user.save()
    return Response(
        {"message": "Phone number changed successfully"}, status=status.HTTP_200_OK
    )


def change_email(request):
    user = request.user
    new_email = request.data.get("new_email")
    password = request.data.get("password")
    if not user.check_password(password):
        return Response(
            {"error": "Invalid password"}, status=status.HTTP_400_BAD_REQUEST
        )
    user.email = new_email
    user.save()
    return Response(
        {"message": "Email changed successfully"}, status=status.HTTP_200_OK
    )


@api_view(["POST"])
def change_mpin(request):
    user = request.user
    new_mpin = request.data.get("new_mpin")
    password = request.data.get("password")
    if not user.check_password(password):
        return Response(
            {"error": "Invalid password"}, status=status.HTTP_400_BAD_REQUEST
        )
    user.mpin = new_mpin
    user.save()
    return Response({"message": "MPIN changed successfully"}, status=status.HTTP_200_OK)


@api_view(["GET", "POST"])
@permission_classes([IsAuthenticated])
def edit_stats(request, match, tournament):
    points = {
        1: 12,
        2: 9,
        3: 8,
        4: 7,
        5: 6,
        6: 5,
        7: 4,
        8: 3,
        9: 2,
        10: 1,
        11: 0,
        12: 0,
    }

    if request.method == "GET":
        match_number = match
        tournament = Tournament.objects.get(pk=tournament)
        aggregate_stats = {}
        for i in range(1, match_number + 1):
            match = Match.objects.get(tournament=tournament, match_number=i)
            team_stats = TeamStat.objects.filter(
                tournament=tournament, match_number=match
            )
            for team_stat in team_stats:
                aggregate_stats[team_stat.team.team_name] = {}
                aggregate_stats[team_stat.team.team_name]["booyah"] = (
                    aggregate_stats[team_stat.team.team_name].get("booyah", 0)
                    + team_stat.booyah
                )
                aggregate_stats[team_stat.team.team_name]["position_points"] = (
                    aggregate_stats[team_stat.team.team_name].get("position_points", 0)
                    + points[team_stat.position_points]
                )
                aggregate_stats[team_stat.team.team_name]["player_1"] = (
                    aggregate_stats[team_stat.team.team_name].get("player_1", 0)
                    + team_stat.player_1
                )
                aggregate_stats[team_stat.team.team_name]["player_2"] = (
                    aggregate_stats[team_stat.team.team_name].get("player_2", 0)
                    + team_stat.player_2
                )
                aggregate_stats[team_stat.team.team_name]["player_3"] = (
                    aggregate_stats[team_stat.team.team_name].get("player_3", 0)
                    + team_stat.player_3
                )
                aggregate_stats[team_stat.team.team_name]["player_4"] = (
                    aggregate_stats[team_stat.team.team_name].get("player_4", 0)
                    + team_stat.player_4
                )
                aggregate_stats[team_stat.team.team_name]["matches_played"] = (
                    aggregate_stats[team_stat.team.team_name].get("matches_played", 0)
                    + team_stat.matches_played
                )
                aggregate_stats[team_stat.team.team_name]["kills"] = (
                    aggregate_stats[team_stat.team.team_name].get("kills", 0)
                    + aggregate_stats[team_stat.team.team_name]["player_1"]
                    + aggregate_stats[team_stat.team.team_name]["player_2"]
                    + aggregate_stats[team_stat.team.team_name]["player_3"]
                    + aggregate_stats[team_stat.team.team_name]["player_4"]
                )
        return Response(aggregate_stats, status=status.HTTP_200_OK)

    if request.method == "POST":
        if not request.user.groups.filter(name="CustomStaff").exists():
            return Response({"message": "Failure"}, status=status.HTTP_400_BAD_REQUEST)

        tournament = Tournament.objects.get(pk=tournament)
        match = Match.objects.get(pk=match)
        for team_data in request.data["teams"]:
            team = TeamDetail.objects.get(pk=team_data["teamId"])
            team_stat = TeamStat.objects.get_or_create(
                team=team, tournament=tournament, match_number=match
            )
            team_stat = team_stat[0]
            team_stat.player_1 = team_data["player_1"]
            team_stat.player_2 = team_data["player_2"]
            team_stat.player_3 = team_data["player_3"]
            team_stat.player_4 = team_data["player_4"]
            team_stat.position_points = int(team_data["position_points"])
            team_stat.booyah = 1 if team_data["booyah"] else 0
            team_stat.matches_played = 1 if team_data["matches_played"] else 0
            team_stat.save()
        return Response({"message": "Success"}, status=status.HTTP_200_OK)


@api_view(["GET"])
@permission_classes([IsAuthenticated, CustomStaffPermission])
def is_staff(request):
    return Response({"message": "Success"}, status=status.HTTP_200_OK)