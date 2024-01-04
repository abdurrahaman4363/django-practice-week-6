from typing import Any
from django.db.models.query import QuerySet
from django.forms.models import BaseModelForm
from django.http import HttpResponse
from django.shortcuts import render
from django.views.generic import CreateView, ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Transaction
from .forms import DepositForm, WithdrawForm, LoanRequestForm, TransferForm
from .constants import DEPOSITE, WITHDRAWAL, LOAN, LOAN_PAID
from django.contrib import messages
from django.http import HttpResponse
from datetime import datetime
from django.db.models import Sum
from django.shortcuts import get_object_or_404, redirect
from django.views import View
from django.urls import reverse_lazy
from django.db.models import Q

# Create your views here.


# ai view ta ky inherite kory depsoite, withdraw, loan deposite er kaj korbo
class TransactionCreateMixin(LoginRequiredMixin, CreateView):
    template_name = "transaction/transaction_form.html"
    model = Transaction
    title = ""
    success_url = reverse_lazy("transaction_report")

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update(
            {
                "account": self.request.user.account,
            }
        )
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        context.update(
            {
                "title": self.title,
            }
        )
        return context


class DepsoiteMoneyView(TransactionCreateMixin):
    form_class = DepositForm
    title = "Deposit"

    def get_initial(self):
        initial = {"transaction_type": DEPOSITE}
        return initial

    def form_valid(self, form):
        amount = form.cleaned_data.get("amount")
        account = self.request.user.account
        account.balance += amount
        account.save(update_fields=["balance"])

        messages.success(
            self.request, f"{amount}$ was deposited to your account successfully"
        )
        return super().form_valid(form)


class WithdrawMoneyView(TransactionCreateMixin):
    form_class = WithdrawForm
    title = "Withdraw Money"

    def get_initial(self):
        initial = {"transaction_type": WITHDRAWAL}
        return initial

    def form_valid(self, form):
        amount = form.cleaned_data.get("amount")
        account = self.request.user.account

        if amount > account.balance:
            # Check for bankruptcy
            total_balance = self.request.user.account.objects.aggregate(Sum("balance"))[
                "balance__sum"
            ]
            if amount > total_balance:
                return HttpResponse("The bank is bankrupt")

        account.balance -= amount
        account.save(update_fields=["balance"])

        messages.success(
            self.request, f"{amount}$ was withdrawn from your account successfully"
        )
        return super().form_valid(form)


class LoanRequestView(TransactionCreateMixin):
    form_class = LoanRequestForm
    title = "Request For Loan"

    def get_initial(self):
        initial = {"transaction_type": LOAN}
        return initial

    def form_valid(self, form):
        amount = form.cleaned_data.get("amount")
        current_loan_count = Transaction.objects.filter(
            account=self.request.user.account, transaction_type=LOAN, loan_approve=True
        ).count()

        if current_loan_count >= 3:
            return HttpResponse("You have crossed your limits")

        messages.success(
            self.request,
            f"Loan request for amount {amount}$ has been successfully sent to admin",
        )
        return super().form_valid(form)


class TransactionReportView(LoginRequiredMixin, ListView):
    template_name = "transaction/transaction_report.html"
    model = Transaction
    balance = 0  # filter korar pore ba age amar total balance ke show korbe
    context_object_name = "report_list"

    def get_queryset(self):
        user_account = self.request.user.account
        queryset = super().get_queryset().filter(account=user_account)

        start_date_str = self.request.GET.get("start_date")
        end_date_str = self.request.GET.get("end_date")

        if start_date_str and end_date_str:
            start_date = datetime.strptime(start_date_str, "%Y-%m-%d").date()
            end_date = datetime.strptime(end_date_str, "%Y-%m-%d").date()

            queryset = queryset.filter(
                timestamp__date__gte=start_date, timestamp__date__lte=end_date
            )
            self.balance = Transaction.objects.filter(
                Q(account=user_account) | Q(to_account=user_account),
                timestamp__date__gte=start_date,
                timestamp__date__lte=end_date,
            ).aggregate(Sum("amount"))["amount__sum"]
        else:
            self.balance = user_account.balance

        return queryset.distinct()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({"account": self.request.user.account})

        return context


class PayLoanView(LoginRequiredMixin, View):
    def get(self, request, loan_id):
        loan = get_object_or_404(Transaction, id=loan_id)

        if loan.loan_approve:
            user_account = loan.account
            if loan.amount < user_account.balance:
                user_account.balance -= loan.amount
                loan.balance_after_transaction = user_account.balance
                user_account.save()
                loan.transaction_type = LOAN_PAID
                loan.save()
                return redirect("loan_list")

            else:
                messages.error(
                    self.request, f"Loan amount is greater than available balance"
                )
                return redirect("loan_list")


class LoanListView(LoginRequiredMixin, ListView):
    model = Transaction
    template_name = "transaction/loan_request.html"
    context_object_name = "loans"

    def get_queryset(self):
        user_account = self.request.user.account
        querset = Transaction.objects.filter(
            account=user_account, transaction_type=LOAN
        )
        return querset


class TransferMoneyView(TransactionCreateMixin):
    form_class = TransferForm
    title = "Transfer Money"

    def get_initial(self):
        initial = {"transaction_type": WITHDRAWAL}
        return initial

    def form_valid(self, form):
        amount = form.cleaned_data.get("amount")
        to_account = form.cleaned_data.get("to_account")

        if not to_account:
            return HttpResponse("Recipient's account not found")

        sender_account = self.request.user.account
        if amount > sender_account.balance:
            return HttpResponse("Insufficient funds for transfer")

        sender_account.transfer_amount(to_account, amount)

        messages.success(
            self.request,
            f"{amount}$ was transferred to {to_account.user.username}'s account successfully",
        )
        return super().form_valid(form)
