from django.db import models


class Participant(models.Model):
    '''Модель участников мероприятия, представляющая разные типы участников'''
    name = models.CharField('Имя участника', max_length=50)
    subscriber = models.BooleanField('Подписчик', default=False, null=True, blank=True)
    organizer = models.BooleanField('Организатор', default=False, null=True, blank=True)
    speaker = models.BooleanField('Докладчик', default=False, null=True, blank=True)
    tg_id = models.BigIntegerField(unique=True)

    def __str__(self):
        return f'{self.name}'


class Place(models.Model):
    '''Модель места проведения мероприятий, представляющая различные типы мест'''
    name = models.CharField('Место проведения', max_length=50)

    def __str__(self):
        return f'{self.place}'


class Event(models.Model):
    '''Модель мероприятия, представляет различные мероприятия и их свойства'''
    name = models.CharField(
        'Название мероприятия'
    )
    speaker = models.ForeignKey(
        Participant,
        on_delete=models.SET_NULL,
        verbose_name='Докладчик',
        related_name='events',
        blank=True,
        null=True,
    )
    place = models.ForeignKey(
        Place,
        on_delete=models.SET_NULL,
        verbose_name='Место проведения',
        related_name='events',
        null=True
    )
    start = models.DateTimeField('Дата начала')
    finish = models.DateTimeField('Дата оконания')

    def __str__(self):
        return f'{self.name} {self.start} {self.finish}'


class Question(models.Model):
    '''Модель вопроса, представляет информацию о заданном вопросе'''
    author = models.ForeignKey(
        Participant,
        on_delete=models.SET_NULL,
        verbose_name='Автор вопроса',
        related_name='questions',
        null=True
    )
    question = models.CharField('Вопрос', max_length=200)
    event = models.ForeignKey(
        Event,
        on_delete=models.SET_NULL,
        verbose_name='Доклад',
        related_name='questions',
        null=True
    )
    tg_chat_id = models.BigIntegerField(null=True)


class Donat(models.Model):
    '''Модель пожератования, представляет информацию о пожертвовании'''
    donater = models.ForeignKey(
        Participant,
        on_delete=models.SET_NULL,
        verbose_name='Автор пожертвования',
        related_name='donats',
        null=True
    )
    size = models.DecimalField(max_digits=10, decimal_places=2)