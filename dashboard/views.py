from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from rest_framework.authtoken.models import Token

from os.path import exists
from os import environ

from api import selectors as slc
from plotly.subplots import make_subplots
import plotly.graph_objects as go
from datetime import datetime as dt
from datetime import timedelta as td
from dateutil import tz
import plotly
from collections import defaultdict
from bisect import bisect_left as bleft
from bisect import bisect_right as bright


@login_required
@user_passes_test(lambda u: u.is_superuser)
def handle_index(request):
  return render(
    request = request,
    template_name = 'index.html',
    context = dict(
      title = '',
      users = sorted(slc.get_users(), key = lambda x: x.id),
      token = Token.objects.get(user = request.user).key,
    ),
  )


@login_required
@user_passes_test(lambda u: u.is_superuser)
def handle_dq_plot(request):
  users = list()
  if 'pid' in request.GET and slc.user_exists(id = request.GET['pid']):
    user = slc.get_user(id = int(request.GET['pid']))
    if user: users.append(user)
  else:
    users.extend(slc.get_users())

  def add_smartphone_dq_plots(fig, user, timestamps, delta):
    ema_counts = list()
    location_counts = list()
    screenstate_counts = list()
    callog_counts = list()
    activitytransition_counts = list()
    activityrecognition_counts = list()
    calendarevent_counts = list()

    for d in timestamps:
      from_ts, till_ts = int(d.timestamp()*1000), int((d + delta).timestamp()*1000)
      ema_counts.append(slc.get_ema_count(user, from_ts, till_ts))
      location_counts.append(slc.get_location_count(user, from_ts, till_ts))
      screenstate_counts.append(slc.get_screenstate_count(user, from_ts, till_ts))
      callog_counts.append(slc.get_calllog_count(user, from_ts, till_ts))
      activitytransition_counts.append(slc.get_activitytransition_count(user, from_ts, till_ts))
      activityrecognition_counts.append(slc.get_activityrecognitions_count(user, from_ts, till_ts))
      calendarevent_counts.append(slc.get_calendarevent_count(user, from_ts, till_ts))

    # make dq figures
    fig.add_trace(go.Bar(x = timestamps, y = ema_counts, name = 'EMA'), row = 1, col = 1)
    fig.add_trace(go.Bar(x = timestamps, y = location_counts, name = 'Location'), row = 2, col = 1)
    fig.add_trace(go.Bar(x = timestamps, y = screenstate_counts, name = 'ScreenState'), row = 3, col = 1)
    fig.add_trace(go.Bar(x = timestamps, y = callog_counts, name = 'CallLog'), row = 4, col = 1)
    fig.add_trace(go.Bar(x = timestamps, y = activitytransition_counts, name = 'Activity#1'), row = 5, col = 1)
    fig.add_trace(go.Bar(x = timestamps, y = activityrecognition_counts, name = 'Activity#2'), row = 6, col = 1)
    fig.add_trace(go.Bar(x = timestamps, y = calendarevent_counts, name = 'CalendarEvent'), row = 7, col = 1)

  def add_smartwatch_dq_plots(fig, ppg_timestamps, acc_timestamps, offbody_timestamps, timestamps, delta):
    # amounts
    ppg_amounts = defaultdict(int)
    acc_amounts = defaultdict(int)
    offbody_amounts = defaultdict(int)

    # compute amount of samples
    for ts in timestamps:
      from_ts = int(ts.timestamp()*1000)
      till_ts = from_ts + delta.seconds*1000

      i = bleft(ppg_timestamps, from_ts)
      j = bright(ppg_timestamps, till_ts)
      ppg_amounts[ts] += j - i

      i = bleft(acc_timestamps, from_ts)
      j = bright(acc_timestamps, till_ts)
      acc_amounts[ts] += j - i

      i = bleft(offbody_timestamps, from_ts)
      j = bright(offbody_timestamps, till_ts)
      offbody_amounts[ts] += j - i

    # re-organize amount of samples
    ppg_amounts = [ppg_amounts[d] for d in timestamps]
    acc_amounts = [acc_amounts[d] for d in timestamps]
    offbody_amounts = [offbody_amounts[d] for d in timestamps]

    # make dq figures
    fig.add_trace(go.Bar(x = timestamps, y = ppg_amounts, name = 'PPG'), row = 8, col = 1)
    fig.add_trace(go.Bar(x = timestamps, y = acc_amounts, name = 'ACC'), row = 9, col = 1)
    fig.add_trace(go.Bar(x = timestamps, y = offbody_amounts, name = 'Offbody'), row = 10, col = 1)
    fig.update_layout(height = 500, showlegend = False)

  # generate plots
  plots = list()
  for user in users:
    from_ts = slc.get_first_timestamp(user)

    # make figure
    fig = make_subplots(
      rows = 10,
      cols = 1,
      shared_xaxes = True,
      vertical_spacing = 0.02,
      subplot_titles = [
        'EMA count',
        'OffBody count',
        'Location count',
        'Screen state count',
        'Call count',
        'Activity Transition count',
        'Activity Recognition count',
        'Calendar Event count',
        'PPG count',
        'Accelerometer count',
        'OffBody',
      ],
    )

    # file paths
    ppg_path = f'{environ["DATA_DUMP_DIR"]}/{user.email}/ppg.csv'
    acc_path = f'{environ["DATA_DUMP_DIR"]}/{user.email}/acc.csv'
    offbody_path = f'{environ["DATA_DUMP_DIR"]}/{user.email}/offbody.csv'

    # read smartwatch data files
    if exists(ppg_path):
      with open(ppg_path, 'r') as r:
        ppg_timestamps = sorted(map(lambda x: int(x[:x.index(',')]), r.readlines()))
        if ppg_timestamps: from_ts = min(from_ts, ppg_timestamps[0])
    else:
      ppg_timestamps = list()
    if exists(acc_path):
      with open(acc_path, 'r') as r:
        acc_timestamps = sorted(map(lambda x: int(x[:x.index(',')]), r.readlines()))
        if acc_timestamps: from_ts = min(from_ts, acc_timestamps[0])
    else:
      acc_timestamps = list()
    if exists(offbody_path):
      with open(offbody_path, 'r') as r:
        offbody_timestamps = sorted(map(lambda x: int(x[:x.index(',')]), r.readlines()))
        if offbody_timestamps: from_ts = min(from_ts, offbody_timestamps[0])
    else:
      offbody_timestamps = list()

    # make common timestamps for subplots for a selected day
    tz_korea = tz.gettz('Asia/Seoul')
    till_dt = dt.now(tz = tz_korea) + td(days = 1)
    till_dt.replace(hour = 0, minute = 0, second = 0, microsecond = 0)
    timestamps = list()
    d = dt.fromtimestamp(int(from_ts/1000), tz = tz_korea)
    while d < till_dt:
      timestamps.append(d)
      d += td(hours = 1)

    add_smartphone_dq_plots(fig, user, timestamps, td(hours = 1))
    add_smartwatch_dq_plots(fig, ppg_timestamps, acc_timestamps, offbody_timestamps, timestamps, td(hours = 1))

    fig.update_layout(height = 1000, showlegend = False)
    for annotation in fig['layout']['annotations']:
      annotation['textangle'] = 0

    fig.update_layout(margin = dict(l = 10, r = 10, t = 10, b = 10))
    plots.append(plotly.offline.plot(
      figure_or_data = fig,
      auto_open = False,
      output_type = "div",
    ))

  return render(
    request = request,
    template_name = 'dq.html',
    context = dict(
      title = f'{users[0].full_name}({users[0].email})' if len(users) == 1 else 'DQ plots',
      plots = plots,
      token = Token.objects.get(user = request.user).key,
    ),
  )
