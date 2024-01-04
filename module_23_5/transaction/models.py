from django.db import models
from accounts.models import UserBankAccount
from .constants import TRANSACTION_TYPE

# Create your models here.


class Transaction(models.Model):
    account = models.ForeignKey(
        UserBankAccount, related_name="transaction", on_delete=models.CASCADE
    )  # akjon user er multiple transactions hoty pary
    amount = models.DecimalField(decimal_places=2, max_digits=12)
    balance_after_transaction = models.DecimalField(decimal_places=2, max_digits=12)
    transaction_type = models.IntegerField(choices=TRANSACTION_TYPE, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    loan_approve = models.BooleanField(default=False)
    # to_account = models.CharField(max_length=100)

    class Meta:
        ordering = ["timestamp"]
