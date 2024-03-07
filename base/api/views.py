from .serializers import UserSerializer, WalletSerializer, TransactionSerializer, TournamentSerializer, TeamDetailSerializer, MatchesSerializer
from rest_framework.decorators import api_view, permission_classes
from base.models import CustomUser, Wallet, Transaction, Tournament, TeamDetail, Matches
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework import status
from rest_framework.authtoken.models import Token
from django.core.mail import send_mail
from django.contrib.auth import login, logout, get_user_model, authenticate
from django.shortcuts import redirect
from rest_framework.renderers import JSONRenderer

@api_view(['GET'])
@permission_classes([AllowAny])
def tournaments(request):
    if request.method == 'GET':
        tournaments = Tournament.objects.all()
        serializer = TournamentSerializer(tournaments, many=True)
        return Response(serializer.data)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_team(request):
    serializer = TeamDetailSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET','POST'])
@permission_classes([IsAuthenticated])
def users(request):
    if request.method == 'GET':
        users = CustomUser.objects.all()
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data)
    elif request.method == 'POST':
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def book_slot(request, pk):
    try:
        tournament = Tournament.objects.get(pk=pk)
    except Tournament.DoesNotExist:
        return Response({"error": "Tournament not found"}, status=status.HTTP_404_NOT_FOUND)

    user_wallet = Wallet.objects.get(user=request.user)
    if user_wallet.balance < tournament.entry_fee:
        return Response({"error": "Insufficient balance"}, status=status.HTTP_400_BAD_REQUEST)

    if tournament.slots_available < 1:
        return Response({"error": "No slots available"}, status=status.HTTP_400_BAD_REQUEST)

    if request.user in tournament.participants.all():
        serializer = TournamentSerializer(tournament)
        return Response({"message": "Slot already booked", "tournament": serializer.data}, status=status.HTTP_200_OK)

    tournament.slots_available -= 1
    tournament.participants.add(request.user)
    user_wallet.balance -= tournament.entry_fee
    user_wallet.save()

    # Allow subsequent team association (assuming team_id is provided in request):
    if request.method == 'POST' and 'team_id' in request.POST:  # Check for POST method and team_id
        try:
            team = TeamDetail.objects.get(pk=request.POST['team_id'])
            tournament.participant_team_name.add(team)
        except (KeyError, TeamDetail.DoesNotExist):
            return Response({'error': 'Invalid or non-existent team details provided'}, status=status.HTTP_400_BAD_REQUEST)

    tournament.save()
    serializer = TournamentSerializer(tournament)
    return Response({"message": "Slot booked successfully", "tournament": serializer.data}, status=status.HTTP_200_OK)


@api_view(['POST','GET'])
@permission_classes([AllowAny])
def custom_login(request):
    username = request.data.get('username')
    password = request.data.get('password')
    user = authenticate(request,username=username, password=password)
    if user is not None:
            login(request, user)
            return redirect("slots")
    return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)

@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):
    data = request.data
    username = data.get('username')
    password = data.get('password')
    email = data.get('email')
    phone = data.get('phoneNumber')
    mpin = data.get('mpin')

    if not all([username, password, email, phone, mpin]):
        return Response({'error': 'All fields are required'}, status=status.HTTP_400_BAD_REQUEST)

    CustomUser = get_user_model()
    try:
        user = CustomUser.objects.create_user(
            username=username, password=password, email=email, phone=phone, mpin=mpin
        )
        # send_registration_email(user)  # Call the mail sending function
        print("Registration email sent")
        login(request, user)
        return Response({'message': 'Registration successful'}, status=status.HTTP_201_CREATED)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

def send_registration_email(user):
    team_name = "Agent E-Sports"
    message = f"Hello {user.username},\n\nYou have been successfully registered.\n\nThank you for registering with us.\n\nRegards,\nTeam {team_name}"
    subject = "Registration"
    recipient_list = [user.email]
    from_email = None  # Set your email address here
    send_mail(subject, message, from_email, recipient_list, fail_silently=False)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def wallet(request):
    wallet = Wallet.objects.get(user=request.user)
    serializer = WalletSerializer(wallet)
    return Response(serializer.data)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def deposit(request):
    amount = int(request.data.get("amount"))
    transaction_id = request.data.get("transaction_id")
    wallet = Wallet.objects.get(user=request.user)
    wallet.add_transaction(amount, transaction_id)
    serializer = WalletSerializer(wallet)
    return Response(serializer.data)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def withdraw(request):
    amount = int(request.data.get("amount"))
    wallet = Wallet.objects.get(user=request.user)
    wallet.subtract_transaction(amount)
    serializer = WalletSerializer(wallet)
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def custom_logout(request):
    logout(request)
    return Response({'message': 'Logout successful'}, status=status.HTTP_200_OK)

@api_view(['GET'])
def user_info(request):
    user = request.user
    user_data = CustomUser.objects.get(username=user)
    tournaments_participated = Tournament.objects.filter(participants__username=user)

    serializer_context = {'request': request}  # Include request for potential contextual information
    user_serializer = UserSerializer(user_data, context=serializer_context)
    tournaments_serializer = TournamentSerializer(tournaments_participated, many=True, context=serializer_context)

    data = {
        'user_data': user_serializer.data,
        'tournaments_participated': tournaments_serializer.data
    }

    return Response(data, status=status.HTTP_200_OK)

@api_view(['GET'])
def match_details(request, pk):
  try:
    tournament = Tournament.objects.get(pk=pk)
    matches = tournament.matches_set.all()  # Retrieve related matches

    serializer = TournamentSerializer(tournament)
    matches_serializer = MatchesSerializer(matches, many=True)  # Serialize multiple matches

    return Response({
      'data': serializer.data,
      'matches': matches_serializer.data,  # Use serialized match data
      'all_matches': MatchesSerializer(Matches.objects.all(), many=True).data  # Serialize all matches separately
    }, status=status.HTTP_200_OK)

  except Tournament.DoesNotExist:
    return Response({"error": "Tournament not found"}, status=status.HTTP_404_NOT_FOUND)