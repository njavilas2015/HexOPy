import argparse
import asyncio
import importlib.util
import os
import sys

import uvicorn

BASE_DIR = os.getcwd()

sys.path.append(BASE_DIR)

async def run_server():
    """Ejecuta `internal/main.py` como servidor"""
    internal_main = os.path.join(BASE_DIR, "internal", "main.py")

    if not os.path.exists(internal_main):
        print("❌ No se encontró `internal/main.py`. Asegúrate de crearlo.")
        sys.exit(1)

    spec = importlib.util.spec_from_file_location("internal.main", internal_main)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    if hasattr(module, "server"):
        print("🚀 Iniciando FastAPI desde `internal/main.py`...")

        print(f"🚀 Iniciando servidor en {module.server.host}:{module.server.port} ...")

        uvicorn.run(
            "internal.main:server.http",
            host=module.server.host,
            port=module.server.port,
            reload=module.server.reload, 
            workers=module.server.workers
        )

    else:
        print("❌ `internal/main.py` no contiene una instancia `server`.")

def create_migration():
    """Genera una migración para la base de datos"""
    print("📦 Creando migración...")
    # Aquí podrías ejecutar un comando ORM o algún script de migraciones
    os.system("alembic revision --autogenerate -m 'Nueva migración'")

def apply_migrations():
    """Aplica migraciones a la base de datos"""
    print("📦 Aplicando migraciones...")
    os.system("alembic upgrade head")

def list_routes():
    """Lista todas las rutas del servidor"""
    internal_main = os.path.join(BASE_DIR, "internal", "main.py")

    if not os.path.exists(internal_main):
        print("❌ No se encontró `internal/main.py`. Asegúrate de crearlo.")
        sys.exit(1)

    spec = importlib.util.spec_from_file_location("internal.main", internal_main)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    if hasattr(module, "server"):
        print("📌 Rutas registradas:")
        for route in module.server.http.routes:
            print(f"➡ {route.path} - {route.methods}")
    else:
        print("❌ `internal/main.py` no contiene una instancia `server`.")

def main():
    parser = argparse.ArgumentParser(description="CLI para manejar HexoServer")
    subparsers = parser.add_subparsers(dest="command")

    # Comando para ejecutar el servidor
    subparsers.add_parser("run", help="Iniciar el servidor")

    # Comando para crear una nueva migración
    subparsers.add_parser("makemigrations", help="Generar una nueva migración")

    # Comando para aplicar migraciones
    subparsers.add_parser("migrate", help="Aplicar migraciones")

    # Comando para listar las rutas de la API
    subparsers.add_parser("routes", help="Listar rutas de")

    args = parser.parse_args()

    if args.command == "run":
        asyncio.run(run_server())
    elif args.command == "makemigrations":
        create_migration()
    elif args.command == "migrate":
        apply_migrations()
    elif args.command == "routes":
        list_routes()
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
