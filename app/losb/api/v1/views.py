from __future__ import annotations

from random import SystemRandom

from drf_spectacular.utils import extend_schema_view, extend_schema
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from app import settings
from losb.api.v1 import exceptions
from losb.api.v1.serializers import (
    UserSerializer,
    UserNameSerializer,
    UserCitySerializer,
    UserBirthdaySerializer,
    UserPhoneSerializer,
    CitySerializer,
    UserPhoneVerificationSerializer,
    PhoneSerializer,
    BotUrlSerializer,

)
from losb.api.v1.services.sms_verification import SmsVerificationService
from losb.models import City
from losb.schema import TelegramIdJWTSchema  # do not remove, needed for swagger


@extend_schema_view(
    get=extend_schema(
        responses={
            200: CitySerializer,
        },
        summary='Список городов России',
        description='Возвращает список городов России',
    ),
)
class CityListView(generics.ListAPIView):
    serializer_class = CitySerializer
    permission_classes = [IsAuthenticated, ]
    pagination_class = None
    queryset = City.objects.all()


@extend_schema_view(
    get=extend_schema(
        responses={
            200: UserSerializer,
        },
        summary='Профиль пользователя',
        description='Возвращает профиль пользователя',
    ),
)
class UserRetrieveView(generics.RetrieveAPIView):
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated, ]

    def get_object(self):
        return self.request.user


@extend_schema_view(
    update=extend_schema(
        responses={
            200: UserNameSerializer,
        },
        summary='Изменение имени пользователя',
    ),
)
class UserNameUpdateView(generics.UpdateAPIView):
    serializer_class = UserNameSerializer
    permission_classes = [IsAuthenticated, ]
    http_method_names = ["put"]

    def get_object(self):
        return self.request.user


@extend_schema_view(
    update=extend_schema(
        responses={
            200: UserCitySerializer,
        },
        summary='Изменение города пользователя',
    ),
)
class UserCityUpdateView(generics.UpdateAPIView):
    serializer_class = UserCitySerializer
    permission_classes = [IsAuthenticated, ]
    http_method_names = ["put"]

    def get_object(self):
        return self.request.user

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        city = City.objects.get(id=serializer.data['city'])
        response_serializer = CitySerializer(city)

        return Response(response_serializer.data)


class UserBirthdayAPIView(APIView):
    http_method_names = ['post']
    permission_classes = [IsAuthenticated, ]

    @extend_schema(
        request=UserBirthdaySerializer,
        responses={
            200: UserBirthdaySerializer,
        },
        summary='Установить дату рождения пользователя',
        description='Устанавливает дату рождения пользователя, если она ещё не была изменена',
    )
    def post(self, request):
        if self.request.user.birthday:
            raise exceptions.BirthdayAlreadyRegistered

        serializer = UserBirthdaySerializer(data=self.request.data)
        serializer.is_valid(raise_exception=True)
        serializer.update(self.request.user, serializer.validated_data)
        return Response(serializer.data)


class UserPhoneUpdateView(APIView):
    permission_classes = [IsAuthenticated, ]
    http_method_names = ["post", "put"]

    @staticmethod
    def get_otp():
        return "".join(SystemRandom().choice('123456789') for _ in range(settings.SMS_VERIFICATOIN_CODE_DIGITS))

    @extend_schema(
        request=UserPhoneSerializer,
        responses={
            200: {},
        },
        summary='Запросить код подтверждения',
        description='Отправляет otp код на указанный номер телефона',
    )
    def post(self, request):
        serializer = UserPhoneSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            service = SmsVerificationService(request.user)
            verification_code = service.request_verification(
                code=serializer.data['code'],
                number=serializer.data['number'],
            )
        except exceptions.SmsDeliveryError as e:
            raise APIException(
                detail=str(e),
                code='sms_delivery_failed'
            )

        # TODO: remove otp from response, for debug only
        return Response(data={"otp": verification_code},status=status.HTTP_200_OK)

    @extend_schema(
        request=UserPhoneVerificationSerializer,
        responses={
            200: PhoneSerializer,
        },
        summary='Верифицировать код подтверждения',
        description='Верифицирует код подтверждения, в случаи успеха обновляет номер телефона пользователя',
    )
    def put(self, request):
        serializer = UserPhoneVerificationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        service = SmsVerificationService(request.user)
        result = service.verify_code(
            otp=serializer.data['otp'],
            code=serializer.data['phone']['code'],
            number=serializer.data['phone']['number'],
        )

        return Response(result)


@extend_schema_view(
    get=extend_schema(
        responses={
            200: BotUrlSerializer,
        },
        summary='Cсылка на бота поддержки',
    ),
)
class TechSupportAPIView(generics.RetrieveAPIView):
    serializer_class = BotUrlSerializer
    permission_classes = [IsAuthenticated, ]

    def get_object(self):
        return {'url': settings.TECHSUPPORT_BOT_URL}
