from django.contrib.auth import authenticate
from django.utils.timezone import datetime as dt

from rest_framework import generics, permissions, authentication
from rest_framework import serializers
from rest_framework import response, status
from rest_framework.exceptions import ValidationError
from rest_framework.authtoken.models import Token

from firebase_admin.exceptions import InvalidArgumentError
from firebase_admin import messaging
import firebase_admin

from api import models as mdl
from api import services as svc
from api import selectors as slc
from api import serializers as srz

from os import environ, mkdir
from os.path import join, exists

DATA_DUMP_DIR = environ['DATA_DUMP_DIR']

# Firebase sdk
if not firebase_admin._apps:
  cred = firebase_admin.credentials.Certificate('fcm_secret.json')
  firebase_app = firebase_admin.initialize_app(credential = cred)


class SignUp(generics.CreateAPIView):

  class InputSerializer(serializers.Serializer):
    email = serializers.EmailField(required = True, allow_null = False, allow_blank = False)
    full_name = serializers.CharField(max_length = 128, required = True, allow_blank = False, allow_null = False)
    gender = serializers.CharField(max_length = 1, required = True, allow_blank = False, allow_null = False)
    date_of_birth = serializers.DateField(input_formats = [f'%Y%m%d'], required = True, allow_null = False)
    fcm_token = serializers.CharField(max_length = 256, default = None, allow_blank = True, allow_null = True)
    password = serializers.CharField(required = True, allow_null = False, min_length = 8)

    def validate(self, attrs):
      if slc.user_exists(email = attrs['email']):
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

  http_method_names = ['post']
  serializer_class = InputSerializer

  def post(self, request, *args, **kwargs):
    serializer = SignUp.InputSerializer(data = request.data)
    if not serializer.is_valid():
      return response.Response(serializer.errors, status = status.HTTP_400_BAD_REQUEST)

    new_user = svc.create_user(
      username = serializer.validated_data['email'],
      email = serializer.validated_data['email'],
      full_name = serializer.validated_data['full_name'],
      gender = serializer.validated_data['gender'],
      date_of_birth = serializer.validated_data['date_of_birth'],
      password = serializer.validated_data['password'],
    )

    serializer = srz.UserSerializer(instance = new_user)
    return response.Response(serializer.data, status = status.HTTP_201_CREATED)


class SignIn(generics.CreateAPIView):

  class InputSerializer(serializers.Serializer):
    email = serializers.EmailField(required = True, allow_null = False, allow_blank = False)
    password = serializers.CharField(required = True, allow_null = False, min_length = 8)

    class Meta:
      fields = '__all__'
      extra_kwargs = {'password': {'write_only': True}}

  http_method_names = ['post']
  serializer_class = InputSerializer

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


class SetFcmToken(generics.UpdateAPIView):

  class InputSerializer(serializers.Serializer):
    fcm_token = serializers.CharField(max_length = 256, required = True, allow_blank = False, allow_null = False)

    class Meta:
      fields = '__all__'

  authentication_classes = [authentication.TokenAuthentication]
  permission_classes = [permissions.IsAuthenticated]
  serializer_class = InputSerializer

  def update(self, request, *args, **kwargs):
    serializer = SetFcmToken.InputSerializer(data = request.data)
    if not serializer.is_valid():
      return response.Response(serializer.errors, status = status.HTTP_400_BAD_REQUEST)

    request.user.fcm_token = serializer.validated_data['fcm_token']
    request.user.save()

    return response.Response(status = status.HTTP_200_OK)


class InsertSelfReport(generics.CreateAPIView):
  queryset = mdl.SelfReport.objects
  serializer_class = srz.SelfReportSerializer
  authentication_classes = [authentication.TokenAuthentication]
  permission_classes = [permissions.IsAuthenticated]


