from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
import random
import string

from .models import VerificationCode


class AuthService:
    @staticmethod
    def get_client_ip(request):
        """Получить IP адрес клиента"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip

    @staticmethod
    def create_user_with_profile(email, username, password, **extra_fields):
        """Создать пользователя с профилем"""
        from .models import User, UserProfile

        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            **extra_fields
        )
        UserProfile.objects.create(user=user)
        return user


class VerificationService:
    @staticmethod
    def generate_code(length=6):
        """Генерация случайного кода"""
        return ''.join(random.choices(string.digits, k=length))

    @staticmethod
    def create_verification_code(user, code_type, expires_minutes=30):
        """Создать код верификации"""
        # Деактивируем предыдущие коды этого типа
        VerificationCode.objects.filter(
            user=user,
            code_type=code_type,
            is_used=False
        ).update(is_used=True)

        # Создаем новый код
        code = VerificationService.generate_code()
        expires_at = timezone.now() + timezone.timedelta(minutes=expires_minutes)

        return VerificationCode.objects.create(
            user=user,
            code_type=code_type,
            code=code,
            expires_at=expires_at
        )

    @staticmethod
    def send_email_verification(user):
        """Отправить код подтверждения email"""
        try:
            verification_code = VerificationService.create_verification_code(
                user, 'email_verification'
            )

            # В реальном приложении здесь будет отправка email
            subject = 'Подтверждение email - Добрые дела Росатома'
            message = f'''
            Здравствуйте, {user.first_name}!

            Ваш код подтверждения: {verification_code.code}
            Код действителен в течение 30 минут.

            С уважением,
            Команда "Добрые дела Росатома"
            '''

            # В разработке просто выводим код в консоль
            if settings.DEBUG:
                print(f"Email verification code for {user.email}: {verification_code.code}")

            # В продакшене раскомментировать:
            # send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [user.email])

            return True
        except Exception as e:
            print(f"Error sending verification email: {e}")
            return False

    @staticmethod
    def send_password_reset_code(user):
        """Отправить код для сброса пароля"""
        try:
            verification_code = VerificationService.create_verification_code(
                user, 'password_reset'
            )

            # Аналогично send_email_verification, но для сброса пароля
            if settings.DEBUG:
                print(f"Password reset code for {user.email}: {verification_code.code}")

            return True
        except Exception:
            return False

    @staticmethod
    def verify_email_code(user, code):
        """Проверить код подтверждения email"""
        try:
            verification_code = VerificationCode.objects.get(
                user=user,
                code_type='email_verification',
                code=code,
                is_used=False
            )

            if verification_code.is_valid():
                verification_code.is_used = True
                verification_code.save()
                return True
        except VerificationCode.DoesNotExist:
            pass

        return False

    @staticmethod
    def has_active_email_code(user):
        """Проверить есть ли активный код подтверждения"""
        return VerificationCode.objects.filter(
            user=user,
            code_type='email_verification',
            is_used=False,
            expires_at__gt=timezone.now()
        ).exists()