import os
from types import ModuleType
from typing import Optional

from importlib.machinery import ModuleSpec, SourceFileLoader
from importlib.util import spec_from_file_location, module_from_spec

from onbbu.types import T


class ConfigLoader:
    def __init__(self, base_dir: str):
        self.base_dir = base_dir

    def load_python_config(
        self, path: str, attribute: str, default: Optional[T]
    ) -> Optional[T]:
        """Carga un archivo de configuración en formato Python"""

        config_path: str = os.path.join(self.base_dir, *path.split("/"))

        if not os.path.exists(config_path):
            print(
                f"⚠️ Advertencia: No se encontró `{path}`. Se usará el valor por defecto."
            )
            return default

        spec: ModuleSpec | None = spec_from_file_location("config_module", config_path)

        if spec is None or spec.loader is None:
            print(
                f"⚠️ Advertencia: El archivo `{path}` no tiene un cargador de módulo válido."
            )
            return default

        if isinstance(spec.loader, SourceFileLoader):

            config_module: ModuleType = module_from_spec(spec)

            spec.loader.exec_module(config_module)

            return getattr(config_module, attribute, default)

        print(f"⚠️ Advertencia: El cargador de módulo no es válido para `{path}`.")

        return default
