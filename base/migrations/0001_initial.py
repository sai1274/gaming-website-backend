# Generated by Django 5.0.2 on 2024-03-23 17:34

import datetime
import django.contrib.auth.models
import django.contrib.auth.validators
import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("auth", "0012_alter_user_first_name_max_length"),
    ]

    operations = [
        migrations.CreateModel(
            name="CustomUser",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("password", models.CharField(max_length=128, verbose_name="password")),
                (
                    "last_login",
                    models.DateTimeField(
                        blank=True, null=True, verbose_name="last login"
                    ),
                ),
                (
                    "is_superuser",
                    models.BooleanField(
                        default=False,
                        help_text="Designates that this user has all permissions without explicitly assigning them.",
                        verbose_name="superuser status",
                    ),
                ),
                (
                    "username",
                    models.CharField(
                        error_messages={
                            "unique": "A user with that username already exists."
                        },
                        help_text="Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.",
                        max_length=150,
                        unique=True,
                        validators=[
                            django.contrib.auth.validators.UnicodeUsernameValidator()
                        ],
                        verbose_name="username",
                    ),
                ),
                (
                    "first_name",
                    models.CharField(
                        blank=True, max_length=150, verbose_name="first name"
                    ),
                ),
                (
                    "last_name",
                    models.CharField(
                        blank=True, max_length=150, verbose_name="last name"
                    ),
                ),
                (
                    "email",
                    models.EmailField(
                        blank=True, max_length=254, verbose_name="email address"
                    ),
                ),
                (
                    "is_staff",
                    models.BooleanField(
                        default=False,
                        help_text="Designates whether the user can log into this admin site.",
                        verbose_name="staff status",
                    ),
                ),
                (
                    "is_active",
                    models.BooleanField(
                        default=True,
                        help_text="Designates whether this user should be treated as active. Unselect this instead of deleting accounts.",
                        verbose_name="active",
                    ),
                ),
                (
                    "date_joined",
                    models.DateTimeField(
                        default=django.utils.timezone.now, verbose_name="date joined"
                    ),
                ),
                (
                    "phone",
                    models.CharField(default="1234567890", max_length=10, unique=True),
                ),
                ("mpin", models.CharField(default="00000", max_length=5)),
                ("state", models.CharField(default="Andhra Pradesh", max_length=100)),
                (
                    "groups",
                    models.ManyToManyField(
                        blank=True,
                        help_text="The groups this user belongs to. A user will get all permissions granted to each of their groups.",
                        related_name="user_set",
                        related_query_name="user",
                        to="auth.group",
                        verbose_name="groups",
                    ),
                ),
                (
                    "user_permissions",
                    models.ManyToManyField(
                        blank=True,
                        help_text="Specific permissions for this user.",
                        related_name="user_set",
                        related_query_name="user",
                        to="auth.permission",
                        verbose_name="user permissions",
                    ),
                ),
            ],
            options={
                "verbose_name": "user",
                "verbose_name_plural": "users",
                "abstract": False,
            },
            managers=[
                ("objects", django.contrib.auth.models.UserManager()),
            ],
        ),
        migrations.CreateModel(
            name="UTRID",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("utr_id", models.CharField(max_length=255)),
                ("timestamp", models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name="Wallet",
            fields=[
                (
                    "user",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        primary_key=True,
                        serialize=False,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "balance",
                    models.DecimalField(decimal_places=0, default=0, max_digits=10),
                ),
            ],
        ),
        migrations.CreateModel(
            name="TeamDetail",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("team_name", models.CharField(default="Team Name", max_length=100)),
                (
                    "in_game_name",
                    models.CharField(default="In Game Name", max_length=100),
                ),
                ("phone_number", models.CharField(default="1234567890", max_length=10)),
                (
                    "optional_phone_number",
                    models.CharField(
                        blank=True, default="1234567890", max_length=10, null=True
                    ),
                ),
                (
                    "team_leader",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="Tournament",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "tournament_name",
                    models.CharField(default="Tournament Name", max_length=100),
                ),
                ("slots_available", models.PositiveIntegerField(default=12)),
                ("slots_total", models.PositiveIntegerField(default=12)),
                (
                    "room_id",
                    models.CharField(
                        default="Your Room ID will appear 5 mins before the tournament starts",
                        max_length=100,
                    ),
                ),
                (
                    "room_password",
                    models.CharField(
                        default="Your Room Password will appear 5 mins before the tournament starts",
                        max_length=100,
                    ),
                ),
                (
                    "entry_fee",
                    models.DecimalField(decimal_places=0, default=0, max_digits=5),
                ),
                (
                    "prize_pool",
                    models.DecimalField(decimal_places=0, default=0, max_digits=10),
                ),
                (
                    "First_prize",
                    models.DecimalField(decimal_places=0, default=0, max_digits=10),
                ),
                (
                    "Second_prize",
                    models.DecimalField(decimal_places=0, default=0, max_digits=10),
                ),
                (
                    "Third_prize",
                    models.DecimalField(decimal_places=0, default=0, max_digits=10),
                ),
                (
                    "Fourth_prize",
                    models.DecimalField(decimal_places=0, default=0, max_digits=10),
                ),
                (
                    "registration_time",
                    models.DateTimeField(
                        default=datetime.datetime(
                            2024,
                            3,
                            23,
                            17,
                            34,
                            50,
                            922635,
                            tzinfo=datetime.timezone.utc,
                        )
                    ),
                ),
                (
                    "tournament_time",
                    models.DateTimeField(
                        default=datetime.datetime(
                            2024,
                            3,
                            23,
                            17,
                            34,
                            50,
                            922852,
                            tzinfo=datetime.timezone.utc,
                        )
                    ),
                ),
                (
                    "participant_team_name",
                    models.ManyToManyField(
                        blank=True,
                        related_name="participant_team_name",
                        to="base.teamdetail",
                    ),
                ),
                (
                    "participants",
                    models.ManyToManyField(
                        blank=True,
                        related_name="participants",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="Match",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("match_number", models.CharField(default="1", max_length=100)),
                (
                    "tournament",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="base.tournament",
                    ),
                ),
            ],
            options={
                "unique_together": {("tournament", "match_number")},
            },
        ),
        migrations.CreateModel(
            name="Transaction",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("amount", models.DecimalField(decimal_places=0, max_digits=10)),
                ("description", models.CharField(max_length=255)),
                ("timestamp", models.DateTimeField(auto_now_add=True)),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("Pending", "Pending"),
                            ("Rejected", "Rejected"),
                            ("Approved", "Approved"),
                        ],
                        default="Pending",
                        max_length=10,
                    ),
                ),
                ("transaction_details", models.CharField(blank=True, max_length=255)),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "utr_id",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        to="base.utrid",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="TeamStat",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("player_1", models.IntegerField(default=0)),
                ("player_2", models.IntegerField(default=0)),
                ("player_3", models.IntegerField(default=0)),
                ("player_4", models.IntegerField(default=0)),
                ("position_points", models.PositiveIntegerField(default=0)),
                ("booyah", models.PositiveIntegerField(default=0)),
                ("matches_played", models.PositiveIntegerField(default=0)),
                (
                    "match_number",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="base.match"
                    ),
                ),
                (
                    "team",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="base.teamdetail",
                    ),
                ),
                (
                    "tournament",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="base.tournament",
                    ),
                ),
            ],
            options={
                "unique_together": {("team", "tournament", "match_number")},
            },
        ),
    ]
