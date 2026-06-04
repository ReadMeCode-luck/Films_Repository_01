from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.text import slugify
from django.utils.safestring import mark_safe

COUNTRY_CHOICES = [
    ('Германия', 'Германия'),
    ('Китай', 'Китай'),
    ('Италия', 'Италия'),
    ('Великобритания', 'Великобритания'),
    ('Индия', 'Индия'),
    ('Испания', 'Испания'),
    ('Япония', 'Япония'),
    ('Франция', 'Франция'),
    ('Турция', 'Турция'),
    ('Греция', 'Греция'),
    ('Россия', 'Россия'),
    ('США', 'США'),
    ('Канада', 'Канада'),
    ('Казахстан', 'Казахстан'),
    ('Южная Корея', 'Южная Корея'),
    ('Нигерия', 'Нигерия'),
]


class Film(models.Model):
    QUALITY_CHOICES = [
        ('HD', 'HD'),
        ('Full HD', 'Full HD'),
        ('4K', '4K'),
        ('CAM', 'CAM'),
    ]

    AGE_RATING_CHOICES = [
        ('0+', '0+'), ('6+', '6+'), ('12+', '12+'), ('16+', '16+'), ('18+', '18+'),
    ]

    title       = models.CharField(max_length=200, verbose_name='Название')
    age_rating  = models.CharField(
        max_length=5, choices=AGE_RATING_CHOICES,
        default='0+', verbose_name='Возрастной рейтинг'
    )
    year        = models.IntegerField(
        verbose_name='Год',
        validators=[MinValueValidator(1895), MaxValueValidator(2026)]
    )
    genre       = models.CharField(
        max_length=100, verbose_name='Жанр',
        blank=True, default=''
    )
    country     = models.CharField(
        max_length=100, verbose_name='Страна',
        choices=COUNTRY_CHOICES, blank=True, default=''
    )
    description = models.TextField(verbose_name='Описание', blank=True)
    rating      = models.DecimalField(
        max_digits=3, decimal_places=1,
        verbose_name='Рейтинг', default=0.0,
        help_text='От 0.0 до 10.0'
    )
    duration    = models.PositiveIntegerField(
        verbose_name='Длительность (мин)', default=0
    )
    quality     = models.CharField(
        max_length=20, choices=QUALITY_CHOICES,
        default='HD', verbose_name='Качество'
    )
    price       = models.FloatField(verbose_name='Цена', default=0)
    poster      = models.ImageField(
        upload_to='posters/', verbose_name='Постер',
        blank=True, null=True
    )
    is_featured = models.BooleanField(default=False, verbose_name='Показывать на главной')
    is_cartoon  = models.BooleanField(default=False, verbose_name='Мультфильм')

    slug = models.SlugField(
        max_length=220, unique=True,
        null=True, blank=True,
        verbose_name='Slug (URL)',
        allow_unicode=True,
    )

    class Meta:
        verbose_name = 'Фильм'
        verbose_name_plural = 'Фильмы'
        ordering = ['-rating']

    def __str__(self):
        return f'{self.title} ({self.year})'

    def save(self, *args, **kwargs):
        if not self.slug:
            base = slugify(self.title, allow_unicode=True) or f'film-{self.pk or 0}'
            slug = base
            n = 1
            while Film.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f'{base}-{n}'
                n += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def duration_display(self):
        """Возвращает строку вида '2ч 36м'."""
        h = self.duration // 60
        m = self.duration % 60
        return f'{h}ч {m}м' if h else f'{m}м'


class FilmImage(models.Model):
    film  = models.ForeignKey(Film, related_name='images', on_delete=models.CASCADE, verbose_name='Фильм')
    image = models.ImageField('Изображение/Кадр', upload_to='movies/')

    class Meta:
        verbose_name = 'Изображение фильма'
        verbose_name_plural = 'Изображения фильма'


class Genre(models.Model):
    genre = models.CharField(max_length=100, verbose_name='Жанр')
    slug  = models.SlugField(max_length=120, unique=True, null=True, blank=True, allow_unicode=True)

    class Meta:
        verbose_name = 'Жанр'
        verbose_name_plural = 'Жанры'

    def __str__(self):
        return self.genre


class Showtime(models.Model):
    film          = models.ForeignKey(Film, on_delete=models.CASCADE, related_name='showtimes', verbose_name='Фильм')
    date_time     = models.DateTimeField(verbose_name='Дата и время сеанса')
    hall_name     = models.CharField(max_length=50, verbose_name='Зал')
    price         = models.FloatField(verbose_name='Цена билета на этот сеанс')
    rows          = models.PositiveSmallIntegerField(default=10, verbose_name='Рядов в зале')
    seats_per_row = models.PositiveSmallIntegerField(default=12, verbose_name='Мест в ряду')

    class Meta:
        verbose_name = 'Сеанс'
        verbose_name_plural = 'Сеансы'

    def __str__(self):
        return f'{self.film.title} — {self.date_time.strftime("%d.%m.%Y %H:%M")} ({self.hall_name})'


class Ticket(models.Model):
    showtime    = models.ForeignKey(Showtime, on_delete=models.CASCADE, verbose_name='Сеанс')
    seat_number = models.IntegerField(verbose_name='Место')
    row_number  = models.IntegerField(verbose_name='Ряд')
    is_bought   = models.BooleanField(default=False, verbose_name='Куплен')
    user        = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='tickets',
        verbose_name='Покупатель'
    )
    bought_at   = models.DateTimeField(null=True, blank=True, verbose_name='Дата покупки')

    class Meta:
        verbose_name = 'Билет'
        verbose_name_plural = 'Билеты'
        unique_together = ('showtime', 'row_number', 'seat_number')


