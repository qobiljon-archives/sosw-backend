from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib.auth import logout

from rest_framework.authtoken.models import Token

from api.models import User, SelfReport


@login_required
def handle_index(request):
  if request.user.is_superuser:
    participants = []
    for participant in User.objects.all():
      participants += [
        dict(
          id = participant.id,
          name = participant.full_name if participant.full_name else 'N/A',
          fcm_token = participant.fcm_token,
          ema_amount = SelfReport.objects.filter(user = request.user).count(),
        )
      ]
    participants.sort(key = lambda x: x['id'])
    return render(
      request = request,
      template_name = 'index.html',
      context = dict(
        title = 'Stress with smartwatches',
        participants = participants,
        token = Token.objects.get(user = request.user).key,
      ),
    )
  else:
    logout(request = request)
    return redirect('/admin/')
