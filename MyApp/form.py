import os

from django import forms
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from MyApp.models import Child, GeneralSetting, GameSetting, EducationSetting, \
    ChatSetting, SingleGameSetting, ArtSetting, FitnessSetting, Notification
from ParentalNotification.settings import BASE_DIR


class LoginForm(forms.Form):
    login = forms.CharField(label="Username or Email", required=True)
    password = forms.CharField(widget=forms.PasswordInput(), required=True)


class RegisterForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(),
                               help_text="Create your password")
    confirm_password = forms.CharField(widget=forms.PasswordInput(),
                                       help_text="Comfirm your password")
    username = forms.CharField(help_text="No more than 150 characters")
    email = forms.EmailField(help_text="Enter your Email")

    class Meta:
        model = User
        fields = ('username', 'email', 'password',)

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise ValidationError("A user with that email already exists.")
        return email

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            raise ValidationError("A user with that username already exists.")
        return username

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')

        if password and confirm_password:
            if password != confirm_password:
                self.add_error('confirm_password', "The two password fields must match.")
                raise ValidationError("The two password fields must match.")
        return cleaned_data


class ChildForm(forms.ModelForm):
    class Meta:
        model = Child
        fields = ['email_address', 'name', 'age']


class MyAccountForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('username', 'email')

    def __init__(self, *args, **kwargs):
        super(MyAccountForm, self).__init__(*args, **kwargs)
        instance = kwargs.get('instance', None)
        if instance:
            self.initial['username'] = instance.username
            self.initial['email'] = instance.email


class BullyProcessForm(forms.ModelForm):
    Measurement = [
        ('No intervention', 'No intervention'),
        ('BigBuddy verbal reminder of bad behavior', 'BigBuddy verbal reminder of bad behavior'),
        ('Set points to zero', 'Set points to zero'),
        ('Exclude child from current session', 'Exclude child from current session'),
    ]
    bmeasurement_choices = forms.MultipleChoiceField(
        choices=Measurement,
        widget=forms.CheckboxSelectMultiple,
        required=False,
        label="Select measurements:"
    )

    class Meta:
        model = Notification
        fields = ['bmeasurement_choices']


class VictimProcessForm(forms.ModelForm):
    Measurement = [
        ('No intervention', 'No intervention'),
        ('BigBuddy verbal reminder of bad behavior', 'BigBuddy verbal reminder of bad behavior'),
        ('Comfort your child', 'Comfort your child'),
        ('Stop your child from current session', 'Stop your child from current session'),
    ]
    vmeasurement_choices = forms.MultipleChoiceField(
        choices=Measurement,
        widget=forms.CheckboxSelectMultiple,
        required=False,
        label="Select measurements:"
    )

    class Meta:
        model = Notification
        fields = ['vmeasurement_choices']


