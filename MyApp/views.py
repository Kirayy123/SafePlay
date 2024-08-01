import json
import random
from datetime import datetime, timedelta
from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.core.serializers.json import DjangoJSONEncoder
from django.core.validators import validate_email
from django.db.models import Q, Sum, F, ExpressionWrapper, DurationField
from django.db.models.functions import TruncHour
from django.http import HttpResponseRedirect, JsonResponse, HttpResponseNotFound
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.utils.timezone import make_aware, now
from openai import OpenAI

from MyApp.form import LoginForm, RegisterForm, ChildForm, GeneralSettingForm, GameSettingForm, \
    EducationSettingForm, ChatSettingForm, SingleGameSettingForm, ArtSettingForm, FitnessSettingForm, BullyProcessForm, \
    VictimProcessForm, MyAccountForm
from MyApp.models import Child, GameSession, Message, Notification, Textfile, GeneralSetting, GameSetting, \
    EducationSetting, ChatSetting, SingleGameSetting, ArtSetting, FitnessSetting


def login_register(request):
    action = request.POST.get('action', 'login')
    register_active = action == 'register'
    login_active = action == 'login'

    login_form = LoginForm(None, prefix='login')
    register_form = RegisterForm(request.POST if register_active else None, prefix='register')

    if request.method == 'POST':
        if login_active:
            register_active = False
            login_form = LoginForm(request.POST)
            if login_form.is_valid():
                login_input = login_form.cleaned_data['login']
                password = login_form.cleaned_data['password']
                try:
                    validate_email(login_input)
                    is_email = True
                except ValidationError:
                    is_email = False
                if is_email:
                    user = User.objects.filter(email=login_input).first()
                else:
                    user = User.objects.filter(username=login_input).first()

                if user is not None and user.check_password(password):
                    login(request, user)
                    return redirect(reverse('childselect'))
                else:
                    messages.error(request, "Invalid login credentials.")
        if register_active:
            login_active = False
            login_form = LoginForm(None)
            if register_form.is_valid():
                user = register_form.save(commit=False)
                user.set_password(user.password)
                user.save()
                login(request, user)
                return redirect(reverse('childselect'))

    context = {
        'login_form': login_form,
        'register_form': register_form,
        'register_active': register_active,
        'login_active': login_active
    }
    return render(request, 'Login/login_register.html', context)


@login_required
def user_logout(request):
    logout(request)
    return redirect(reverse('login_register'))


@login_required
def child_selection(request):
    parent = request.user
    children = parent.children.all()

    time_limit = now() - timedelta(hours=4)
    Notification.objects.filter(
        Q(child__parent=parent), Q(type__in=[1, 2, 4]), processed=False, time__lte=time_limit
    ).update(processed=True)

    urgent_notification = Notification.objects.none()

    for child in children:
        notification = child.notifications.filter(Q(type=1) | Q(type=2) | Q(type=4), processed=False).order_by('-time')
        if notification.exists():
            urgent_notification = urgent_notification | notification

    urgent_notification = urgent_notification.order_by('-time')

    context = {'children': children, 'urgent_notification': urgent_notification}

    if children.exists():
        return render(request, 'Child/SelectChild.html', context)
    else:
        return redirect('addchild')


def fetch_urgent_notifications(request):
    parent = request.user
    children = parent.children.all()
    urgent_notification = Notification.objects.none()

    for child in children:
        notification = child.notifications.filter(Q(type=1) | Q(type=2) | Q(type=4), processed=False).order_by('-time')
        if notification.exists():
            urgent_notification = urgent_notification | notification

    urgent_notification = urgent_notification.order_by('-time')

    data = [{
        'id': n.id,
        'child_name': n.child.name,
        'time': n.time.strftime("%Y-%m-%d %H:%M"),
        'type': n.type,
        'text': n.text,
        'processed': n.processed
    } for n in urgent_notification]

    return JsonResponse(data, safe=False)


@login_required
def add_child(request):
    if request.method == 'POST':
        form = ChildForm(request.POST)
        if form.is_valid():
            child = form.save(commit=False)
            child.parent = request.user
            child.save()
            return redirect('childselect')
    else:
        form = ChildForm()

    return render(request, 'Child/AddChild.html', context={'form': form})


