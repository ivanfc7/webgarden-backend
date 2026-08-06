import traceback
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from ..resources.magic import generar_magic_token, verify_magic_token
from django.contrib.auth.models import User
from rest_framework_simplejwt.tokens import RefreshToken
from django.http import JsonResponse
import os
import resend
from django.conf import settings

@api_view(["POST"])
def magic_link(request):
    email = request.data.get("email")
    nombre = request.data.get("first_name")

    if not email:
        return Response( {"error": "Email requerido"}, status=status.HTTP_400_BAD_REQUEST )
    
    if nombre is None:
        user, created = User.objects.get_or_create(
            username=email,
        )
    else:
        user, created = User.objects.get_or_create(
            username=email,
            defaults={"email": email, "first_name": nombre}
        )

    if not created and nombre:
        user.first_name = nombre
        user.save()

    token = generar_magic_token(email)
    link = f"https://webgarden.vercel.app/verify-magic/{token}"
    resend.api_key = settings.RESEND_API_KEY

    try:
        # send_mail(
        #     "Verificar usuario",
        #     f"Ingresa a este link para verificar tu usuario y activar la cuenta: {link}",
        #     "ivanflores521111@gmail.com",
        #     [email],
        # )
        params = {
            "from": "onboarding@resend.dev", # Remitente gratuito de prueba de Resend
            "to": email, # Tu correo donde quieres que llegue
            "subject": "Tu link de acceso - Sistema Educativo de plantas y arboles",
            "html": f"<strong>¡Hola!</strong> Ingresa a este link para verificar tu usuario y activar la cuenta: <a href='{link}'>Haz clic aquí</a>",
        }
        
        email_output = resend.Emails.send(params)
        print('enviando '+email_output)
        return Response({"success": "Correo enviado"}, status=status.HTTP_200_OK)
    except Exception as e:
        print(f"Error crítico en Resend: {e}")
        return Response({"error": "Correo no fue enviado"}, status=status.HTTP_400_BAD_REQUEST)
        raise
    
@api_view(["GET"])
def verify_magic(request):
    try:
        token = request.GET.get("token")
        print(f"--- TOKEN RECIBIDO: {token} ---")
        
        # Validamos el token
        email = verify_magic_token(token)

        if not email:
            print("--- ALERTA: verify_magic_token devolvió None (Token inválido o expirado) ---")
            return Response(
                {"error": "Token inválido o expirado"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Buscamos o creamos al usuario
        user, created = User.objects.get_or_create(
            username=email,
            defaults={"email": email}
        )

        refresh = RefreshToken.for_user(user)
        response = JsonResponse({
            "access": str(refresh.access_token),
            "is_new_user": created
        })

        # Configuración de Cookie (Atención con secure/samesite para producción)
        response.set_cookie(
            key="refresh_token",
            value=str(refresh),
            httponly=True,
            secure=True,    # CAMBIADO A True: Vercel y Render usan HTTPS en producción
            samesite="None", # CAMBIADO A None: Necesario para peticiones Cross-Site (Vercel <-> Render)
            max_age=60 * 60 * 24 * 30
        )
        return response

    except Exception as e:
        print("--- EXCEPCIÓN DETECTADA EN VERIFY_MAGIC ---")
        traceback.print_exc()  # Esto imprimirá el error real con número de línea en Render
        print("-------------------------------------------")
        return Response(
            {"error": f"Error interno en el servidor: {str(e)}"},
            status=status.HTTP_400_BAD_REQUEST
        )