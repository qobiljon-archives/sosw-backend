from django.shortcuts import render, redirect

from api.models import Participant, EMAData
from api.models import SensingDataCount


def handle_index(request):
    if request.user.is_superuser:
        participants = []
        for participant in Participant.objects.all():
            if not SensingDataCount.objects.filter(participant=participant).exists():
                SensingDataCount.objects.create(participant=participant)
            participants += [{
                'id': participant.id,
                'name': participant.name if participant.name else 'N/A',
                'fcm_token': participant.fcm_token,
                'sensing_amount': SensingDataCount.objects.get(participant=participant).count,
                'ema_amount': EMAData.objects.filter(participant=participant).count()
            }]
        return render(request=request, template_name='index.html', context={
            'title': 'Stress with smartwatches',
            'participants': participants
        })
    else:
        return redirect('/admin/')
