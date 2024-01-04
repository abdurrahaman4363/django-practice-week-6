from django.db import models
from django.contrib.auth.models import User
from .constants import ACCOUNT_TYPE, GENDER_TYPE

# Create your models here.
# django amader build in user make korar fecilities deii...


class UserBankAccount(models.Model):
    user = models.OneToOneField(
        User, related_name="account", on_delete=models.CASCADE
    )  # ak ta user information ak ber e nibo
    account_type = models.CharField(max_length=10, choices=ACCOUNT_TYPE)
    account_no = models.IntegerField(
        unique=True
    )  # account no dui jon er kkn o same hoty parby na
    birth_date = models.DateField(null=True, blank=True)
    gender = models.CharField(max_length=10, choices=GENDER_TYPE)
    initial_deposite_date = models.DateField(auto_now_add=True)
    balance = models.DecimalField(
        default=0, max_digits=12, decimal_places=2
    )  # ak jon user 12 digit obdhi taka rakhty parby , dui dhoshomik ghor obdhi rakty parby

    def __str__(self):
        return str(self.account_no)

    # def transfer_amount(self, to_account, amount):
    #     if amount > self.balance:
    #         raise ValueError("Insufficient funds for transfer")

    #     self.balance -= amount
    #     self.save()

    #     to_account.balance += amount
    #     to_account.save()

    #     # Create transactions for both accounts
    #     Transaction.objects.create(
    #         account=self,
    #         amount=-amount,
    #         balance_after_transaction=self.balance,
    #         transaction_type=WITHDRAWAL  # You may need to import WITHDRAWAL constant
    #     )

    #     Transaction.objects.create(
    #         account=to_account,
    #         amount=amount,
    #         balance_after_transaction=to_account.balance,
    #         transaction_type=DEPOSITE  # You may need to import DEPOSITE constant
    #     )


class UserAddress(models.Model):
    user = models.OneToOneField(User, related_name="address", on_delete=models.CASCADE)
    street_address = models.CharField(max_length=100)
    city = models.CharField(max_length=100)
    postal_code = models.IntegerField()
    country = models.CharField(max_length=100)

    def __str__(self):
        return self.user.email