class InsertOffBody(generics.CreateAPIView):
  queryset = mdl.OffBody.objects
  serializer_class = srz.OffBodySerializer
  authentication_classes = [authentication.TokenAuthentication]
  permission_classes = [permissions.IsAuthenticated]


class InsertPPG(generics.CreateAPIView):

  class InputSerializer(serializers.Serializer):
    file = serializers.FileField(required = True, allow_empty_file = False)

    def validate(self, attrs):
      filename_lower = attrs['file'].name.lower()
      if 'ppg' not in filename_lower or 'acc' in filename_lower:
        raise ValidationError(f'Filename must contain "ppg" and NOT contain "acc"')

      return attrs

    class Meta:
      fields = '__all__'

  authentication_classes = [authentication.TokenAuthentication]
  permission_classes = [permissions.IsAuthenticated]
  serializer_class = InputSerializer

  def post(self, request, *args, **kwargs):
    serializer = InsertPPG.InputSerializer(data = request.data)

    if not serializer.is_valid():
      return response.Response(serializer.errors, status = status.HTTP_400_BAD_REQUEST)

    # prepare user's directory
    dirpath = join(DATA_DUMP_DIR, request.user.email)
    if not exists(dirpath): mkdir(dirpath)

    # save the files
    file = serializer.validated_data['file']
    with open(join(dirpath, file.name), 'wb') as wb:
      wb.write(file.read())

    return response.Response(status = status.HTTP_200_OK)


class InsertAcc(generics.CreateAPIView):

  class InputSerializer(serializers.Serializer):
    file = serializers.FileField(required = True, allow_empty_file = False)

    def validate(self, attrs):
      filename_lower = attrs['file'].name.lower()
      if 'acc' not in filename_lower or 'ppg' in filename_lower:
        raise ValidationError(f'Filename must contain "acc" and NOT contain "ppg')

      return attrs

    class Meta:
      fields = '__all__'

  serializer_class = InputSerializer
  authentication_classes = [authentication.TokenAuthentication]
  permission_classes = [permissions.IsAuthenticated]

  def post(self, request, *args, **kwargs):
    serializer = InsertAcc.InputSerializer(data = request.data)

    if not serializer.is_valid():
      return response.Response(serializer.errors, status = status.HTTP_400_BAD_REQUEST)

    # prepare user's directory
    dirpath = join(DATA_DUMP_DIR, request.user.email)
    if not exists(dirpath): mkdir(dirpath)

    # save the files
    file = serializer.validated_data['file']
    with open(join(dirpath, file.name), 'wb') as wb:
      wb.write(file.read())

    return response.Response(status = status.HTTP_200_OK)


class SendEmaPush(generics.CreateAPIView):

  class InputSerializer(serializers.Serializer):
    pid = serializers.IntegerField(required = True)

    def validate(self, attrs):
      if not slc.user_exists(id = attrs['pid']):
        raise ValidationError('Invalid user id provided!')
      return attrs

    class Meta:
      fields = '__all__'

  serializer_class = InputSerializer
  authentication_classes = [authentication.TokenAuthentication]
  permission_classes = [permissions.IsAuthenticated, permissions.IsAdminUser]

  def post(self, request, *args, **kwargs):
    serializer = SendEmaPush.InputSerializer(data = request.data)

    if not serializer.is_valid():
      return response.Response(serializer.errors, status = status.HTTP_400_BAD_REQUEST)

    try:
      messaging.send(
        message = messaging.Message(
          android = messaging.AndroidConfig(
            priority = 'high',
            notification = messaging.AndroidNotification(
              title = "Stress report time!",
              body = "Please log your current situation and stress levels.",
              channel_id = 'sosw.app.push',
            ),
          ),
          token = slc.get_fcm_token(id = serializer.validated_data['pid']),
        ),
        app = firebase_app,
      )
      return response.Response(status = status.HTTP_200_OK)
    except InvalidArgumentError:
      return response.Response(status = status.HTTP_400_BAD_REQUEST)
