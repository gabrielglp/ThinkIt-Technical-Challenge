import logging
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import aiosmtplib

from app.core.config import settings

log = logging.getLogger(__name__)


async def send_mail(to: str, subject: str, html: str) -> None:
    if not settings.smtp_host or not settings.smtp_port:
        log.warning("SMTP não configurado — email para %s ignorado (assunto: %s)", to, subject)
        return

    message = MIMEMultipart("alternative")
    message["From"] = settings.smtp_from_email
    message["To"] = to
    message["Subject"] = subject
    message.attach(MIMEText(html, "html"))

    await aiosmtplib.send(
        message,
        hostname=settings.smtp_host,
        port=settings.smtp_port,
        username=settings.smtp_user,
        password=settings.smtp_password,
        use_tls=True,
        validate_certs=False,
    )
    log.info("Email enviado para %s — assunto: %s", to, subject)


def build_reset_password_email(name: str, token: str) -> str:
    reset_url = f"{settings.app_url}/reset-password/{token}"
    return f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Redefinição de senha — Função extra</title>
  <style>
    * {{ margin: 0; padding: 0; box-sizing: border-box; }}
    body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Arial, sans-serif;
            background: #0f0f0f; color: #ffffff; line-height: 1.6; }}
    .container {{ max-width: 600px; margin: 0 auto; padding: 40px 20px; }}
    .header {{ text-align: center; margin-bottom: 40px; }}
    .logo {{ font-size: 28px; font-weight: 700; color: #ffffff; }}
    .subtitle {{ color: #a1a1aa; font-size: 14px; margin-top: 4px; }}
    .card {{ background: #1f1f1f; border: 1px solid #2a2a2a; border-radius: 12px;
             padding: 32px; margin-bottom: 24px; }}
    .badge {{ display: inline-block; background: #2563eb; color: #fff; padding: 4px 10px;
              border-radius: 4px; font-size: 11px; font-weight: 600; text-transform: uppercase;
              letter-spacing: 0.5px; margin-bottom: 16px; }}
    .title {{ font-size: 24px; font-weight: 700; margin-bottom: 12px; }}
    .text {{ color: #d4d4d8; font-size: 15px; margin-bottom: 20px; }}
    .warning {{ background: #1e3a5f; border: 1px solid #2563eb; color: #93c5fd;
                padding: 14px; border-radius: 8px; margin: 20px 0; font-size: 14px; }}
    .btn {{ display: inline-block; background: #ffffff; color: #000000; text-decoration: none;
            padding: 14px 32px; border-radius: 8px; font-weight: 600; font-size: 15px;
            margin-top: 8px; }}
    .footer {{ text-align: center; margin-top: 32px; padding-top: 24px;
               border-top: 1px solid #2a2a2a; color: #52525b; font-size: 12px; }}
  </style>
</head>
<body>
  <div class="container">
    <div class="header">
      <div class="logo">⬡ Função extra</div>
      <div class="subtitle">Plataforma de gestão de pedidos</div>
    </div>
    <div class="card">
      <div class="badge">Redefinição de senha</div>
      <h1 class="title">Redefinir sua senha</h1>
      <p class="text">
        Olá <strong>{name}</strong>, recebemos uma solicitação para redefinir a senha da sua conta.
        Clique no botão abaixo para criar uma nova senha.
      </p>
      <div style="text-align:center; margin: 28px 0;">
        <a href="{reset_url}" class="btn">Redefinir senha</a>
      </div>
      <div class="warning">
        ⏱️ Este link é válido por <strong>30 minutos</strong>. Após esse prazo, você precisará solicitar um novo link.
      </div>
    </div>
    <div class="footer">
      Se você não solicitou a redefinição de senha, ignore este email — sua senha atual continua válida.<br>
      Este email foi enviado automaticamente. Não responda a este email.
    </div>
  </div>
</body>
</html>"""
