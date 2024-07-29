from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse,HttpResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Expense, Participant
from user.models import User
import json
from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction
from django.urls import reverse
import csv
import requests

BASE_URL = 'http://localhost:8000'

@csrf_exempt
def add_expense(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            description = data.get('description')
            amount = data.get('amount')
            currency = data.get('currency')
            date = data.get('date')
            payer_id = data.get('payer_id')
            payment_type = data.get('payment_type')
            participants_data = data.get('participants')

            if not all([description, amount, currency, date, payer_id, payment_type, participants_data]):
                return JsonResponse({'error': 'All fields are required'}, status=400)

            try:
                payer=get_object_or_404(User, id=int(payer_id))
            except ObjectDoesNotExist:
                return JsonResponse({'error': 'Payer does not exist'}, status=404)

            total_amount = float(amount)
            exact_sum = 0
            percentage_sum = 0

            for participant_data in participants_data:
                if payment_type == "exact":
                    exact_sum += float(participant_data['amount']) 
                elif payment_type == "percentage":
                    percentage_sum += float(participant_data['amount'])

            if payment_type == "exact" and exact_sum != total_amount: # Check whether individual sums amount to total sum
                return JsonResponse({'error': 'Exact amounts do not sum up to the total expense amount'}, status=400)
            elif payment_type == "percentage" and percentage_sum != 100: # Check whether all percentages sum to 100
                return JsonResponse({'error': 'Percentages do not sum up to 100%'}, status=400)

            with transaction.atomic():
                expense = Expense.objects.create(
                    description=description,
                    amount=total_amount,
                    currency=currency,
                    date=date,
                    payer=payer,
                    payment_type=payment_type
                )

                for participant_data in participants_data:
                    user = User.objects.get(id=participant_data['user_id'])
                    if payment_type == "percentage":
                        participant_amount = (float(participant_data['amount']) / 100) * total_amount
                    else:
                        participant_amount = float(participant_data['amount'])
                    
                    Participant.objects.create(expense=expense, user=user, amount=participant_amount)

            return JsonResponse({'message': 'Expense created successfully'}, status=201)

        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
        except ObjectDoesNotExist as e:
            return JsonResponse({'error': str(e)}, status=404)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'Invalid request method'}, status=405)

@csrf_exempt
def get_individual_expenses(request, user_id):
    try:
        user = get_object_or_404(User, id=user_id)

        participant_entries = Participant.objects.filter(user=user).exclude(expense__payer=user)
        payer_entries = Expense.objects.filter(payer=user)

        user_expenses = []

        total_owed = 0
        total_paid = 0

        for entry in participant_entries:
            expense = entry.expense
            total_owed += entry.amount #Money is owed if user is a participant in an expense
            user_expenses.append({
                'expense_id': expense.id,
                'description': expense.description,
                'amount': expense.amount,
                'currency': expense.currency,
                'date': expense.date,
                'payer': expense.payer.name,
                'payment_type': expense.payment_type,
                'amount_owed': entry.amount
            })

        for expense in payer_entries:
            total_paid += expense.amount # Money is paid if user is the payer of expense
            user_expenses.append({
                'expense_id': expense.id,
                'description': expense.description,
                'amount': expense.amount,
                'currency': expense.currency,
                'date': expense.date,
                'payer': user.name,
                'payment_type': expense.payment_type,
                'amount_paid': expense.amount
            })

        net_owed = total_paid - total_owed

        return JsonResponse({
            'expenses': user_expenses,
            'total_owed': total_owed,
            'total_paid': total_paid,
            'net_owed': net_owed
        }, status=200, safe=False)

    except User.DoesNotExist:
        return JsonResponse({'error': 'User not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt
def get_overall_expenses(request):
    try:
        expenses = Expense.objects.all()

        overall_expenses = []

        for expense in expenses:
            participants = Participant.objects.filter(expense=expense)
            participant_details = []

            for participant in participants:  # Find details of all participants in an expense
                participant_details.append({
                    'user_id': participant.user.id,
                    'username': participant.user.name,
                    'amount': participant.amount
                })

            overall_expenses.append({         # Add expense details as well as participant details
                'expense_id': expense.id,
                'description': expense.description,
                'amount': expense.amount,
                'currency': expense.currency,
                'date': expense.date,
                'payer': expense.payer.name,
                'payment_type': expense.payment_type,
                'participants': participant_details
            })

        return JsonResponse({
            'overall_expenses': overall_expenses,
        }, status=200, safe=False)

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt
def balance_sheet(request, user_id=None):
    if request.method == 'GET':
        try:
            if user_id:
                individual_expenses_url = reverse('get_individual_expenses', args=[user_id])
                individual_expenses_response = requests.get(f"{BASE_URL}{individual_expenses_url}") # Call Individual Expense
                individual_expenses_response.raise_for_status()
                individual_expenses = individual_expenses_response.json()
            else:
                individual_expenses = {'expenses': []}

            overall_expenses_url = reverse('get_overall_expenses')
            overall_expenses_response = requests.get(f"{BASE_URL}{overall_expenses_url}") # Call Overall Expense
            overall_expenses_response.raise_for_status()
            overall_expenses = overall_expenses_response.json()

            response = HttpResponse(content_type='text/csv')
            response['Content-Disposition'] = 'attachment; filename="balance_sheet.csv"'

            writer = csv.writer(response)
            #Headings of CSV File
            writer.writerow([
                'Type', 'Expense ID', 'Description', 'Amount', 'Currency', 'Date',
                'Payer Name', 'Payment Type', 'Amount Owed', 'Amount Paid'
            ])

            if user_id:
                #Individual expenses
                for expense in individual_expenses['expenses']:
                    amount_owed = expense.get('amount_owed', 0)
                    amount_paid = expense.get('amount_paid', 0)
                    writer.writerow([
                        'Individual',
                        expense['expense_id'],
                        expense['description'],
                        expense['amount'],
                        expense['currency'],
                        expense['date'],
                        expense['payer'],
                        expense['payment_type'],
                        amount_owed,
                        amount_paid
                    ])
                #Overall Expenses
                writer.writerow([
                'Type', 'Expense ID', 'Description', 'Amount', 'Currency', 'Date',
                'Payer Name', 'Payment Type', 'ParticipantId' ,'ParticipantName' ,'Amount' 
            ])
                for expense in overall_expenses['overall_expenses']:
                    for participant in expense['participants']:
                        writer.writerow([
                            'Overall',
                            expense['expense_id'],
                            expense['description'],
                            expense['amount'],
                            expense['currency'],
                            expense['date'],
                            expense['payer'],
                            expense['payment_type'],
                            participant['user_id'],
                            participant['username'],
                            participant['amount']
                        ])

            return response

        except requests.exceptions.RequestException as e:
            return JsonResponse({'error': f'Error fetching data: {str(e)}'}, status=500)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'Invalid request method'}, status=405)
