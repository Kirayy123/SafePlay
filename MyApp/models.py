from django.db import models

# Create your models here.

from django.db import models
from django.contrib.auth.models import User


class Child(models.Model):
    parent = models.ForeignKey(User, on_delete=models.CASCADE, related_name='children')
    name = models.CharField(max_length=255, default=None)
    email_address = models.EmailField(max_length=100, unique=True)
    AGE_CHOICES = (
        (0, 'under 12'),
        (1, '12-16'),
        (2, '16+')
    )
    age = models.IntegerField(choices=AGE_CHOICES, default=0)


class Notification(models.Model):
    child = models.ForeignKey(Child, on_delete=models.CASCADE, related_name='notifications')
    text = models.TextField(default=None)
    time = models.DateTimeField(default=False)
    TYPE_CHOICES = (
        (0, 'Enter game'),
        (3, 'Exit game'),
        (1, 'Victim'),
        (2, 'Bully'),
        (4, 'bad word'),
        (5, 'interaction')
    )
    type = models.IntegerField(choices=TYPE_CHOICES, default=0)
    processed = models.BooleanField(default=False)
    processed_measures = models.TextField(null=True, blank=True)
    game_url = models.URLField(null=True, blank=True)
    GAME_TYPE_CHOICES = (
        (0, 'MultiPlayerGame'),
        (1, 'SinglePlayerGame'),
        (2, 'Education'),
        (3, 'Art_Creativity'),
        (4, 'Fitness'),
        (5, 'Chat'))
    game_type = models.IntegerField(choices=GAME_TYPE_CHOICES, default=0)


class GameSession(models.Model):
    GAME_TYPES = (
        (1, 'Multi-Player Game'),
        (2, 'One-Player Game'),
        (3, 'Education VR'),
        (4, 'Chat Platforms'),
        (5, 'Creative VR'),
        (6, 'Fitness VR'),
    )
    child = models.ForeignKey(Child, on_delete=models.CASCADE, related_name='game_sessions')
    game_name = models.CharField(max_length=255, default=None)
    start_time = models.DateTimeField(default=None)
    end_time = models.DateTimeField(default=None)
    players = models.TextField(default=None)
    satisfaction = models.IntegerField(default=None)
    video = models.FileField(upload_to='videos', default=None)
    video_url = models.URLField(null=True, default="https://youtu.be/YJDaypZl6Jk")
    game_type = models.IntegerField(choices=GAME_TYPES)
    bully_num = models.IntegerField(null=True, blank=True)
    victim_num = models.IntegerField(null=True, blank=True)
    bully_info = models.TextField(null=True, blank=True)
    victim_info = models.TextField(null=True, blank=True)

    @property
    def session_duration(self):
        return (self.end_time - self.start_time).total_seconds() / 60  # calculate minutes


class Message(models.Model):
    child = models.ForeignKey(Child, on_delete=models.CASCADE, related_name='messages')
    text = models.TextField(default=None)
    time = models.DateTimeField(auto_now_add=True)
    TAG_CHOICES = (
        (0, 'From Parent'),
        (1, 'From Child')
    )
    tag = models.IntegerField(choices=TAG_CHOICES, default=0)


class Setting(models.Model):
    child = models.ForeignKey(Child, on_delete=models.CASCADE, related_name='settings')
    bad_words = models.TextField(null=True, blank=True)
    urgent_notification = models.BooleanField(default=False)

    game_daily_playtime = models.IntegerField(null=True, blank=True)
    game_break_time = models.IntegerField(null=True, blank=True)
    game_break_duration_time = models.IntegerField(null=True, blank=True)
    game_presence_of_ai = models.BooleanField(default=False)
    game_bully_action = models.TextField(
        choices=[
            ('exit', 'BigBuddy verbal reminders, set points to 0 AND exclude from the game'),
            ('point', 'BigBuddy verbal reminders AND set points to 0'),
            ('notice', 'BigBuddy verbal reminders for bad behavior'),
            ('ignore', 'No intervention')], default='exit')
    game_victim_action = models.TextField(
        choices=[
            ('comfort', 'BigBuddy verbal notice, set points to 0 AND comfort child'),
            ('point', 'BigBuddy verbal reminders AND set bully points to 0'),
            ('notice', 'BigBuddy verbal notice about bad behavior'),
            ('ignore', 'No intervention'), ], default='comfort')

    ed_daily_playtime = models.IntegerField(null=True, blank=True)
    ed_break_time = models.IntegerField(null=True, blank=True)
    ed_break_duration_time = models.IntegerField(null=True, blank=True)
    ed_presence_of_ai = models.BooleanField(default=False)
    ed_bully_action = models.TextField(
        choices=[
            ('exit', 'BigBuddy verbal reminders AND exclude from current session'),
            ('notice', 'BigBuddy verbal reminders for bad behavior'),
            ('ignore', 'No intervention')], default='exit')
    ed_victim_action = models.TextField(
        choices=[
            ('exit', 'BigBuddy verbal reminders, comfort child AND exclude bully from current session'),
            ('comfort', 'BigBuddy verbal notice AND comfort your child'),
            ('notice', 'BigBuddy verbal notice about bad behavior'),
            ('ignore', 'No intervention'), ], default='comfort')

    chat_daily_playtime = models.IntegerField(null=True, blank=True)
    chat_break_time = models.IntegerField(null=True, blank=True)
    chat_break_duration_time = models.IntegerField(null=True, blank=True)
    chat_presence_of_ai = models.BooleanField(default=False)
    chat_bully_action = models.TextField(
        choices=[
            ('exit', 'BigBuddy verbal reminders AND stop current chat'),
            ('notice', 'BigBuddy verbal reminders for bad behavior'),
            ('ignore', 'No intervention')], default='exit')
    chat_victim_action = models.TextField(
        choices=[
            ('exit', 'BigBuddy verbal notice, comfort your child AND stop current chat'),
            ('comfort', 'BigBuddy verbal notice AND comfort your child'),
            ('notice', 'BigBuddy verbal notice about bad behavior'),
            ('ignore', 'No intervention'), ], default='comfort')


