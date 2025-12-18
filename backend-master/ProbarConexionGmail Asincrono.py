import aiosmtplib
import asyncio
import ssl
from email.message import EmailMessage
import email.utils
import uuid

async def send_email():
    try:
        # Configuración SMTP
        ssl_context = ssl.create_default_context()
        client = aiosmtplib.SMTP(
            hostname="smtp.gmail.com",
            port=587,
            start_tls=True,
            tls_context=ssl_context,
            timeout=20
        )
        await client.connect()
        
        # Autenticación
        await client.login("sistema.academia.25@gmail.com", "acsr lmlb ouxl oxxf")

        # Crear mensaje profesional
        msg = EmailMessage()
        msg["From"] = "Academia <sistema.academia.25@gmail.com>"
        msg["To"] = "sistema.academia.25@gmail.com"
        msg["Subject"] = "Confirmación de sistema"
        msg["Message-ID"] = f"<{uuid.uuid4()}@gmail.com>"
        msg["Date"] = email.utils.formatdate(localtime=True)
        
        # Contenido mixto (texto + HTML)
        msg.set_content("Confirmamos tu acceso al sistema.")
        msg.add_alternative("""\
        <html>
            <body>
                <p>Hola,</p>
                <p>Confirmamos tu acceso al <strong>Sistema Académico</strong>.</p>
            </body>
        </html>
        """, subtype="html")

        # Envío
        await client.send_message(msg)
        print("¡Correo enviado correctamente a la bandeja principal!")
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        await client.quit()

if __name__ == "__main__":
    asyncio.run(send_email())