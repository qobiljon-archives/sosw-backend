from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib.auth import logout

from rest_framework.authtoken.models import Token

from plotly import express as px
from os.path import exists
from os import environ
import pandas as pd
import plotly

from api.models import User, SelfReport
from dashboard.utils import count_file_lines


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
  users = list()

  if 'pid' in request.GET and str(request.GET['pid']).isdigit():
    pid = int(request.GET['pid'])
    if User.objects.filter(id = pid):
      users.append(User.objects.get(id = pid))
  else:
    users.extend(User.objects.filter(is_superuser = False))

  plots = list()
  filenames = [
    ('ppg', 16),
    ('acc', 3),
  ]
  for user in users:
    for filename, col_count in filenames:
      filepath = f'{environ["DATA_DUMP_DIR"]}/{user.email}/{filename}.csv'
      if not exists(filepath): continue
      lines_count = count_file_lines(filepath)

      names = ['ts'] + [chr(ord('a') + x) for x in range(col_count)]
      df = pd.read_csv(
        filepath,
        names = names,
        dtype = {x: int if x == 'ts' else float for x in names},
        skiprows = max(0, lines_count - 540_000),
      )
      df = df[['ts', 'a']]
      df = df[df.ts > df.iloc[-1].ts - 24*60*60*1000]

      df.ts = pd.to_datetime(df.ts, unit = 'ms', utc = True).map(lambda x: x.tz_convert('Asia/Seoul'))
      df.set_index('ts', drop = True, inplace = True)

      df_resampled = df.resample('60S').count().rename(columns = {'value': 'amount/minute'})
      fig = px.bar(df_resampled, title = f'{user.email}, {filename}.csv')
      fig.update_layout(xaxis_title = "Time", yaxis_title = "amount of data / minute")
      plots.append(plotly.offline.plot(
        figure_or_data = fig,
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
