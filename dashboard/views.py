from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib.auth import logout

from rest_framework.authtoken.models import Token

from os.path import exists
from os import environ
import pandas as pd

from api import selectors as slc
from dashboard.utils import count_file_lines
from plotly.subplots import make_subplots
import plotly.graph_objects as go
import plotly
import time


@login_required
@user_passes_test(lambda u: u.is_superuser)
def handle_index(request):
  return render(
    request = request,
    template_name = 'index.html',
    context = dict(
      title = 'Stress with smartwatches',
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

  def add_smartphone_dq_plots(user, fig, from_ts, till_ts):
    # Self Report submissions
    self_reports = slc.get_self_reports(user, from_ts, till_ts)
    x = [x.timestamp for x in self_reports]
    y = [1]*len(x)
    self_report_df = pd.DataFrame(dict(timestamp = x, value = y))
    self_report_df.timestamp = pd.to_datetime(
      self_report_df.timestamp,
      unit = 'ms',
      utc = True,
    ).map(lambda x: x.tz_convert('Asia/Seoul'))
    self_report_df.set_index(keys = ['timestamp'], drop = True, inplace = True)

    # Off Body detections
    off_bodys = slc.get_off_bodys(user, from_ts, till_ts)
    x = [x.timestamp for x in off_bodys]
    y = [1]*len(x)
    off_body_df = pd.DataFrame(dict(timestamp = x, value = y))
    off_body_df.timestamp = pd.to_datetime(
      off_body_df.timestamp,
      unit = 'ms',
      utc = True,
    ).map(lambda x: x.tz_convert('Asia/Seoul'))
    off_body_df.set_index(keys = ['timestamp'], drop = True, inplace = True)

    # Locations
    locations = slc.get_locations(user, from_ts, till_ts)
    x = [x.timestamp for x in locations]
    y = [1]*len(x)
    location_df = pd.DataFrame(dict(timestamp = x, value = y))
    location_df.timestamp = pd.to_datetime(
      location_df.timestamp,
      unit = 'ms',
      utc = True,
    ).map(lambda x: x.tz_convert('Asia/Seoul'))
    location_df.set_index(keys = ['timestamp'], drop = True, inplace = True)

    # Screen State changes
    screen_states = slc.get_screen_states(user, from_ts, till_ts)
    x = [x.timestamp for x in screen_states]
    y = [1]*len(x)
    screen_state_df = pd.DataFrame(dict(timestamp = x, value = y))
    screen_state_df.timestamp = pd.to_datetime(
      screen_state_df.timestamp,
      unit = 'ms',
      utc = True,
    ).map(lambda x: x.tz_convert('Asia/Seoul'))
    screen_state_df.set_index(keys = ['timestamp'], drop = True, inplace = True)

    # Call logs
    call_logs = slc.get_screen_states(user, from_ts, till_ts)
    x = [x.timestamp for x in call_logs]
    y = [1]*len(x)
    call_log_df = pd.DataFrame(dict(timestamp = x, value = y))
    call_log_df.timestamp = pd.to_datetime(
      call_log_df.timestamp,
      unit = 'ms',
      utc = True,
    ).map(lambda x: x.tz_convert('Asia/Seoul'))
    call_log_df.set_index(keys = ['timestamp'], drop = True, inplace = True)

    # Activity transitions
    activity_transitions = slc.get_screen_states(user, from_ts, till_ts)
    x = [x.timestamp for x in activity_transitions]
    y = [1]*len(x)
    activity_transition_df = pd.DataFrame(dict(timestamp = x, value = y))
    activity_transition_df.timestamp = pd.to_datetime(
      activity_transition_df.timestamp,
      unit = 'ms',
      utc = True,
    ).map(lambda x: x.tz_convert('Asia/Seoul'))
    activity_transition_df.set_index(keys = ['timestamp'], drop = True, inplace = True)

    # Activity recognitions
    activity_recognitions = slc.get_screen_states(user, from_ts, till_ts)
    x = [x.timestamp for x in activity_recognitions]
    y = [1]*len(x)
    activity_recognition_df = pd.DataFrame(dict(timestamp = x, value = y))
    activity_recognition_df.timestamp = pd.to_datetime(
      activity_recognition_df.timestamp,
      unit = 'ms',
      utc = True,
    ).map(lambda x: x.tz_convert('Asia/Seoul'))
    activity_recognition_df.set_index(keys = ['timestamp'], drop = True, inplace = True)

    # Calendar events
    calendar_events = slc.get_screen_states(user, from_ts, till_ts)
    x = [x.timestamp for x in calendar_events]
    y = [1]*len(x)
    calendar_event_df = pd.DataFrame(dict(timestamp = x, value = y))
    calendar_event_df.timestamp = pd.to_datetime(
      calendar_event_df.timestamp,
      unit = 'ms',
      utc = True,
    ).map(lambda x: x.tz_convert('Asia/Seoul'))
    calendar_event_df.set_index(keys = ['timestamp'], drop = True, inplace = True)

    # resample, count
    self_report_df = self_report_df.resample('10Min').count()
    off_body_df = off_body_df.resample('10Min').count()
    location_df = location_df.resample('10Min').count()
    screen_state_df = screen_state_df.resample('10Min').count()
    call_log_df = call_log_df.resample('10Min').count()
    activity_transition_df = activity_transition_df.resample('10Min').count()
    activity_recognition_df = activity_recognition_df.resample('10Min').count()
    calendar_event_df = calendar_event_df.resample('10Min').count()

    # make dq figures
    fig.add_trace(
      go.Bar(x = self_report_df.index, y = self_report_df['value'], name = 'SelfReport'),
      row = 1,
      col = 1,
    )
    fig.add_trace(
      go.Bar(x = off_body_df.index, y = off_body_df['value'], name = 'SelfReport'),
      row = 2,
      col = 1,
    )
    fig.add_trace(
      go.Bar(x = location_df.index, y = location_df['value'], name = 'SelfReport'),
      row = 3,
      col = 1,
    )
    fig.add_trace(
      go.Bar(x = screen_state_df.index, y = screen_state_df['value'], name = 'SelfReport'),
      row = 4,
      col = 1,
    )
    fig.add_trace(
      go.Bar(x = call_log_df.index, y = call_log_df['value'], name = 'SelfReport'),
      row = 5,
      col = 1,
    )
    fig.add_trace(
      go.Bar(x = activity_transition_df.index, y = activity_transition_df['value'], name = 'SelfReport'),
      row = 6,
      col = 1,
    )
    fig.add_trace(
      go.Bar(x = activity_recognition_df.index, y = activity_recognition_df['value'], name = 'SelfReport'),
      row = 7,
      col = 1,
    )
    fig.add_trace(
      go.Bar(x = calendar_event_df.index, y = calendar_event_df['value'], name = 'SelfReport'),
      row = 8,
      col = 1,
    )
    return fig

  def add_smartwatch_dq_plots(user, fig, from_ts, till_ts):
    # file paths
    ppg_path = f'{environ["DATA_DUMP_DIR"]}/{user.email}/ppg.csv'
    acc_path = f'{environ["DATA_DUMP_DIR"]}/{user.email}/acc.csv'
    offbody_path = f'{environ["DATA_DUMP_DIR"]}/{user.email}/offbody.csv'
    if any(not exists(x) for x in [ppg_path, acc_path, offbody_path]): return

    # load files
    ppg_df = pd.read_csv(
      ppg_path,
      names = ['ts', 'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p'],
      dtype = dict(
        ts = int,
        a = float,
        b = float,
        c = float,
        d = float,
        e = float,
        f = float,
        g = float,
        h = float,
        i = float,
        j = float,
        k = float,
        l = float,
        m = float,
        n = float,
        o = float,
        p = float,
      ),
      skiprows = max(
        0,
        count_file_lines(ppg_path) - 540_000,
      ),
    )[['ts', 'a']]
    acc_df = pd.read_csv(
      acc_path,
      names = ['ts', 'x', 'y', 'z'],
      dtype = dict(ts = int, x = float, y = float, z = float),
      skiprows = max(
        0,
        count_file_lines(acc_path) - 540_000,
      ),
    )[['ts', 'x']]
    offbody_df = pd.read_csv(
      offbody_path,
      names = ['ts', 'off_body'],
      dtype = dict(ts = int, off_body = str),
    )[['ts', 'off_body']]

    # timestamp range
    # till_ts = max(ppg_df.ts.max(), acc_df.ts.max(), offbody_df.ts.max())
    # from_ts = till_ts - 36*60*60*1000

    # make timestamp range same across dataframes
    ppg_df = pd.concat(
      [ppg_df, pd.DataFrame([[from_ts, 0], [till_ts, 0]], columns = ['ts', 'a'])],
      ignore_index = True,
    )
    acc_df = pd.concat(
      [acc_df, pd.DataFrame([[from_ts, 0], [till_ts, 0]], columns = ['ts', 'x'])],
      ignore_index = True,
    )
    offbody_df = pd.concat(
      [offbody_df, pd.DataFrame([[from_ts, 'false'], [till_ts, 'false']], columns = ['ts', 'off_body'])],
      ignore_index = True,
    )

    # filter by time (last 48 hours)
    ppg_df = ppg_df[(from_ts <= ppg_df.ts) & (ppg_df.ts <= till_ts)]
    acc_df = acc_df[(from_ts <= acc_df.ts) & (acc_df.ts <= till_ts)]
    offbody_df = offbody_df[(from_ts <= offbody_df.ts) & (offbody_df.ts <= till_ts)]

    # convert timezone
    ppg_df.ts = pd.to_datetime(ppg_df.ts, unit = 'ms', utc = True).map(lambda x: x.tz_convert('Asia/Seoul'))
    acc_df.ts = pd.to_datetime(acc_df.ts, unit = 'ms', utc = True).map(lambda x: x.tz_convert('Asia/Seoul'))
    offbody_df.ts = pd.to_datetime(offbody_df.ts, unit = 'ms', utc = True).map(lambda x: x.tz_convert('Asia/Seoul'))

    # set indices
    ppg_df.set_index('ts', drop = True, inplace = True)
    acc_df.set_index('ts', drop = True, inplace = True)
    offbody_df.set_index('ts', drop = True, inplace = True)

    # count value frequencies
    ppg_df = ppg_df.resample('10Min').count()
    acc_df = acc_df.resample('10Min').count()
    offbody_df = offbody_df.resample('10Min').count()

    # make dq figures
    fig.add_trace(go.Bar(x = ppg_df.index, y = ppg_df['a'], name = 'PPG'), row = 9, col = 1)
    fig.add_trace(go.Bar(x = acc_df.index, y = acc_df['x'], name = 'ACC'), row = 10, col = 1)
    fig.add_trace(go.Bar(x = offbody_df.index, y = offbody_df['off_body'], name = 'Offbody'), row = 11, col = 1)
    fig.update_layout(height = 500, showlegend = False)

    # make offline plot
    return plotly.offline.plot(
      figure_or_data = fig,
      auto_open = False,
      output_type = "div",
    )

  plots = list()
  till_ts = int(time.time()*1000)
  from_ts = till_ts - 36*60*60*1000
  for user in users:
    fig = make_subplots(
      rows = 11,
      cols = 1,
      shared_xaxes = True,
      vertical_spacing = 0.02,
      row_titles = [
        'EMA',
        'OffBody',
        'Location',
        'Lock',
        'Calls',
        'Activity1',
        'Activity2',
        'Calendar',
        'PPG',
        'ACC',
        'OffBody',
      ],
    )
    add_smartphone_dq_plots(user, fig, from_ts, till_ts)
    add_smartwatch_dq_plots(user, fig, from_ts, till_ts)
    fig.update_layout(height = 1000, showlegend = False)
    for annotation in fig['layout']['annotations']:
      annotation['textangle'] = 0
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
