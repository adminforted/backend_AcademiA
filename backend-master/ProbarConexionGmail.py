import aiosmtplib
import asyncio
import ssl

async def test_smtp():
    try:
        # Configurar cliente SMTP con timeout
        client = aiosmtplib.SMTP(
            hostname="smtp.gmail.com",
            port=587,
            username="sistema.academia.25@gmail.com",  # Reemplaza con tu correo
            password="acsr lmlb ouxl oxxf",  # Reemplaza con tu contraseña de aplicación
            start_tls=True,
            timeout=10,  # Timeout de 10 segundos
        )
        # Conectar y autenticar
        async with client:
            await client.connect()
            print("Conexión exitosa")
    except aiosmtplib.SMTPException as e:
        print(f"Error SMTP: {e}")
    except asyncio.TimeoutError:
        print("Error: Timeout al conectar con el servidor SMTP")
    except Exception as e:
        print(f"Error general: {e}")

if __name__ == "__main__":
    asyncio.run(test_smtp())



