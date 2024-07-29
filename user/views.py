# views.py
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.hashers import make_password
from .models import User
import json

@csrf_exempt
def create_user(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            name = data.get('name')
            email = data.get('email')
            phone = data.get('phone')
            password = data.get('password')

            if not (name and email and phone and password):
                return JsonResponse({'error': 'All fields are required'}, status=400)

            if User.objects.filter(email=email).exists():
                return JsonResponse({'error': 'Email already exists'}, status=400)

            if User.objects.filter(phone=phone).exists():
                return JsonResponse({'error': 'Phone number already exists'}, status=400)

            hashed_password = make_password(password)
            user = User.objects.create(name=name, email=email, phone=phone, password=hashed_password)
            return JsonResponse({'message': 'User created successfully', 'user_id': user.id}, status=201)
        
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    return HttpResponse("Method not allowed", status=405)

def get_user(user_id):
    try:
        user = get_object_or_404(User, id=user_id)
        user_data = {
            'id': user.id,
            'name': user.name,
            'email': user.email,
            'phone': user.phone
        }
        return JsonResponse(user_data)
    except User.DoesNotExist:
        return JsonResponse({'error': 'User not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
