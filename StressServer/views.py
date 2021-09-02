from django.shortcuts import render, redirect

from api.models import Participant


def handle_index(request):
    if request.user.is_superuser:
        return render(request=request, template_name='index.html', context={
            'title': 'Stress with smartwatches',
            'participants': Participant.objects.all()
        })
    else:
        return redirect('/admin/')
