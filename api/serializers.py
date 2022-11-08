from django.core.exceptions import ValidationError

from rest_framework import serializers

from api import models as mdl
from api import services as svc
from api import selectors as slc
from api import utils


class UserSerializer(serializers.ModelSerializer):
	full_name = serializers.CharField(required = True)
	date_of_birth = serializers.CharField(required = True)

	def validate(self, attrs):
		if not utils.is_valid_date(date_str = attrs['date_of_birth']):
			raise ValidationError(f'Invalid date of birth ({attrs["date_of_birth"]}) was provided')

		if slc.user_exists(full_name = attrs['full_name'], date_of_birth = attrs['full_name']):
			raise ValidationError(f'User ({attrs["full_name"]}, {attrs["full_name"]}) already exists')

		return attrs

	class Meta:
		model = mdl.User
		fields = ('email',)


class AnswerSerializer(serializers.ModelSerializer):

	class Meta:
		model = mdl.Answer
		fields = (
			'slug',
			'title',
			'is_correct',
		)

	slug = serializers.SlugField(read_only = True)
	title = serializers.CharField(min_length = 1, max_length = 2048, allow_null = False, allow_blank = False, required = True)
	is_correct = serializers.BooleanField(allow_null = False, required = True)


class QuestionSerializer(serializers.ModelSerializer):

	class Meta:
		model = mdl.Question
		fields = ('slug', 'title', 'type', 'answers')
		MIN_ANS_COUNT = 1
		MAX_ANS_COUNT = 5

	slug = serializers.SlugField(required = False)
	title = serializers.CharField(min_length = 1, max_length = 2048, allow_null = False, allow_blank = False, required = True)
	type = serializers.ChoiceField(choices = mdl.Question.Type.choices, allow_null = False, allow_blank = False, required = True)
	answers = AnswerSerializer(many = True, required = True)

	def validate(self, attrs):
		ans_count = len(attrs['answers'])
		# 1. validate minimum amount of answers
		if ans_count < QuestionSerializer.Meta.MIN_ANS_COUNT or QuestionSerializer.Meta.MAX_ANS_COUNT < ans_count:
			raise ValidationError(
				f'Question must include {QuestionSerializer.Meta.MIN_ANS_COUNT}-{QuestionSerializer.Meta.MAX_ANS_COUNT} answer options!')

		# 2. validate amount of correct answers
		cor_ans_count = sum([1 for ans in attrs['answers'] if ans['is_correct']])
		if cor_ans_count < 1:   # no correct answer
			raise ValidationError(f'Question must have correct answer(s)!')
		if cor_ans_count > 1 and attrs['type'] == mdl.Question.Type.SINGLE_CHOICE:   # multiple correct answers for a single choice question
			raise ValidationError(f'Single choice question must have only one correct answer!')

		return attrs


class QuizSerializer(serializers.ModelSerializer):

	class Meta:
		model = mdl.Quiz
		fields = (
			'slug',
			'title',
			'is_published',
			'creator_user',
			'questions',
		)
		MIN_QUESTION_COUNT = 1
		MAX_QUESTION_COUNT = 10

	slug = serializers.SlugField(read_only = True)
	is_published = serializers.BooleanField(read_only = True)
	creator_user = UserSerializer(read_only = True)
	title = serializers.CharField(allow_null = False, required = True)
	questions = QuestionSerializer(many = True, allow_null = False, required = True)

	def validate(self, attrs):
		err = ValidationError(f'Quiz must include {QuizSerializer.Meta.MIN_QUESTION_COUNT}-{QuizSerializer.Meta.MAX_QUESTION_COUNT} questions!')

		# amount of questions check
		question_count = len(attrs['questions'])
		if question_count < QuizSerializer.Meta.MIN_QUESTION_COUNT or QuizSerializer.Meta.MAX_QUESTION_COUNT < question_count:
			raise err

		return attrs

	def create(self, validated_data):
		the_quiz = svc.create_quiz(creator_user = self.context['request'].user, **validated_data)
		return the_quiz


class QuizResponseSerializer(serializers.ModelSerializer):

	class Meta:
		model = mdl.QuizResponse
		fields = (
			'slug',
			'user',
			'quiz',
			'selections',
		)

	slug = serializers.SlugField(read_only = True)
	user = UserSerializer(allow_null = False, required = True)
	quiz = QuizSerializer(allow_null = False, required = True)
	selections = AnswerSerializer(many = True, allow_null = False, required = True)


class ReadOnlyAnswerSerializer(serializers.ModelSerializer):

	class Meta:
		model = mdl.Answer
		fields = (
			'slug',
			'title',
		)

	slug = serializers.SlugField(read_only = True)
	title = serializers.CharField(read_only = True)


class ReadOnlyQuestionSerializer(serializers.ModelSerializer):

	class Meta:
		model = mdl.Question
		fields = ('slug', 'title', 'type', 'answers')

	slug = serializers.SlugField(read_only = True)
	title = serializers.CharField(read_only = True)
	type = serializers.ChoiceField(read_only = True, choices = mdl.Question.Type.choices)
	answers = ReadOnlyAnswerSerializer(read_only = True)


class ReadOnlyQuizSerializer(serializers.ModelSerializer):

	class Meta:
		model = mdl.Quiz
		fields = (
			'slug',
			'title',
			'is_published',
			'creator_user',
			'questions',
		)

	slug = serializers.SlugField(read_only = True)
	is_published = serializers.BooleanField(read_only = True)
	creator_user = UserSerializer(read_only = True)
	title = serializers.CharField(read_only = True)
	questions = ReadOnlyQuestionSerializer(read_only = True)


class ReadOnlyQuizResponseSerializer(serializers.ModelSerializer):

	class Meta:
		model = mdl.QuizResponse
		fields = ('slug', 'user', 'quiz', 'selections', 'scores')

	slug = serializers.SlugField(read_only = True)
	user = UserSerializer(read_only = True)
	quiz = ReadOnlyQuizSerializer(read_only = True)
	selections = ReadOnlyAnswerSerializer(read_only = True)
	scores = serializers.SerializerMethodField()

	def get_scores(self, obj):
		return slc.get_quiz_response_score(obj)