class Slider(models.Model):
    """Слайды для главного Hero-баннера."""
    image       = models.ImageField(upload_to='slider/', verbose_name='Изображение')
    title       = models.CharField(max_length=200, verbose_name='Название')
    description = models.TextField(verbose_name='Описание', blank=True)
    genre       = models.CharField(max_length=100, verbose_name='Жанр', blank=True)
    duration    = models.PositiveIntegerField(verbose_name='Длительность (мин)', default=0)
    rating      = models.DecimalField(
        max_digits=3, decimal_places=1, verbose_name='Рейтинг', default=0.0
    )
    order       = models.PositiveSmallIntegerField(default=0, verbose_name='Порядок')
    is_active   = models.BooleanField(default=True, verbose_name='Активен')

    class Meta:
        verbose_name = 'Слайд'
        verbose_name_plural = 'Слайдер (главная)'
        ordering = ['order']

    def __str__(self):
        return self.title

    def duration_display(self):
        h = self.duration // 60
        m = self.duration % 60
        return f'{h}ч {m}м' if h else f'{m}м'


class PromoBanner(models.Model):
    """Промо-баннер на главной странице (большой блок с фоновым изображением)."""
    badge_text  = models.CharField(max_length=60, default='Премьера недели', verbose_name='Текст значка')
    image       = models.ImageField(upload_to='promo/', verbose_name='Фоновое изображение')
    title       = models.CharField(max_length=200, verbose_name='Название (крупно)')
    subtitle    = models.CharField(max_length=200, blank=True, verbose_name='Подзаголовок (розовый)')
    description = models.TextField(blank=True, verbose_name='Описание / синопсис')
    genre       = models.CharField(max_length=150, blank=True, verbose_name='Жанр')
    rating      = models.DecimalField(max_digits=3, decimal_places=1, default=0.0, verbose_name='IMDb рейтинг')
    duration    = models.PositiveIntegerField(default=0, verbose_name='Длительность (мин)')
    button_url  = models.CharField(max_length=300, blank=True, default='#', verbose_name='Ссылка кнопки «Смотреть»')
    is_active   = models.BooleanField(default=True, verbose_name='Показывать на сайте')

    class Meta:
        verbose_name = 'Промо-баннер'
        verbose_name_plural = 'Промо-баннер (главная)'

    def __str__(self):
        return self.title

    def duration_display(self):
        h = self.duration // 60
        m = self.duration % 60
        return f'{h}ч {m}м' if h else f'{m}м'


class CartoonFilm(Film):
    """Прокси-модель для управления мультфильмами в отдельной секции админки."""
    class Meta:
        proxy = True
        verbose_name = 'Мультфильм'
        verbose_name_plural = 'Мультфильмы'


POSITION_CHOICES = [(i, str(i)) for i in range(1, 6)]


class FeaturedFilm(models.Model):
    """Рекомендуемые фильмы на главной (ровно 5 позиций)."""
    film     = models.OneToOneField(
        Film, on_delete=models.CASCADE,
        limit_choices_to={'is_cartoon': False},
        verbose_name='Фильм'
    )
    position = models.PositiveSmallIntegerField(
        choices=POSITION_CHOICES, unique=True,
        verbose_name='Позиция (1–5)'
    )

    class Meta:
        verbose_name = 'Рекомендуемый фильм'
        verbose_name_plural = 'Рекомендуемые фильмы (главная)'
        ordering = ['position']

    def __str__(self):
        return f'#{self.position} — {self.film}'


class FeaturedCartoon(models.Model):
    """Рекомендуемые мультфильмы на главной (ровно 5 позиций)."""
    film     = models.OneToOneField(
        Film, on_delete=models.CASCADE,
        limit_choices_to={'is_cartoon': True},
        verbose_name='Мультфильм'
    )
    position = models.PositiveSmallIntegerField(
        choices=POSITION_CHOICES, unique=True,
        verbose_name='Позиция (1–5)'
    )

    class Meta:
        verbose_name = 'Рекомендуемый мультфильм'
        verbose_name_plural = 'Рекомендуемые мультфильмы (главная)'
        ordering = ['position']

    def __str__(self):
        return f'#{self.position} — {self.film}'


SLIDER_ORDER_CHOICES = [(i, str(i)) for i in range(1, 11)]


class SliderItem(models.Model):
    """Фильм в герой-карусели на главной странице."""
    film  = models.OneToOneField(
        Film, on_delete=models.CASCADE,
        verbose_name='Фильм'
    )
    order = models.PositiveSmallIntegerField(
        choices=SLIDER_ORDER_CHOICES, unique=True,
        verbose_name='Позиция (1–10)'
    )

    class Meta:
        verbose_name = 'Слайд'
        verbose_name_plural = 'Слайдер (главная)'
        ordering = ['order']

    def __str__(self):
        return f'#{self.order} — {self.film}'


class BannerItem(models.Model):
    """Промо-баннер на главной — один активный фильм."""
    film = models.OneToOneField(
        Film, on_delete=models.CASCADE,
        verbose_name='Фильм'
    )

    class Meta:
        verbose_name = 'Промо-баннер'
        verbose_name_plural = 'Промо-баннер (главная)'

    def __str__(self):
        return f'Баннер: {self.film}'


class Favorite(models.Model):
    """Избранные фильмы пользователя."""
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='favorites',
        verbose_name='Пользователь'
    )
    film = models.ForeignKey(
        Film,
        on_delete=models.CASCADE,
        related_name='favorited_by',
        verbose_name='Фильм'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'film')
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранное'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.user} → {self.film}'