@login_required
def my_account(request):
    user = request.user
    next_page = request.GET.get('next', '')
    if request.method == 'POST':
        form = MyAccountForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            if next_page:
                return HttpResponseRedirect(next_page)
            return redirect('childselect')
    else:
        form = MyAccountForm(instance=user)

    context = {'form': form, 'next': next_page}
    return render(request, 'Child/MyAccount.html', context)


@login_required
def Notifications(request, child_id=None):
    child = get_object_or_404(Child, pk=child_id, parent=request.user)
    notification_type = request.GET.get('type', None)

    all_notifications = child.notifications.all().order_by('-time')

    time_limit = now() - timedelta(hours=0.1)
    notifications = all_notifications.filter(time__gte=time_limit)  # today's notification

    if notifications.exists():
        first_notification = notifications.first()
        if hasattr(first_notification, 'game_url'):
            gameurl = first_notification.game_url
        else:
            gameurl = None
    else:
        gameurl = None
    # # filter by type
    # if notification_type is not None:
    #     notification_type = int(notification_type)
    #     if notification_type == 6:  # filter all
    #         notifications_by_type = all_notifications
    #     elif notification_type == 1 or notification_type == 2 or notification_type == 4 or notification_type == 5:
    #         notifications_by_type = all_notifications.filter(type__in=[1, 2, 4, 5]).order_by('-time')
    #     elif notification_type == 0:
    #         notifications_by_type = all_notifications.filter(type__in=[0, 3]).order_by('-time')
    #     else:
    #         notifications_by_type = all_notifications.filter(type=notification_type).order_by('-time')
    # else:
    #     notifications_by_type = all_notifications

    context = {
        'child_id': child_id,
        'notifications': notifications,
        'current_type': notification_type,
        'gameurl': gameurl
    }
    return render(request, 'App/Notification.html', context)


@login_required
def fetch_notifications(request, child_id):
    child = get_object_or_404(Child, pk=child_id, parent=request.user)
    all_notifications = child.notifications.all().order_by('-time')
    notifications = all_notifications.filter(time__gte=now() - timedelta(hours=0.1))  # today's notification

    if notifications.exists():
        first_notification = notifications.first()
        if hasattr(first_notification, 'game_url'):
            gameurl = first_notification.game_url
        else:
            gameurl = None
    else:
        gameurl = None

    time_limit = now() - timedelta(hours=4)
    notifications_to_process = notifications.filter(
        processed_measures='1' or None, time__lte=time_limit
    )

    for notification in notifications_to_process:
        action = ''
        if notification.game_type == 0:  # MultiPlayerGame
            settings = notification.child.game_setting
            if notification.type == 2:
                action = settings.game_bully_action_display()
            elif notification.type == 1:
                action = settings.game_victim_action_display()
        elif notification.game_type == 2:  # Education
            settings = notification.child.education_setting
            if notification.type == 2:
                action = settings.edu_bully_action_display()
            elif notification.type == 1:
                action = settings.edu_victim_action_display()
        elif notification.game_type == 5:  # Chat
            settings = notification.child.chat_setting
            if notification.type == 2:
                action = settings.chat_bully_action_display()
            elif notification.type == 1:
                action = settings.chat_victim_action_display()

        if notification.type == 4:  # Bad word
            settings = notification.child.general_setting
            action = settings.bad_words_measures_display()

        # Update processed measures and mark as processed
        notification.processed_measures = action
        notification.processed = True
        notification.save()

    notifications_data = [{
        'name': notification.child.name,
        'time': notification.time.strftime("%Y-%m-%d %H:%M"),
        'type': notification.type,
        'text': notification.text,
        'processed': notification.processed,
        'processed_measures': notification.processed_measures,
        'game_url': notification.game_url,
        'id': notification.id,
    } for notification in notifications]
    return JsonResponse({'notifications': notifications_data, 'gameurl': gameurl})


