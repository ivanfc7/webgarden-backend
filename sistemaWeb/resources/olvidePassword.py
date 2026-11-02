from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.core.mail import send_mail
from django.contrib.auth.models import User
import requests
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework import status
from django.conf import settings

token_generator = PasswordResetTokenGenerator()

LOCAL_URL = 'http://127.0.0.1:5173'
DEPLOY_URL = 'https://webgarden.vercel.app'

@api_view(["POST"])
def generar_token(request):
    correo = request.data.get("correo")
    try:
        user = User.objects.get(email=correo)
    except:
        return Response({"error": "Correo no encontrado"}, status=status.HTTP_404_NOT_FOUND)
    
    # Si se encontro
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    token = token_generator.make_token(user)

    reset_url = f"{DEPLOY_URL}/reset-password/{uid}/{token}/"
    # Aquí deberías usar un sistema real de emails (SMTP, Sendgrid, etc.)
    try:
        enviar_correo(correo, reset_url)
        print("Correo enviado mediante Brevo")
        print('enviando')
        return Response({"success": "Correo enviado"}, status=status.HTTP_200_OK)
    except:
        return Response({"error": "Correo no fue enviado"}, status=status.HTTP_400_BAD_REQUEST)
    
@api_view(["POST"])
def reset_password(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (User.DoesNotExist, ValueError, TypeError, OverflowError):
        return Response({"error": "Token inválido"}, status=status.HTTP_400_BAD_REQUEST)

    if not token_generator.check_token(user, token):
        return Response({"error": "Token inválido o expirado"}, status=status.HTTP_400_BAD_REQUEST)

    new_password = request.data.get("new_password")
    user.set_password(new_password)
    user.save()
    return Response({"success": "Contraseña restablecida correctamente"}, status=status.HTTP_200_OK)

def enviar_correo(email, link):
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
        "subject": "Cambiar contraseña",
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
                            Utiliza el siguiente botón para verificar tu correo y tener acceso al cambio de contraseña de 
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
                                Cambiar contraseña
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
        url, headers=headers, json=data, timeout=10,
    )
    response.raise_for_status()
    return response.json()