class Textfile(models.Model):
    title = models.CharField(max_length=200)
    body = models.TextField()

    def __str__(self):
        return self.title


class TextfileURL(models.Model):
    textfile = models.ForeignKey(Textfile, related_name='urls', on_delete=models.CASCADE)
    paper = models.CharField(max_length=200)
    url = models.URLField()

    def __str__(self):
        return self.url


class GeneralSetting(models.Model):
    child = models.OneToOneField(Child, on_delete=models.CASCADE, related_name='general_setting')
    bad_words = models.TextField(null=True, blank=True)
    all_bad_words = models.BooleanField(default=True)
    bad_words_intervention = models.TextField(null=True, blank=True)
    urgent_notification = models.TextField(null=True, blank=True)
    what_notification = models.TextField(null=True, blank=True)
    daily_playtime = models.IntegerField(default=240)
    daily_playtime_start = models.TimeField(default='08:00:00')
    daily_playtime_end = models.TimeField(default='20:00:00')
    INTERVENTION_CHOICES = [
        ('verbal', 'verbal reminders and educate'),
        ('silence', 'silence bad words')
    ]

    def bad_words_measures_display(self):
        if not self.bad_words_intervention:
            return ""
        selected_interventions = self.bad_words_intervention.split(',')
        intervention_dict = dict(self.INTERVENTION_CHOICES)
        display_values = [intervention_dict.get(choice.strip(), choice.strip()) for choice in selected_interventions]
        return ', '.join(display_values)


class GameSetting(models.Model):
    child = models.OneToOneField(Child, on_delete=models.CASCADE, related_name='game_setting')
    game_daily_playtime = models.IntegerField(default=240)
    game_break_time = models.IntegerField(null=True, blank=True)
    game_break_duration_time = models.IntegerField(default=30)
    game_presence_of_ai = models.CharField(max_length=50, choices=[
        ('Always', 'Always'),
        ('bully', 'Only Appear when child is bullying'),
        ('victim', 'Only Appear when child is bullying victim'),
        ('urgent', 'Only Appear when bully OR victim situations')], default='Always')
    GAME_Bully_ACTION_CHOICES = [
            ('exit', 'BigBuddy verbal reminders, set points to 0 AND exclude from the game'),
            ('point', 'BigBuddy verbal reminders AND set points to 0'),
            ('notice', 'BigBuddy verbal reminders and educate for bad behavior'),
            ('ignore', 'No intervention')]
    game_bully_action = models.TextField(choices=GAME_Bully_ACTION_CHOICES, default='exit')
    GAME_Victim_ACTION_CHOICES = [
        ('comfort', 'BigBuddy verbal notice, set points to 0 AND comfort child'),
        ('point', 'BigBuddy verbal reminders AND set bully points to 0'),
        ('notice', 'BigBuddy verbal notice about bad behavior'),
        ('ignore', 'No intervention')]
    game_victim_action = models.TextField(choices=GAME_Victim_ACTION_CHOICES, default='comfort')
    def game_bully_action_display(self):
        return dict(GameSetting.GAME_Bully_ACTION_CHOICES)[self.game_bully_action]
    def game_victim_action_display(self):
        return dict(GameSetting.GAME_Victim_ACTION_CHOICES)[self.game_victim_action]