@login_required
def Urgent_process(request, notification_id, fromtag):
    try:
        notification = Notification.objects.get(pk=notification_id)
    except Notification.DoesNotExist:
        return HttpResponseNotFound('<h1>Notification not found</h1>')

    child_id = notification.child_id

    if request.method == 'POST':
        if notification.type == 2:  # Bully
            form = BullyProcessForm(request.POST, instance=notification)
        else:  # Victim
            form = VictimProcessForm(request.POST, instance=notification)

        if form.is_valid():
            notification = form.save(commit=False)
            selected_measures = form.cleaned_data.get(
                'bmeasurement_choices' if notification.type == 2 else 'vmeasurement_choices', [])
            notification.processed_measures = ', '.join(selected_measures)
            notification.processed = True
            notification.save()
            if fromtag == 0:
                return redirect('childselect')
            elif fromtag == 1:
                return redirect('notification', child_id)
    else:
        if notification.type == 2:
            form = BullyProcessForm(instance=notification)
        else:
            form = VictimProcessForm(instance=notification)

    context = {
        'form': form,
        'notification': notification,
        'child_id': child_id,
        'texts': Textfile.objects.prefetch_related('urls').filter(title__in=[
            'What is Bully?', 'Impact of Bully.', 'Bully in Games.', 'What parents should do with Bully?',
        ]),
        'fromtag': fromtag
    }
    return render(request, 'App/UrgentProcess.html', context)


@login_required
def History(request, child_id=None):
    child = Child.objects.get(pk=child_id, parent=request.user)
    gamesessions = child.game_sessions.all().order_by('-start_time')

    filter_date = request.GET.get('date')
    if filter_date:
        datetime_obj = make_aware(datetime.strptime(filter_date, '%Y-%m-%d'))
        gamesessions = gamesessions.filter(start_time__date=datetime_obj.date())

    for gamesession in gamesessions:
        gamesession.stars = range(gamesession.satisfaction)
        gamesession.non_stars = range(5 - gamesession.satisfaction)
        duration_timedelta = gamesession.end_time - gamesession.start_time
        total_minutes = duration_timedelta.total_seconds() / 60
        hours, minutes = divmod(total_minutes, 60)
        gamesession.durations = "{} hours {} minutes".format(int(hours), int(minutes))

    context = {'child_id': child_id, 'gamesessions': gamesessions}
    return render(request, 'App/History.html', context)


@login_required
def History_detail(request, gamesession_id=None):
    gamesession = GameSession.objects.get(pk=gamesession_id)
    child_id = gamesession.child_id
    stars = gamesession.satisfaction
    non_stars = 5 - gamesession.satisfaction
    context = {'child_id': child_id, 'gamesession': gamesession, 'stars': range(stars), 'non_stars': range(non_stars)}
    return render(request, 'App/History_detail.html', context)


