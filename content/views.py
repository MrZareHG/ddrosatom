from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Count, Q
from django.core.paginator import Paginator
from django.utils import timezone
from datetime import datetime, timedelta

from .models import News, Event, KnowledgeBase, Comment, EventParticipation, ContentView, ContentLike
from .forms import NewsForm, EventForm, KnowledgeBaseForm, CommentForm, EventParticipationForm
from .services import ContentService


def home(request):
    """Главная страница"""
    return render(request, 'content/home.html')


def news_list(request):
    """Список новостей"""
    news_list = News.objects.filter(status='published', published_at__lte=timezone.now())

    # Фильтрация
    city = request.GET.get('city')
    search = request.GET.get('search')

    if city:
        news_list = news_list.filter(city=city)
    if search:
        news_list = news_list.filter(
            Q(title__icontains=search) |
            Q(content__icontains=search) |
            Q(excerpt__icontains=search)
        )

    # Пагинация
    paginator = Paginator(news_list, 10)
    page_number = request.GET.get('page')
    news = paginator.get_page(page_number)

    context = {
        'news': news,
        'search_query': search,
        'selected_city': city,
    }
    return render(request, 'content/news_list.html', context)


def news_detail(request, slug):
    """Детальная страница новости"""
    news = get_object_or_404(News, slug=slug, status='published')

    # Увеличиваем счетчик просмотров
    ContentService.record_view(news, request)

    # Комментарии
    comments = news.comments.filter(is_approved=True, parent__isnull=True)

    # Форма комментария
    if request.method == 'POST' and request.user.is_authenticated:
        comment_form = CommentForm(request.POST)
        if comment_form.is_valid():
            comment = comment_form.save(commit=False)
            comment.author = request.user
            comment.content_object = news
            comment.save()
            messages.success(request, 'Комментарий добавлен')
            return redirect('content:news_detail', slug=slug)
    else:
        comment_form = CommentForm()

    context = {
        'news': news,
        'comments': comments,
        'comment_form': comment_form,
    }
    return render(request, 'content/news_detail.html', context)


def event_list(request):
    """Список мероприятий"""
    events = Event.objects.filter(status='published')

    # Фильтрация
    city = request.GET.get('city')
    event_type = request.GET.get('event_type')
    timeframe = request.GET.get('timeframe', 'upcoming')

    if city:
        events = events.filter(city=city)
    if event_type:
        events = events.filter(event_type=event_type)

    # Фильтр по времени
    now = timezone.now()
    if timeframe == 'upcoming':
        events = events.filter(start_date__gte=now)
    elif timeframe == 'past':
        events = events.filter(end_date__lt=now)
    elif timeframe == 'ongoing':
        events = events.filter(start_date__lte=now, end_date__gte=now)

    events = events.order_by('start_date')

    context = {
        'events': events,
        'selected_city': city,
        'selected_event_type': event_type,
        'selected_timeframe': timeframe,
        'event_types': Event.EVENT_TYPE_CHOICES,
    }
    return render(request, 'content/event_list.html', context)


def event_detail(request, pk):
    """Детальная страница мероприятия"""
    event = get_object_or_404(Event, pk=pk, status='published')

    # Увеличиваем счетчик просмотров
    ContentService.record_view(event, request)

    # Проверяем участие пользователя
    user_participation = None
    if request.user.is_authenticated:
        try:
            user_participation = EventParticipation.objects.get(user=request.user, event=event)
        except EventParticipation.DoesNotExist:
            pass

    # Участники
    participants = event.eventparticipation_set.filter(status__in=['registered', 'confirmed', 'attended'])

    # Форма регистрации
    if request.method == 'POST' and request.user.is_authenticated:
        participation_form = EventParticipationForm(request.POST)
        if participation_form.is_valid():
            if not user_participation:
                participation = participation_form.save(commit=False)
                participation.user = request.user
                participation.event = event
                participation.save()

                # Увеличиваем счетчик участников
                event.current_participants += 1
                event.save()

                messages.success(request, 'Вы успешно зарегистрировались на мероприятие!')
                return redirect('content:event_detail', pk=pk)
            else:
                messages.warning(request, 'Вы уже зарегистрированы на это мероприятие')
    else:
        participation_form = EventParticipationForm()

    context = {
        'event': event,
        'user_participation': user_participation,
        'participants': participants,
        'participation_form': participation_form,
    }
    return render(request, 'content/event_detail.html', context)


