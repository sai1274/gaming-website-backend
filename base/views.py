from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, get_user_model, login, logout
from django.core.mail import send_mail
from .models import CustomUser, Wallet, Transaction, TeamDetail, Tournament

# Create your views here.
def slots(request):
    rooms = Tournament.objects.all()
    context = {
        "rooms": rooms,
    }
    # Check if redirect is necessary (e.g., user clicked a "Book Slot" button)
    if request.method == "GET":
        room_id = request.GET.get("room_id")  # Assuming "room_id" is in the GET parameters
        if room_id:
            try:
                room = Tournament.objects.get(pk=int(room_id))
                if room.participants.filter(pk=request.user.pk).exists():
                    return redirect("book_slot", pk=room.pk) #Redirect to book_slot with room ID since user is registered already
                else:
                    return redirect("team-details", pk=room.pk)  # Redirect to team details with room ID
            except (Tournament.DoesNotExist, ValueError):
                # Handle potential errors (room not found, invalid ID)
                pass
    return render(request, "base/slots.html", context)

@login_required(login_url="login")
def book_slot(request,pk):
    room = Tournament.objects.get(pk=pk)
    if not room.participants.filter(pk=request.user.pk).exists():
        if room.slots_available > 0:
            room.slots_available -= 1
            room.save()
            room.participants.add(request.user)
        else:
            return render(request, "base/slot_full.html")
    context = {
        "room": room,
        "participants": room.participants.all(),
    }
    return render(request, "base/credentials.html", context)

@login_required(login_url="login")
def team_details(request,pk):
    room = Tournament.objects.get(pk=pk)
    if request.method == "POST":
        team_name = request.POST.get("team_name")
        phone_number = request.POST.get("phone")
        optional_phone_number = request.POST.get("optional")
        team = TeamDetail(team_name=team_name, team_leader=request.user, phone_number=phone_number, optional_phone_number=optional_phone_number)
        if team.save():  # Check if team is saved successfully
            if room.slots_available > 0:
                room.slots_available -= 1
                room.save()
                room.participants.add(request.user)
                return redirect("book_slot", pk=pk)  # Redirect to book_slot with room ID
            else:
                return render(request, "base/slot_full.html")  # Slot full message
        room.participant_team_name.add(team)
        return redirect("book_slot", pk=pk)
    return render(request, "base/team_details.html")

def custom_login(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request,username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect("slots")
        else:
            return render(request, "base/login.html", {"message": "Invalid Username or Password"})
    return render(request, "base/login.html")

def register(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        email = request.POST.get('email')
        phone = request.POST.get('ph-number')
        mpin = request.POST.get('mpin')
        CustomUser = get_user_model()
        user = CustomUser.objects.create_user(username=username,password=password,email=email,phone=phone,mpin=mpin)
        team_name = "Agent E-Sports"
        # message = f"Hello {user.username},\n\nYou have been successfully registered.\n\nThank you for registering with us.\n\nRegards,\nTeam {team_name}"
        # from_email = None
        # send_mail(subject="Registration", message=message, recipient_list=[email],fail_silently=True, from_email=from_email)
        user.save()
        print("User Created Successfully!")
        login(request, user)
        return redirect("slots")
    else:
        return render(request, "base/register.html")
    
@login_required(login_url="login")
def wallet(request):
    wallet = Wallet.objects.get(user=request.user)
    transactions = Transaction.objects.filter(user=request.user)

    context = {
        "user": request.user,
        "transactions": transactions,
        "wallet": wallet,
    }
    return render(request, "base/wallet.html", context)

@login_required(login_url="login")
def deposit(request):
    if request.method == "POST":
        amount = int(request.POST.get("amount"))
        transaction_id = request.POST.get("transaction_id")
        wallet = Wallet.objects.get(user=request.user)
        wallet.add_transaction(amount, transaction_id)
        return redirect("wallet")
    return render(request, "base/add_money.html")

@login_required(login_url="login")
def withdraw(request):
    if request.method == "POST":
        amount = int(request.POST.get("amount"))
        wallet = Wallet.objects.get(user=request.user)
        if wallet.balance >= amount:
            wallet.subtract_transaction(amount)
        else:
            return render(request, "base/withdraw_error.html")
        return redirect("wallet")
    return render(request, "base/withdraw_money.html")

@login_required(login_url="login")
def user_info(request):
    user = request.user
    user_data = CustomUser.objects.get(username=user)
    # Tournaments = Tournament.objects.all()
    # for room in Tournaments:
    #     print(room.participants.all())
    tournaments_participated = Tournament.objects.filter(participants__username=user)
    print("Check",tournaments_participated)
    context = {
        "user_data": user_data,
        "tournaments_participated": tournaments_participated,
    }
    return render(request, "base/user_info.html", context)

@login_required(login_url="login")
def custom_logout(request):
    logout(request)
    return redirect("login")

@login_required(login_url="login")
def change_mpin(request):
    if request.method == "POST":
        new_mpin = request.POST.get("new_mpin")
        user = request.user
        if request.user.mpin == new_mpin:
            return render(request, "base/change_mpin.html", {"message": "New MPIN cannot be same as old MPIN"})
        user.mpin = new_mpin
        user.save()
        # if request.POST.get("password") == user.password:
        #     user.mpin = new_mpin
        #     user.save()
        # else:
        #     return render(request, "base/change_mpin.html", {"message": "Invalid Password"})
        return redirect("user-info")
    return render(request, "base/change_mpin.html")