@login_required
def Setup(request, child_id=None):
    child = get_object_or_404(Child, pk=child_id)

    # Create or get instances of settings
    general_setting, _ = GeneralSetting.objects.get_or_create(child=child)
    game_setting, _ = GameSetting.objects.get_or_create(child=child)
    education_setting, _ = EducationSetting.objects.get_or_create(child=child)
    chat_setting, _ = ChatSetting.objects.get_or_create(child=child)
    sgame_setting, _ = SingleGameSetting.objects.get_or_create(child=child)
    art_setting, _ = ArtSetting.objects.get_or_create(child=child)
    fitness_setting, _ = FitnessSetting.objects.get_or_create(child=child)

    if request.method == 'POST':
        general_form = GeneralSettingForm(request.POST, instance=general_setting)
        game_form = GameSettingForm(request.POST, instance=game_setting)
        education_form = EducationSettingForm(request.POST, instance=education_setting)
        chat_form = ChatSettingForm(request.POST, instance=chat_setting)
        sgame_form = SingleGameSettingForm(request.POST, instance=sgame_setting)
        art_form = ArtSettingForm(request.POST, instance=art_setting)
        fitness_form = FitnessSettingForm(request.POST, instance=fitness_setting)

        if all([general_form.is_valid(), game_form.is_valid(), education_form.is_valid(),
                chat_form.is_valid(), sgame_form.is_valid(), fitness_form.is_valid(),
                art_form.is_valid()]):
            general_setting = general_form.save(commit=False)
            selected_bad_words = general_form.cleaned_data['bad_words_choices']
            custom_bad_words = general_form.cleaned_data['custom_bad_words'].strip()
            if custom_bad_words:
                combined_bad_words = ', '.join(selected_bad_words + [custom_bad_words])
            else:
                combined_bad_words = ', '.join(selected_bad_words)

            general_setting.bad_words = combined_bad_words

            selected_intervention_methods = general_form.cleaned_data['bad_words_intervention']
            general_setting.bad_words_intervention = ', '.join(selected_intervention_methods)
            selected_urgent_notification = general_form.cleaned_data['urgent_notification']
            general_setting.urgent_notification = ', '.join(selected_urgent_notification)
            selected_what_notification = general_form.cleaned_data['what_notification']
            general_setting.what_notification = ', '.join(selected_what_notification)

            general_setting.save()

            game_form.save()
            education_form.save()
            chat_form.save()
            sgame_form.save()
            art_form.save()
            fitness_form.save()
            return redirect(reverse('setting', args=[child_id]))

    else:
        general_form = GeneralSettingForm(instance=general_setting)
        game_form = GameSettingForm(instance=game_setting)
        education_form = EducationSettingForm(instance=education_setting)
        chat_form = ChatSettingForm(instance=chat_setting)
        sgame_form = SingleGameSettingForm(instance=sgame_setting)
        art_form = ArtSettingForm(instance=art_setting)
        fitness_form = FitnessSettingForm(instance=fitness_setting)

    context = {
        'general_form': general_form,
        'game_form': game_form,
        'education_form': education_form,
        'chat_form': chat_form,
        'sgame_form': sgame_form,
        'art_form': art_form,
        'fitness_form': fitness_form,
        'child_id': child_id,
    }
    return render(request, 'App/Setting.html', context)


@login_required
def Communication(request, child_id=None):
    child = get_object_or_404(Child, pk=child_id)
    if request.method == 'POST':
        message_text = request.POST.get('message', '').strip()
        if message_text:
            Message.objects.create(child=child, text=message_text, tag=0)
            return redirect('communication', child_id=child_id)
    messages = Message.objects.filter(child=child).order_by('-time')[:6]
    messages = sorted(messages, key=lambda m: m.time)
    context = {
        'child_id': child_id,
        'messages': messages,
    }
    return render(request, 'App/Communication.html', context)


def fetch_messages(request, child_id):
    child = get_object_or_404(Child, pk=child_id)
    messages = Message.objects.filter(child=child).order_by('-time')[:6]
    messages = sorted(messages, key=lambda m: m.time)
    messages_data = [{'text': message.text, 'time': message.time.strftime("%Y-%m-%d %H:%M"), 'tag': message.tag} for
                     message in messages]
    return JsonResponse({'messages': messages_data})


def fetch_history(request, child_id):
    child = get_object_or_404(Child, pk=child_id)
    date = request.GET.get('date')
    if date:
        messages = Message.objects.filter(child=child, time__date=date).order_by('time')
    else:
        messages = Message.objects.filter(child=child).order_by('-time')
    messages_data = [{'text': message.text, 'time': message.time.strftime("%Y-%m-%d %H:%M"), 'tag': message.tag} for
                     message in messages]
    return JsonResponse({'messages': messages_data})


