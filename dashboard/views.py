from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib.auth import logout

from rest_framework.authtoken.models import Token

from api.models import User, SelfReport


@login_required
def handle_index(request):
  if request.user.is_superuser:
    users = list()
    for user in User.objects.filter(is_superuser = False):
      users.append(dict(
        id = user.id,
        name = user.full_name if user.full_name else 'N/A',
        fcm_token = user.fcm_token,
        ema_amount = SelfReport.objects.filter(user = request.user).count(),
      ))
    users.sort(key = lambda x: x['id'])
    return render(
      request = request,
      template_name = 'index.html',
      context = dict(
        title = 'Stress with smartwatches',
        users = users,
        token = Token.objects.get(user = request.user).key,
      ),
    )
  else:
    logout(request = request)
    return redirect('/admin/')