class EducationSetting(models.Model):
    child = models.OneToOneField(Child, on_delete=models.CASCADE, related_name='education_setting')
    edu_daily_playtime = models.IntegerField(default=240)
    edu_break_time = models.IntegerField(null=True, blank=True)
    edu_break_duration_time = models.IntegerField(default=30)
    edu_presence_of_ai = models.CharField(max_length=50, choices=[
        ('Always', 'Always'),
        ('bully', 'Only Appear when child is bullying'),
        ('victim', 'Only Appear when child is bullying victim'),
        ('urgent', 'Only Appear when bully OR victim situations')], default='Always')
    EDU_Bully_ACTION_CHOICES = [
            ('exit', 'BigBuddy verbal reminders AND exclude from current session'),
            ('notice', 'BigBuddy verbal reminders and educate for bad behavior'),
            ('ignore', 'No intervention')]
    edu_bully_action = models.TextField(choices=EDU_Bully_ACTION_CHOICES, default='exit')
    EDU_Victim_ACTION_CHOICES = [
            ('exit', 'BigBuddy verbal reminders, comfort child AND exclude bully from current session'),
            ('comfort', 'BigBuddy verbal notice AND comfort your child'),
            ('notice', 'BigBuddy verbal notice about bad behavior'),
            ('ignore', 'No intervention')]
    edu_victim_action = models.TextField(
        choices=EDU_Victim_ACTION_CHOICES, default='comfort')
    def edu_bully_action_display(self):
        return dict(EducationSetting.EDU_Bully_ACTION_CHOICES)[self.edu_bully_action]
    def edu_victim_action_display(self):
        return dict(EducationSetting.EDU_Victim_ACTION_CHOICES)[self.edu_victim_action]


class ChatSetting(models.Model):
    child = models.OneToOneField(Child, on_delete=models.CASCADE, related_name='chat_setting')
    chat_daily_playtime = models.IntegerField(default=240)
    chat_break_time = models.IntegerField(null=True, blank=True)
    chat_break_duration_time = models.IntegerField(default=30)
    chat_presence_of_ai = models.CharField(max_length=50, choices=[
        ('Always', 'Always'),
        ('bully', 'Only Appear when child is bullying'),
        ('victim', 'Only Appear when child is bullying victim'),
        ('urgent', 'Only Appear when bully OR victim situations')], default='Always')
    CHAT_Bully_ACTION_CHOICES = [
            ('exit', 'BigBuddy verbal reminders AND stop current chat'),
            ('notice', 'BigBuddy verbal reminders and educate for bad behavior'),
            ('ignore', 'No intervention')]
    chat_bully_action = models.TextField(choices=CHAT_Bully_ACTION_CHOICES, default='exit')
    CHAT_Victim_ACTION_CHOICES = [
            ('exit', 'BigBuddy verbal notice, comfort your child AND stop current chat'),
            ('comfort', 'BigBuddy verbal notice AND comfort your child'),
            ('notice', 'BigBuddy verbal notice about bad behavior'),
            ('ignore', 'No intervention'),]
    chat_victim_action = models.TextField(choices=CHAT_Victim_ACTION_CHOICES, default='comfort')
    who_can_chat = models.TextField(
        choices=[
            ('friend', 'Friends only'),
            ('everyone', 'Everyone')], default='everyone')
    def chat_bully_action_display(self):
        return dict(ChatSetting.CHAT_Bully_ACTION_CHOICES)[self.chat_bully_action]
    def chat_victim_action_display(self):
        return dict(ChatSetting.CHAT_Victim_ACTION_CHOICES)[self.chat_victim_action]


class SingleGameSetting(models.Model):
    child = models.OneToOneField(Child, on_delete=models.CASCADE, related_name='sgame_setting')
    sgame_daily_playtime = models.IntegerField(default=240)
    sgame_break_time = models.IntegerField(null=True, blank=True)
    sgame_break_duration_time = models.IntegerField(default=30)
    sgame_presence_of_ai = models.CharField(max_length=50, choices=[
        ('Always', 'Always'),
        ('sometimes', 'Only appear when child needs')], default='Always')


class FitnessSetting(models.Model):
    child = models.OneToOneField(Child, on_delete=models.CASCADE, related_name='fitness_setting')
    fitness_daily_playtime = models.IntegerField(default=240)
    fitness_break_time = models.IntegerField(null=True, blank=True)
    fitness_break_duration_time = models.IntegerField(default=30)
    fitness_presence_of_ai = models.CharField(max_length=50, choices=[
        ('Always', 'Always'),
        ('Hurt', 'Appear when child get hurt'),
        ('Need', 'Only Appear when child needs')], default='Always')


class ArtSetting(models.Model):
    child = models.OneToOneField(Child, on_delete=models.CASCADE, related_name='art_setting')
    art_daily_playtime = models.IntegerField(default=240)
    art_break_time = models.IntegerField(null=True, blank=True)
    art_break_duration_time = models.IntegerField(default=30)
    art_presence_of_ai = models.CharField(max_length=50, choices=[
        ('Always', 'Always'),
        ('Need', 'Only Appear when child needs')], default='Always')