@login_required
def Report(request, child_id):
    child = get_object_or_404(Child, pk=child_id)
    today_min = now().replace(hour=0, minute=0, second=0, microsecond=0)
    today_max = today_min + timedelta(days=1)

    # Calculate hourly sessions for the daily chart
    hourly_sessions = GameSession.objects.filter(
        child=child, start_time__range=(today_min, today_max)
    ).annotate(
        hour=TruncHour('start_time')
    ).values('hour', 'game_name', 'start_time', 'end_time').annotate(
        session_duration=ExpressionWrapper(
            F('end_time') - F('start_time'),
            output_field=DurationField()
        )
    ).order_by('hour')

    daily_chart_data = prepare_daily_data(hourly_sessions)
    weekly_chart_data = prepare_weekly_data(child)
    weekly_game_times_stacked = get_weekly_game_time_stacked_data(child)

    # Calculate daily and weekly Bully and Bullying victim counts
    daily_bully_count = Notification.objects.filter(
        child=child, type=2, time__range=(today_min, today_max)
    ).count()
    daily_victim_count = Notification.objects.filter(
        child=child, type=1, time__range=(today_min, today_max)
    ).count()

    week_min = today_min - timedelta(days=6)
    weekly_bully_count = Notification.objects.filter(
        child=child, type=2, time__range=(week_min, today_max)
    ).count()
    weekly_victim_count = Notification.objects.filter(
        child=child, type=1, time__range=(week_min, today_max)
    ).count()

    bully_notifications_daily = Notification.objects.filter(child=child, type=2, time__range=(today_min, today_max))
    victim_notifications_daily = Notification.objects.filter(child=child, type=1, time__range=(today_min, today_max))
    bully_notifications_weekly = Notification.objects.filter(child=child, type=2, time__range=(week_min, today_max))
    victim_notifications_weekly = Notification.objects.filter(child=child, type=1, time__range=(week_min, today_max))

    victimtext = Textfile.objects.filter(title='victimtext').first()
    bullytext = Textfile.objects.filter(title='bullytext').first()

    context = {
        'child_id': child_id,
        'daily_chart_data': json.dumps(daily_chart_data, cls=DjangoJSONEncoder),
        'weekly_chart_data': json.dumps(weekly_chart_data, cls=DjangoJSONEncoder),
        'weekly_game_times_stacked': json.dumps(weekly_game_times_stacked, cls=DjangoJSONEncoder),
        'daily_bully_count': daily_bully_count,
        'daily_victim_count': daily_victim_count,
        'weekly_bully_count': weekly_bully_count,
        'weekly_victim_count': weekly_victim_count,
        'bully_notifications_daily': bully_notifications_daily,
        'victim_notifications_daily': victim_notifications_daily,
        'bully_notifications_weekly': bully_notifications_weekly,
        'victim_notifications_weekly': victim_notifications_weekly,
        'bullytext': bullytext,
        'victimtext': victimtext,
    }
    return render(request, 'App/Report.html', context)


def prepare_daily_data(hourly_sessions):
    games = set(session['game_name'] for session in hourly_sessions)

    # Initialize 24-hour labels and dataset
    data = {'labels': [f'{i:02}:00' for i in range(24)], 'datasets': {}, 'tooltipData': {}}

    # Initialize the tooltip data structure for each hour and each game
    for hour in data['labels']:
        data['tooltipData'][hour] = {game: [] for game in games}

    # Initialize the dataset for each game
    for game in games:
        data['datasets'][game] = [0] * 24  # Initialize each hour to 0

    # Session Process
    for session in hourly_sessions:
        hour_index = session['hour'].hour  # Get hour as index
        hour_label = f"{hour_index:02}:00"
        game_name = session['game_name']
        duration = session['session_duration'].total_seconds() / 60  # Convert to min
        start_time = session['start_time'].strftime('%H:%M')
        end_time = session['end_time'].strftime('%H:%M')

        # Add game times
        data['datasets'][game_name][hour_index] += duration
        data['tooltipData'][hour_label][game_name].append(f"{start_time} - {end_time}")

    # Construct an array of datasets, one for each game
    datasets = []
    for game, durations in data['datasets'].items():
        datasets.append({
            'label': game,
            'data': durations,
            'backgroundColor': generate_random_color(),
            'stack': 'GameStack'
        })

    return {'labels': data['labels'], 'datasets': datasets, 'tooltipData': data['tooltipData']}


def generate_random_color():
    r = random.randint(0, 255)
    g = random.randint(0, 255)
    b = random.randint(0, 255)
    return f'rgba({r}, {g}, {b}, 0.2)'


