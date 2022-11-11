from django.shortcuts import render, redirect

from api.models import User, SelfReport


def handle_index(request):
	if request.user.is_superuser:
		participants = []
		for participant in User.objects.all():
			participants += [{
				'id': participant.id,
				'name': participant.full_name if participant.full_name else 'N/A',
				'fcm_token': participant.fcm_token,
				'ema_amount': SelfReport.objects.filter(participant=participant).count()
			}]
		participants.sort(key=lambda x: x['id'])
		return render(request=request, template_name='index.html', context={
			'title': 'Stress with smartwatches',
			'participants': participants
		})
	else:
		return redirect('/admin/')