class GeneralSettingForm(forms.ModelForm):
    TIME_CHOICES = [(30, '30 minutes'), (60, '1 hour'), (90, '1.5 hours'),
                    (120, '2 hours'), (180, '3 hours'), (240, '4 hours')]
    daily_playtime = forms.ChoiceField(choices=TIME_CHOICES, required=False)
    file_path = os.path.join(BASE_DIR, 'static', 'bad-words.txt')
    with open(file_path, "r") as file:
        bad_words = [line.strip() for line in file if line.strip()]
    BAD_WORD_CHOICES = [(word, word) for word in bad_words]

    bad_words_choices = forms.MultipleChoiceField(
        choices=BAD_WORD_CHOICES,
        widget=forms.CheckboxSelectMultiple,
        required=False,
        label="Select bad words"
    )
    custom_bad_words = forms.CharField(
        widget=forms.TextInput(attrs={'placeholder': 'Separated by commas'}),
        required=False,
        label="Custom bad words"
    )
    INTERVENTION_CHOICES = [
        ('verbal', 'verbal reminders and educate'),
        ('silence', 'silence bad words')]
    bad_words_intervention = forms.MultipleChoiceField(
        choices=INTERVENTION_CHOICES,
        widget=forms.CheckboxSelectMultiple,
        required=False,
        label="Intervention Methods"
    )
    HOW_NOTIFICATION_CHOICE = [
        ('app', 'Notice on APP'),
        ('email', 'Email me'),
        ('sms', 'SMS me')]
    urgent_notification = forms.MultipleChoiceField(
        choices=HOW_NOTIFICATION_CHOICE,
        widget=forms.CheckboxSelectMultiple,
        required=False,
        label="How to notice"
    )
    WHAT_NOTIFICATION_CHOICE = [
        ('all', 'Notice all notifications'),
        ('bully', 'Notice when my child bullying'),
        ('victim', 'Notice when my child is bullied'),
        ('badword', 'Notice when my child say bad words'),
        ('badword_from_other', 'Notice when others say bad words to my child')]
    what_notification = forms.MultipleChoiceField(
        choices=WHAT_NOTIFICATION_CHOICE,
        widget=forms.CheckboxSelectMultiple,
        required=False,
        label="What to notice"
    )

    daily_playtime_start = forms.TimeField(
        widget=forms.TimeInput(format='%H:%M', attrs={'type': 'time'}),
        label="Daily Play Time Start",
        initial="08:00"
    )
    daily_playtime_end = forms.TimeField(
        widget=forms.TimeInput(format='%H:%M', attrs={'type': 'time'}),
        label="Daily Play Time End",
        initial="20:00"
    )

    class Meta:
        model = GeneralSetting
        fields = ['daily_playtime', 'bad_words_choices', 'custom_bad_words', 'bad_words_intervention',
                  'daily_playtime_start', 'daily_playtime_end',
                  'what_notification', 'urgent_notification']

    def __init__(self, *args, **kwargs):
        super(GeneralSettingForm, self).__init__(*args, **kwargs)
        instance = kwargs.get('instance', None)
        if instance:
            if instance.bad_words:
                selected_bad_words = instance.bad_words.split(',')
                self.initial['bad_words_choices'] = [word.strip() for word in selected_bad_words if
                                                     word.strip() in dict(self.BAD_WORD_CHOICES)]
                custom_words = [word.strip() for word in selected_bad_words if
                                word.strip() not in dict(self.BAD_WORD_CHOICES)]
                self.initial['custom_bad_words'] = ', '.join(custom_words)
            if instance.bad_words_intervention:
                self.initial['bad_words_intervention'] = [method.strip() for method in
                                                          instance.bad_words_intervention.split(',')]
            if instance.what_notification:
                self.initial['what_notification'] = [method.strip() for method in
                                                          instance.what_notification.split(',')]
                if instance.urgent_notification:
                    self.initial['urgent_notification'] = [method.strip() for method in
                                                              instance.urgent_notification.split(',')]
            self.initial['daily_playtime'] = instance.daily_playtime
            self.initial['daily_playtime_start'] = instance.daily_playtime_start.strftime('%H:%M')
            self.initial['daily_playtime_end'] = instance.daily_playtime_end.strftime('%H:%M')


Daily_TIME_CHOICES = [
    (15, '15 minutes'), (30, '30 minutes'), (45, '45 minutes'),
    (60, '60 minutes'), (90, '90 minutes'), (120, '2 hours'),
    (180, '3 hours'), (240, '4 hours')]
Break_TIME_CHOICES = [
    (minutes, f"{minutes}") for minutes in range(5, 61, 5)]
Duration_TIME_CHOICES = [
    (15, '15'), (30, '30'), (45, '45'),
    (60, '60'), (90, '90'), (120, '120')]


class GameSettingForm(forms.ModelForm):
    game_daily_playtime = forms.ChoiceField(choices=Daily_TIME_CHOICES, required=False)
    game_break_time = forms.ChoiceField(choices=Break_TIME_CHOICES, required=False)
    game_break_duration_time = forms.ChoiceField(choices=Duration_TIME_CHOICES, required=False)
    game_presence_of_ai = forms.ChoiceField(
        choices=[('Always', 'Always'),
                 ('bully', 'Only Appear when child is bullying'),
                 ('victim', 'Only Appear when child is bullying victim'),
                 ('urgent', 'Only Appear when bully OR victim situations')],
        widget=forms.RadioSelect,
        label="Visible of AI"
    )
    game_bully_action = forms.ChoiceField(
        choices=[
            ('exit', 'BigBuddy verbal reminders, set points to 0 AND exclude from the game'),
            ('point', 'BigBuddy verbal reminders AND set points to 0'),
            ('notice', 'BigBuddy verbal reminders and educate for bad behavior'),
            ('ignore', 'No intervention')],
        widget=forms.Select(attrs={'class': 'form-control fixed-width'}),
        required=False
    )
    game_victim_action = forms.ChoiceField(
        choices=[
            ('comfort', 'BigBuddy verbal notice, set points to 0 AND comfort child'),
            ('point', 'BigBuddy verbal reminders AND set bully points to 0'),
            ('notice', 'BigBuddy verbal notice about bad behavior'),
            ('ignore', 'No intervention')],
        widget=forms.Select(attrs={'class': 'form-control fixed-width'}),
        required=False
    )

    class Meta:
        model = GameSetting
        fields = ['game_daily_playtime', 'game_break_time', 'game_break_duration_time',
                  'game_presence_of_ai', 'game_bully_action', 'game_victim_action']

    def __init__(self, *args, **kwargs):
        super(GameSettingForm, self).__init__(*args, **kwargs)
        instance = kwargs.get('instance', None)
        if instance:
            self.initial['game_daily_playtime'] = instance.game_daily_playtime
            self.initial['game_break_time'] = instance.game_break_time
            self.initial['game_break_duration_time'] = instance.game_break_duration_time


