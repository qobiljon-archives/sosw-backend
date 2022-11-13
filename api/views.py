from django.contrib.auth import authenticate
from django.utils.timezone import datetime as dt

from rest_framework import generics, permissions, authentication
from rest_framework import serializers
from rest_framework import response, status
from rest_framework.exceptions import ValidationError
from rest_framework.authtoken.models import Token

from firebase_admin import messaging
import firebase_admin

from api import models as mdl
from api import services as svc
from api import selectors as slc
from api import serializers as srz

from os import environ
from os.path import join

# Firebase sdk
if not firebase_admin._apps:
  cred = firebase_admin.credentials.Certificate('fcm_secret.json')
  firebase_app = firebase_admin.initialize_app(credential = cred)
"""
messaging.send(message = messaging.Message(android = messaging.AndroidConfig(priority = 'high',
				notification = messaging.AndroidNotification(title = "Stress report time!",
				body = "Please log your current situation and stress levels.",
				channel_id = 'sosw.app.push')),
				token = User.objects.get(id = pid).fcm_token),
				app = firebase_app
			)
"""


class SignUp(generics.CreateAPIView):
  serializer_class = 'InputSerializer'

  def post(self, request, *args, **kwargs):
    serializer = SignUp.InputSerializer(data = request.data)
    if not serializer.is_valid():
      return response.Response(serializer.errors, status = status.HTTP_400_BAD_REQUEST)

    new_user = mdl.User.objects.create_user(
      username = serializer.validated_data['email'],
      email = serializer.validated_data['email'],
      full_name = serializer.validated_data['full_name'],
      gender = serializer.validated_data['gender'],
      date_of_birth = serializer.validated_data['date_of_birth'],
      password = serializer.validated_data['password'],
    )

    serializer = srz.UserSerializer(instance = new_user)
    return response.Response(serializer.data, status = status.HTTP_201_CREATED)

  class InputSerializer(serializers.Serializer):
    email = serializers.EmailField(required = True, allow_null = False, allow_blank = False)
    full_name = serializers.CharField(max_length = 128, required = True, allow_blank = False, allow_null = False)
    gender = serializers.CharField(max_length = 1, required = True, allow_blank = False, allow_null = False)
    date_of_birth = serializers.DateField(input_formats = [f'%Y%m%d'], required = True, allow_null = False)
    fcm_token = serializers.CharField(max_length = 128, required = True, allow_blank = False, allow_null = False)
    password = serializers.CharField(required = True, allow_null = False, min_length = 8)

    def validate(self, attrs):
      if mdl.User.objects.filter(email = attrs['email']).exists():
        raise ValidationError('Email already registered')

      if attrs['gender'] not in ['f', 'F', 'm', 'M']:
        raise ValidationError('Gender can be "F" or "M" only')
      attrs['gender'] = attrs['gender'].upper()

      if attrs['date_of_birth'] > dt.today().date():
        raise ValidationError('Date of birth cannot be in future!')

      return attrs

    class Meta:
      fields = '__all__'
      extra_kwargs = {'password': {'write_only': True}}


class SignIn(generics.CreateAPIView):
  queryset = mdl.User.objects
  serializer_class = 'InputSerializer'

  def post(self, request, *args, **kwargs):
    serializer = SignIn.InputSerializer(data = request.data)
    if not serializer.is_valid():
      return response.Response(serializer.errors, status = status.HTTP_400_BAD_REQUEST)

    user = authenticate(
      username = serializer.validated_data['email'],
      password = serializer.validated_data['password'],
    )
    if not user:
      return response.Response(dict(credentials = 'Incorrect credentials'), status = status.HTTP_400_BAD_REQUEST)

    serializer = srz.ReadOnlyTokenSerializer(instance = Token.objects.get(user = user))
    return response.Response(serializer.data, status = status.HTTP_200_OK)

  class InputSerializer(serializers.Serializer):
    email = serializers.EmailField(required = True, allow_null = False, allow_blank = False)
    password = serializers.CharField(required = True, allow_null = False, min_length = 8)

    class Meta:
      fields = '__all__'
      extra_kwargs = {'password': {'write_only': True}}


class InsertSelfReport(generics.CreateAPIView):
  queryset = mdl.SelfReport.objects
  serializer_class = srz.SelfReportSerializer
  authentication_classes = [authentication.TokenAuthentication]
  permission_classes = [permissions.IsAuthenticated]


class InsertBVP(generics.CreateAPIView):
  serializer_class = 'InputSerializer'
  authentication_classes = [authentication.TokenAuthentication]
  permission_classes = [permissions.IsAuthenticated]

  def post(self, request, *args, **kwargs):
    serializer = InsertBVP.InputSerializer(data = request.data)

    if not serializer.is_valid():
      return response.Response(serializer.errors, status = status.HTTP_400_BAD_REQUEST)

    files = serializer.validated_data['files']
    for file in files:
      with open(join(environ['DATA_DUMP_DIR'], file.name), 'wb') as wb:
        wb.write(file.read())

    return response.Response(status = status.HTTP_200_OK)

  class InputSerializer(serializers.Serializer):
    files = serializers.ListField(
      child = serializers.FileField(required = True, allow_empty_file = False),
      allow_empty = False,
      max_length = 10,
    )

    class Meta:
      fields = '__all__'
