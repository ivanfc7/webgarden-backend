import traceback
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from ..resources.magic import generar_magic_token, verify_magic_token
from django.contrib.auth.models import User
from rest_framework_simplejwt.tokens import RefreshToken
from django.http import JsonResponse
from django.conf import settings
import requests

LOCAL_URL = 'http://127.0.0.1:5173'
DEPLOY_URL = 'https://webgarden.vercel.app'

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
    link = f"{DEPLOY_URL}/verify-magic/{token}"
    
    try:
        enviar_magic_link(email, link)
        print("Correo enviado mediante Brevo")
        return Response({"success": "Correo enviado"}, status=status.HTTP_200_OK)
    except Exception as e:
        print("=== DETALLE DEL ERROR DEL CORREO ===")
        traceback.print_exc()
        print("===================================")
        return Response(
            {"error": f"Error de Resend: {str(e)}"}, 
            status=status.HTTP_400_BAD_REQUEST
        )
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
            secure=True,    # True in Deploy - False in Local
            samesite="None", # None in Deploy - Lax in Local
            max_age=60 * 60 * 24 * 30
        )
        return response

    except Exception as e:
        print("--- EXCEPCIÓN DETECTADA EN VERIFY_MAGIC ---")
        traceback.print_exc()  
        print("-------------------------------------------")
        return Response(
            {"error": f"Error interno en el servidor: {str(e)}"},
            status=status.HTTP_400_BAD_REQUEST
        )
    
def enviar_magic_link(email, link):
    url = "https://api.brevo.com/v3/smtp/email"

    headers = {
        "accept": "application/json",
        "api-key": settings.BREVO_API_KEY,
        "content-type": "application/json",
    }

    data = {
        "sender": {
            "name": settings.BREVO_SENDER_NAME,
            "email": settings.BREVO_SENDER_EMAIL,
        },
        "to": [
            {
                "email": email,
            }
        ],
        "subject": "Verificar usuario",
        "htmlContent": f"""
            <div style="
                margin: 0;
                padding: 40px 20px;
                background-color: #f0fdf4;
                font-family: Arial, Helvetica, sans-serif;
            ">
                <div style="
                    max-width: 520px;
                    margin: 0 auto;
                    background-color: #ffffff;
                    border-radius: 16px;
                    overflow: hidden;
                    border: 1px solid #bbf7d0;
                    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
                ">
                    <!-- Encabezado -->
                    <div style="
                        background-color: #166534;
                        padding: 28px 24px;
                        text-align: center;
                    ">
                        <div style="
                            font-size: 42px;
                            margin-bottom: 8px;
                        ">
                            🌱
                        </div>

                        <h1 style="
                            margin: 0;
                            color: #ffffff;
                            font-size: 26px;
                            font-weight: bold;
                        ">
                            Bienvenido
                        </h1>
                    </div>

                    <!-- Contenido -->
                    <div style="
                        padding: 32px 28px;
                        color: #374151;
                    ">
                        <p style="
                            margin-top: 0;
                            font-size: 16px;
                            line-height: 1.6;
                        ">
                            Hola,
                        </p>

                        <p style="
                            font-size: 16px;
                            line-height: 1.6;
                        ">
                            Utiliza el siguiente botón para verificar tu correo y tener acceso a
                            <strong style="color: #166534;">Mi Jardín</strong>.
                        </p>

                        <!-- Botón -->
                        <div style="
                            text-align: center;
                            margin: 30px 0;
                        ">
                            <a href="{link}" style="
                                display: inline-block;
                                padding: 14px 28px;
                                background-color: #15803d;
                                color: #ffffff;
                                text-decoration: none;
                                border-radius: 10px;
                                font-size: 16px;
                                font-weight: bold;
                            ">
                                Verificar mi acceso
                            </a>
                        </div>
                    </div>

                    <!-- Pie -->
                    <div style="
                        padding: 20px 24px;
                        background-color: #f9fafb;
                        text-align: center;
                        border-top: 1px solid #e5e7eb;
                    ">
                        <p style="
                            margin: 0;
                            color: #166534;
                            font-size: 14px;
                            font-weight: bold;
                        ">
                            🌿 Webgarden
                        </p>

                        <p style="
                            margin: 8px 0 0;
                            color: #9ca3af;
                            font-size: 12px;
                        ">
                            Sistema web educativo para el seguiumiento y cuidado de arboles y plantas.
                        </p>
                    </div>
                </div>
            </div>
        """,
    }

    response = requests.post(
        url,
        headers=headers,
        json=data,
        timeout=10,
    )
    response.raise_for_status()
    return response.json()