class SingleGameSettingForm(forms.ModelForm):
    sgame_daily_playtime = forms.ChoiceField(choices=Daily_TIME_CHOICES, required=False)
    sgame_break_time = forms.ChoiceField(choices=Break_TIME_CHOICES, required=False)
    sgame_break_duration_time = forms.ChoiceField(choices=Duration_TIME_CHOICES, required=False)
    sgame_presence_of_ai = forms.ChoiceField(
        choices=[('Always', 'Always'),
                 ('sometimes', 'Only appear when child needs')],
        widget=forms.RadioSelect,
        label="Visible of AI"
    )

    class Meta:
        model = SingleGameSetting
        fields = ['sgame_daily_playtime', 'sgame_break_time', 'sgame_break_duration_time',
                  'sgame_presence_of_ai']

    def __init__(self, *args, **kwargs):
        super(SingleGameSettingForm, self).__init__(*args, **kwargs)
        instance = kwargs.get('instance', None)
        if instance:
            self.initial['sgame_daily_playtime'] = instance.sgame_daily_playtime
            self.initial['sgame_break_time'] = instance.sgame_break_time
            self.initial['sgame_break_duration_time'] = instance.sgame_break_duration_time


class EducationSettingForm(forms.ModelForm):
    edu_daily_playtime = forms.ChoiceField(choices=Daily_TIME_CHOICES, required=False)
    edu_break_time = forms.ChoiceField(choices=Break_TIME_CHOICES, required=False)
    edu_break_duration_time = forms.ChoiceField(choices=Duration_TIME_CHOICES, required=False)
    edu_presence_of_ai = forms.ChoiceField(
        choices=[('Always', 'Always'),
                 ('bully', 'Only Appear when child is bullying'),
                 ('victim', 'Only Appear when child is bullying victim'),
                 ('urgent', 'Only Appear when bully OR victim situations')],
        widget=forms.RadioSelect,
        label="Visible of AI"
    )
    edu_bully_action = forms.ChoiceField(
        choices=[
            ('exit', 'BigBuddy verbal reminders AND exclude from current session'),
            ('notice', 'BigBuddy verbal reminders and educate for bad behavior'),
            ('ignore', 'No intervention')],
        widget=forms.Select(attrs={'class': 'form-control fixed-width'}),
        required=False
    )
    edu_victim_action = forms.ChoiceField(
        choices=[
            ('exit', 'BigBuddy verbal reminders, comfort child AND exclude bully from current session'),
            ('comfort', 'BigBuddy verbal notice AND comfort your child'),
            ('notice', 'BigBuddy verbal notice about bad behavior'),
            ('ignore', 'No intervention')],
        widget=forms.Select(attrs={'class': 'form-control fixed-width'}),
        required=False
    )

    class Meta:
        model = EducationSetting
        fields = ['edu_daily_playtime', 'edu_break_time', 'edu_break_duration_time',
                  'edu_presence_of_ai', 'edu_bully_action', 'edu_victim_action']

    def __init__(self, *args, **kwargs):
        super(EducationSettingForm, self).__init__(*args, **kwargs)
        instance = kwargs.get('instance', None)
        if instance:
            self.initial['edu_daily_playtime'] = instance.edu_daily_playtime
            self.initial['edu_break_time'] = instance.edu_break_time
            self.initial['edu_break_duration_time'] = instance.edu_break_duration_time


