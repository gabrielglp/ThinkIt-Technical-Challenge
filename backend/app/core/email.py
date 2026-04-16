import logging
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import aiosmtplib

from app.core.config import settings

log = logging.getLogger(__name__)


async def send_mail(to: str, subject: str, html: str) -> None:
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


def build_forgot_password_email(name: str, new_password: str) -> str:
    return f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Nova Senha — Função extra</title>
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
    .badge {{ display: inline-block; background: #dc2626; color: #fff; padding: 4px 10px;
              border-radius: 4px; font-size: 11px; font-weight: 600; text-transform: uppercase;
              letter-spacing: 0.5px; margin-bottom: 16px; }}
    .title {{ font-size: 24px; font-weight: 700; margin-bottom: 12px; }}
    .text {{ color: #d4d4d8; font-size: 15px; margin-bottom: 20px; }}
    .password-box {{ background: #2a2a2a; border: 2px solid #22c55e; border-radius: 8px;
                     padding: 20px; margin: 24px 0; text-align: center; }}
    .password-label {{ color: #a1a1aa; font-size: 12px; font-weight: 600;
                       text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 8px; }}
    .password-value {{ color: #22c55e; font-size: 20px; font-weight: 700;
                       font-family: 'Courier New', monospace; letter-spacing: 3px;
                       background: #1a1a1a; padding: 12px 20px; border-radius: 6px;
                       display: inline-block; margin-top: 6px; }}
    .warning {{ background: #7f1d1d; border: 1px solid #dc2626; color: #fca5a5;
                padding: 14px; border-radius: 8px; margin: 20px 0; font-size: 14px; }}
    .btn {{ display: inline-block; background: #ffffff; color: #000000; text-decoration: none;
            padding: 12px 28px; border-radius: 8px; font-weight: 600; font-size: 14px;
            margin-top: 16px; }}
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
      <div class="badge">Recuperação de senha</div>
      <h1 class="title">🔐 Nova senha gerada</h1>
      <p class="text">
        Olá <strong>{name}</strong>, uma nova senha temporária foi gerada para a sua conta.
      </p>
      <div class="password-box">
        <div class="password-label">Sua nova senha</div>
        <div class="password-value">{new_password}</div>
      </div>
      <div class="warning">
        ⚠️ Esta é uma senha temporária. Recomendamos que você altere sua senha após fazer login.
      </div>
      <div style="text-align:center;">
        <a href="{settings.app_url}/login" class="btn">Fazer login agora</a>
      </div>
    </div>
    <div class="footer">
      Se você não solicitou esta alteração, ignore este email — sua senha antiga continua válida.<br>
      Este email foi enviado automaticamente. Não responda a este email.
    </div>
  </div>
</body>
</html>"""
