from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib.auth import logout

from rest_framework.authtoken.models import Token

from plotly import express as px
from os import environ
import pandas as pd
import plotly

from api.models import User, SelfReport


@login_required
@user_passes_test(lambda u: u.is_superuser)
def handle_index(request):
  users = list(User.objects.filter(is_superuser = False))
  users.sort(key = lambda x: x.id)

  return render(
    request = request,
    template_name = 'index.html',
    context = dict(
      title = 'Stress with smartwatches',
      users = users,
      token = Token.objects.get(user = request.user).key,
    ),
  )


@login_required
@user_passes_test(lambda u: u.is_superuser)
def handle_dq_plot(request):
  users = list(User.objects.filter(is_superuser = False))
  plots = list()

  for user in users:
    df = pd.read_csv(
      f'{environ["DATA_DUMP_DIR"]}/{user.email}/ppg.csv',
      names = ['ts'] + [chr(ord('a') + x) for x in range(16)],
    )
    df = df[['ts', 'f']]

    df.ts = pd.to_datetime(df.ts, unit = 'ms', utc = True).map(lambda x: x.tz_convert('Asia/Seoul'))
    df.set_index('ts', drop = True, inplace = True)

    df_resampled = df.resample('60S').count()

    plots.append(
      plotly.offline.plot(
        figure_or_data = px.bar(df_resampled, title = user.email),
        auto_open = False,
        output_type = "div",
      ))

  return render(
    request = request,
    template_name = 'dq_plots.html',
    context = dict(
      title = 'DQ plots',
      plots = plots,
      token = Token.objects.get(user = request.user).key,
    ),
  )