class ChatSettingForm(forms.ModelForm):
    chat_daily_playtime = forms.ChoiceField(choices=Daily_TIME_CHOICES, required=False)
    chat_break_time = forms.ChoiceField(choices=Break_TIME_CHOICES, required=False)
    chat_break_duration_time = forms.ChoiceField(choices=Duration_TIME_CHOICES, required=False)
    chat_presence_of_ai = forms.ChoiceField(
        choices=[('Always', 'Always'),
                 ('bully', 'Only Appear when child is bullying'),
                 ('victim', 'Only Appear when child is victim'),
                 ('urgent', 'Only Appear when bully OR victim situations')],
        widget=forms.RadioSelect,
        label="Visible of AI"
    )
    chat_bully_action = forms.ChoiceField(
        choices=[
            ('exit', 'BigBuddy verbal reminders AND stop current chat'),
            ('notice', 'BigBuddy verbal reminders and educate for bad behavior'),
            ('ignore', 'No intervention')],
        widget=forms.Select(attrs={'class': 'form-control fixed-width'}),
        required=False
    )
    chat_victim_action = forms.ChoiceField(
        choices=[
            ('exit', 'BigBuddy verbal notice, comfort your child AND stop current chat'),
            ('comfort', 'BigBuddy verbal notice AND comfort your child'),
            ('notice', 'BigBuddy verbal notice about bad behavior'),
            ('ignore', 'No intervention')],
        widget=forms.Select(attrs={'class': 'form-control fixed-width'}),
        required=False
    )
    who_can_chat = forms.ChoiceField(
        choices=[
            ('friend', 'Friends only'),
            ('everyone', 'Everyone')],
        widget=forms.RadioSelect,
        required=False
    )

    class Meta:
        model = ChatSetting
        fields = ['chat_daily_playtime', 'chat_break_time', 'chat_break_duration_time',
                  'chat_presence_of_ai', 'who_can_chat', 'chat_bully_action', 'chat_victim_action']

    def __init__(self, *args, **kwargs):
        super(ChatSettingForm, self).__init__(*args, **kwargs)
        instance = kwargs.get('instance', None)
        if instance:
            self.initial['chat_daily_playtime'] = instance.chat_daily_playtime
            self.initial['chat_break_time'] = instance.chat_break_time
            self.initial['chat_break_duration_time'] = instance.chat_break_duration_time


class FitnessSettingForm(forms.ModelForm):
    fitness_daily_playtime = forms.ChoiceField(choices=Daily_TIME_CHOICES, required=False)
    fitness_break_time = forms.ChoiceField(choices=Break_TIME_CHOICES, required=False)
    fitness_break_duration_time = forms.ChoiceField(choices=Duration_TIME_CHOICES, required=False)
    fitness_presence_of_ai = forms.ChoiceField(
        choices=[('Always', 'Always'),
                 ('Hurt', 'Appear when child get hurt'),
                 ('Need', 'Only Appear when child needs')],
        widget=forms.RadioSelect,
        label="Visible of AI"
    )

    class Meta:
        model = FitnessSetting
        fields = ['fitness_daily_playtime', 'fitness_break_time', 'fitness_break_duration_time',
                  'fitness_presence_of_ai']

    def __init__(self, *args, **kwargs):
        super(FitnessSettingForm, self).__init__(*args, **kwargs)
        instance = kwargs.get('instance', None)
        if instance:
            self.initial['fitness_daily_playtime'] = instance.fitness_daily_playtime
            self.initial['fitness_break_time'] = instance.fitness_break_time
            self.initial['fitness_break_duration_time'] = instance.fitness_break_duration_time


class ArtSettingForm(forms.ModelForm):
    art_daily_playtime = forms.ChoiceField(choices=Daily_TIME_CHOICES, required=False)
    art_break_time = forms.ChoiceField(choices=Break_TIME_CHOICES, required=False)
    art_break_duration_time = forms.ChoiceField(choices=Duration_TIME_CHOICES, required=False)
    art_presence_of_ai = forms.ChoiceField(
        choices=[('Always', 'Always'),
                 ('sometimes', 'Only appear when child needs')],
        widget=forms.RadioSelect,
        label="Visible of AI"
    )

    class Meta:
        model = ArtSetting
        fields = ['art_daily_playtime', 'art_break_time', 'art_break_duration_time',
                  'art_presence_of_ai']

    def __init__(self, *args, **kwargs):
        super(ArtSettingForm, self).__init__(*args, **kwargs)
        instance = kwargs.get('instance', None)
        if instance:
            self.initial['art_daily_playtime'] = instance.art_daily_playtime
            self.initial['art_break_time'] = instance.art_break_time
            self.initial['art_break_duration_time'] = instance.art_break_duration_time
