from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import User
from ..serializer import UserSerializer
from rest_framework import status
from rest_framework.decorators import authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from ..models import Planta, AporteAmbiental
from django.db.models import Sum
from django.http import HttpResponse
from django.contrib.auth import authenticate
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from ..models import ProgresoJuego, MensajeJuego,  AprendizajeJuego
from ..serializer import UserSerializer
from django.db import transaction
from ..resources.datos_iniciales import CONSEJOS_INICIALES, APRENDIZAJES_INICIALES
from django.db import connection

@api_view(["POST"])
def login(request):
    username = request.data.get("username")
    password = request.data.get("password")

    if not username or not password:
        return Response(
            {"error": "Debes ingresar usuario y contraseña."},
            status=status.HTTP_400_BAD_REQUEST
        )

    user = authenticate(
        request,
        username=username,
        password=password
    )

    if user is None:
        return Response(
            {"error": "Usuario o contraseña incorrectos."},
            status=status.HTTP_401_UNAUTHORIZED
        )

    # Garantizar que el usuario tenga un progreso registrado
    ProgresoJuego.objects.get_or_create(usuario=user)

    refresh = RefreshToken.for_user(user)
    access = str(refresh.access_token)

    serializer = UserSerializer(instance=user)

    response = Response(
        {
            "token": access,
            "user": serializer.data
        },
        status=status.HTTP_200_OK
    )

    response.set_cookie(
        key="refresh_token",
        value=str(refresh),
        httponly=True,
        secure=False,  # Solo desarrollo local
        samesite="Lax",
        max_age=60 * 60 * 24 * 30,
        path="/sistemaWeb/api/"
    )

    return response
@api_view(['POST'])
def register(request):
    nuevoUser = UserSerializer(data=request.data)

    if nuevoUser.is_valid():
        # 1. Crear usuario mediante el serializer
        usuario = nuevoUser.save()

        # 2. Insertar directamente en la tabla de Turso usando SQL puro
        with connection.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO sistemaWeb_progresojuego 
                (usuario_id, cantidadMsjDesbloqueados, cantidadApzjDesbloqueados, experiencia)
                VALUES (%s, %s, %s, %s)
                """,
                [usuario.pk, 3, 1, 0]
            )

        # 3. Obtener la instancia de ProgresoJuego ya confirmada en la BD
        progreso = ProgresoJuego.objects.get(usuario=usuario)
        print('============VALIDACION============')
        print(progreso)
        print('=============================')
        # 4. Crear los mensajes iniciales
        for consejo in CONSEJOS_INICIALES:
            MensajeJuego.objects.create(
                progreso=progreso,
                titulo=consejo["titulo"],
                descripcion=consejo["descripcion"],
                desbloqueado=True
            )

        # 5. Crear los aprendizajes iniciales
        for tema in APRENDIZAJES_INICIALES:
            AprendizajeJuego.objects.create(
                progreso=progreso,
                titulo=tema["titulo"],
                contenido=tema["contenido"],
                imagen=tema["imagen"],
                fuente=tema["fuente"],
                desbloqueado=True
            )

        return Response({
            'mensaje': 'Usuario y progreso creados correctamente',
            'progresoId': progreso.pk,
            'consejosIniciales': 3,
        }, status=status.HTTP_201_CREATED)

    return Response(
        nuevoUser.errors,
        status=status.HTTP_400_BAD_REQUEST
    )

@api_view(['POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def profile(request):
    elId = request.user.id
    nombre = request.user.first_name
    apellidos = request.user.last_name
    correo = request.user.email
    return Response({"id":elId , "firstName": nombre, "lastName": apellidos, "email": correo},status=status.HTTP_200_OK)

@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def totalPlantas(request):
    user = request.user
    total = Planta.objects.filter(usuario=user).count()
    if not total:
        total = 0
    return Response({'total': total},status=status.HTTP_200_OK)

@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def totalAportes(request):
    user = request.user
    total = AporteAmbiental.objects.filter(planta__usuario=user).aggregate(
        totalCarbono = Sum('carbonoTotal')
    )
    if not total:
        total = [0]
    return Response({"total":total["totalCarbono"] or 0}, status=status.HTTP_200_OK)

def ping(request):
    print(request)
    return HttpResponse("ok", content_type="text/plain")