@login_required
def event_register(request, pk):
    """Регистрация на мероприятие"""
    event = get_object_or_404(Event, pk=pk, status='published')

    # Проверяем возможность регистрации
    if not event.is_registration_open:
        messages.error(request, 'Регистрация на это мероприятие закрыта')
        return redirect('content:event_detail', pk=pk)

    if not event.has_free_slots:
        messages.error(request, 'На это мероприятие нет свободных мест')
        return redirect('content:event_detail', pk=pk)

    # Проверяем, не зарегистрирован ли уже
    if EventParticipation.objects.filter(user=request.user, event=event).exists():
        messages.warning(request, 'Вы уже зарегистрированы на это мероприятие')
        return redirect('content:event_detail', pk=pk)

    # Регистрируем
    participation = EventParticipation.objects.create(
        user=request.user,
        event=event,
        status='registered'
    )

    # Увеличиваем счетчик участников
    event.current_participants += 1
    event.save()

    messages.success(request, 'Вы успешно зарегистрировались на мероприятие!')
    return redirect('content:event_detail', pk=pk)


def knowledge_base_list(request):
    """Список материалов базы знаний"""
    materials = KnowledgeBase.objects.filter(is_public=True)

    # Фильтрация
    category = request.GET.get('category')
    difficulty = request.GET.get('difficulty')
    search = request.GET.get('search')

    if category:
        materials = materials.filter(category=category)
    if difficulty:
        materials = materials.filter(difficulty_level=difficulty)
    if search:
        materials = materials.filter(
            Q(title__icontains=search) |
            Q(content__icontains=search) |
            Q(excerpt__icontains=search)
        )

    materials = materials.order_by('-created_at')

    context = {
        'materials': materials,
        'categories': KnowledgeBase.CATEGORY_CHOICES,
        'difficulty_levels': KnowledgeBase._meta.get_field('difficulty_level').choices,
        'selected_category': category,
        'selected_difficulty': difficulty,
        'search_query': search,
    }
    return render(request, 'content/knowledge_base_list.html', context)


def knowledge_base_detail(request, pk):
    """Детальная страница материала базы знаний"""
    material = get_object_or_404(KnowledgeBase, pk=pk, is_public=True)

    # Увеличиваем счетчик просмотров
    ContentService.record_view(material, request)

    # Увеличиваем счетчик скачиваний если запрошен файл
    if 'download' in request.GET and material.attached_file:
        material.download_count += 1
        material.save()

    context = {
        'material': material,
    }
    return render(request, 'content/knowledge_base_detail.html', context)


def calendar_view(request):
    """Страница календаря мероприятий"""
    year = request.GET.get('year')
    month = request.GET.get('month')

    if year and month:
        try:
            selected_date = datetime(int(year), int(month), 1)
        except ValueError:
            selected_date = timezone.now()
    else:
        selected_date = timezone.now()

    # Получаем события для выбранного месяца
    start_of_month = selected_date.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    end_of_month = (start_of_month + timedelta(days=32)).replace(day=1) - timedelta(days=1)

    events = Event.objects.filter(
        status='published',
        start_date__gte=start_of_month,
        start_date__lte=end_of_month
    ).order_by('start_date')

    # Формируем календарь
    calendar_data = ContentService.get_calendar_data(selected_date, events)

    context = {
        'calendar_data': calendar_data,
        'selected_date': selected_date,
        'events': events,
    }
    return render(request, 'content/calendar.html', context)


@login_required
def like_content(request, content_type, object_id):
    """Лайк контента"""
    from django.contrib.contenttypes.models import ContentType

    try:
        ct = ContentType.objects.get(model=content_type)
        content_object = ct.get_object_for_this_type(pk=object_id)

        # Проверяем, не лайкал ли уже
        like, created = ContentLike.objects.get_or_create(
            content_type=ct,
            object_id=object_id,
            user=request.user
        )

        if created:
            messages.success(request, 'Лайк добавлен!')
        else:
            like.delete()
            messages.info(request, 'Лайк удален!')

    except Exception as e:
        messages.error(request, 'Ошибка при добавлении лайка')

    # Возвращаем на предыдущую страницу
    return redirect(request.META.get('HTTP_REFERER', 'content:home'))