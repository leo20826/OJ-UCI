import csv
import secrets

from django.conf import settings
from django.contrib.auth.models import User
from django.core.management.base import BaseCommand

from judge.models import Language, Profile

ALPHABET = 'abcdefghkqtxyz' + 'abcdefghkqtxyz'.upper() + '23456789'


def generate_password():
    return "".join(secrets.choice(ALPHABET) for _ in range(8))


def add_user(username, fullname, password):
    usr = User(username=username, first_name=fullname, is_active=True)
    usr.set_password(password)
    usr.save()

    profile = Profile(user=usr)
    profile.language = Language.objects.get(key=settings.DEFAULT_USER_LANGUAGE)
    profile.save()


class Command(BaseCommand):
    help = "batch create users"

    def add_arguments(self, parser):
        parser.add_argument(
            "input", help="csv file containing id (if any), username and fullname"
        )
        parser.add_argument("output", help="where to store output csv file")

    def handle(self, *args, **options):
        with open(options["input"], "r") as fin, open(
            options["output"], "w", newline=""
        ) as fout:
            reader = csv.DictReader(fin)

            # Data validation
            if not reader.fieldnames:
                self.stderr.write(
                    self.style.ERROR("Input CSV file is empty or has no header.")
                )
                return

            if (
                "username" not in reader.fieldnames
                or "fullname" not in reader.fieldnames
            ):
                self.stderr.write(
                    self.style.ERROR(
                        "Input CSV file must contain 'username' and 'fullname' fields."
                    )
                )
                return

            hasId = "id" in reader.fieldnames

            if hasId:
                writer = csv.DictWriter(
                    fout, fieldnames=["id", "username", "fullname", "password"]
                )
            else:
                writer = csv.DictWriter(
                    fout, fieldnames=["username", "fullname", "password"]
                )
            writer.writeheader()

            for row in reader:
                if hasId:
                    row["id"] = row["id"].strip()
                    _id = row["id"]
                username = row["username"]
                fullname = row["fullname"]
                password = generate_password()

                try:
                    add_user(username, fullname, password)
                except Exception as e:
                    self.stderr.write(
                        self.style.ERROR(
                            f"Error adding user {username}: {e}. Skipping this user."
                        )
                    )
                    continue

                if hasId:
                    writer.writerow(
                        {
                            "id": _id,
                            "username": username,
                            "fullname": fullname,
                            "password": password,
                        }
                    )
                else:
                    writer.writerow(
                        {
                            "username": username,
                            "fullname": fullname,
                            "password": password,
                        }
                    )