def prepare_weekly_data(child):
    weekly_data = {}
    labels = []
    today = datetime.now().date()  # Corrected to just datetime
    days = [(today - timedelta(days=i)).strftime('%a') for i in range(6, -1, -1)]  # Corrected to just timedelta

    for i, day_name in enumerate(days):
        day = today - timedelta(days=6 - i)  # Corrected to just timedelta
        sessions_on_day = GameSession.objects.filter(
            child=child,
            start_time__date=day
        ).annotate(
            duration=ExpressionWrapper(
                F('end_time') - F('start_time'),
                output_field=DurationField()
            )
        )

        duration = sessions_on_day.aggregate(
            total_duration=Sum('duration')
        )

        # Safely get the sum or default to 0 if None, convert to minutes
        total_duration = duration.get('total_duration')
        total_minutes = total_duration.total_seconds() / 60 if total_duration else 0
        weekly_data[day_name] = total_minutes
        labels.append(day_name)

    # Format data for Chart.js
    values = [weekly_data[day] for day in days]
    datasets = [{
        'label': "Weekly Game Time",
        'data': values,
        'backgroundColor': generate_random_color(),
        'fill': False,
    }]

    return {'labels': labels, 'datasets': datasets}


def get_weekly_game_time_stacked_data(child):
    today_min = now().replace(hour=0, minute=0, second=0, microsecond=0)
    today_max = today_min + timedelta(days=1)
    week_min = today_min - timedelta(days=6)

    game_times = GameSession.objects.filter(
        child=child,
        start_time__date__range=[week_min, today_max]
    ).values('game_name').annotate(
        total_time=Sum(ExpressionWrapper(F('end_time') - F('start_time'), output_field=DurationField()))
    ).order_by('-total_time')

    datasets = []
    for game in game_times:
        total_minutes = game['total_time'].total_seconds() / 60 if game['total_time'] else 0
        datasets.append({
            'label': game['game_name'],
            'data': [total_minutes],
            'backgroundColor': generate_random_color(),
        })

    return {'labels': ["Game Time (each)"], 'datasets': datasets}


def AIinfo(request, child_id, fromtag):
    texts = Textfile.objects.prefetch_related('urls').filter(title__in=[
        'What is Bully?', 'Impact of Bully.', 'Bully in Games.',
        'What parents should do with Bully?',
    ])

    if request.method == 'POST':
        user_question = request.POST.get('userQuery')
        # client = OpenAI(
        #     api_key="sk-x9XIbhuccUypiLMq3mqfCiBqnV0bExnkwUkz3eRxABfLhzd",
        #     base_url="https://api.chatanywhere.cn/v1"
        # )
        client = OpenAI(api_key="sk-proj-XUrICV4CQdnOUA9xb636T3BlbkFJM1XukZRieCo69xQn7DNQ")
        completion = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "user", "content": user_question},
            ],
        )
        respond = completion.choices[0].message.content
        return JsonResponse({'respond': respond})

    context = {
        'child_id': child_id,
        'fromtag': fromtag,
        'texts': texts
    }
    return render(request, 'App/AIinfo.html', context)


def Paper(request, link_id):
    if link_id == 1:
        return HttpResponseRedirect(
            'https://dl.acm.org/doi/pdf/10.1145/3585088.3589374?casa_token=7tk8k9U-bpAAAAAA:OD4vgezDoFTm8K06BSpef0Mbxn_VyqrkxZT1_pSCC9eyWIWiiOwy7okq0WW-nd-AtySXgdqB0Hb1-g')
    elif link_id == 2:
        return HttpResponseRedirect('https://dl.acm.org/doi/10.1145/3544549.3585840')


# ______________________________________________________________________________TEST
def ChatGPT_TRY(request, child_id):
    if request.method == 'POST':
        user_question = request.POST.get('userQuery')
        client = OpenAI(
            api_key="sk-x9XIbhuccUypiLMq3mqfCiyBqnV0bExnkwUkz3eRxABfLhzd",
            base_url="https://api.chatanywhere.cn/v1"
        )
        completion = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "user",
                 "content": user_question},
            ],
        )
        respond = completion.choices[0].message.content

        context = {'child_id': child_id,
                   'user_question': user_question,
                   'respond': respond}
        return render(request, 'App/ChatGPT_TRY.html', context)

    return render(request, 'App/ChatGPT_TRY.html', {'child_id': child_id})
