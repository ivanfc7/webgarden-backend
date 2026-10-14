from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import User
from ..serializer import UserSerializer
from rest_framework import status
from django.shortcuts import get_object_or_404
from rest_framework.decorators import authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from rest_framework_simplejwt.authentication import JWTAuthentication
from ..models import Planta, AporteAmbiental
from django.db.models import Sum

@api_view(['POST'])
def register(request):
    nuevoUser = UserSerializer(data=request.data)
    if nuevoUser.is_valid():
        nuevoUser.save()
        return Response({'mensaje': 'Usuario creado correctamente'}, status=status.HTTP_201_CREATED)
    return Response(nuevoUser.errors, status=status.HTTP_400_BAD_REQUEST)

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