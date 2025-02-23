Las **entidades** en una **arquitectura hexagonal** deben estar en la **capa de dominio**.  

---

# 📌 **¿Dónde van las entidades en Arquitectura Hexagonal?**
✅ **📂 Capa de Dominio (`domain`)**  
Las **entidades** representan el **núcleo del negocio**, por lo que deben estar en la **capa de dominio**.  
Aquí se define la lógica pura del negocio **sin depender de frameworks ni infraestructura**.

### 📂 **Estructura recomendada**:
```
src/
│── application/         # Casos de uso, DTOs, servicios de aplicación
│── domain/              # Entidades y repositorios (interfaces)
│   ├── entities/        # 🏗️ Entidades de negocio
│   ├── repositories/    # 🔌 Interfaces de repositorios
│── infrastructure/      # Implementaciones concretas (DB, APIs)
│── main.py              # Punto de entrada
```

---

# ✅ **📂 Ejemplo de una entidad en `domain/entities/discount.py`**
```python
# src/domain/entities/discount.py
from dataclasses import dataclass

@dataclass
class Discount:
    id: str
    name: str
    percentage: float

    def update_percentage(self, new_percentage: float):
        if new_percentage <= 0 or new_percentage > 100:
            raise ValueError("Invalid discount percentage")
        self.percentage = new_percentage
```

---

# 🚀 **¿Por qué las entidades deben estar en `domain/` y no en `application/`?**
| Capa               | Función |
|--------------------|---------|
| **`domain/`**      | 📌 **Define las reglas de negocio** sin depender de la infraestructura. Aquí van las entidades. |
| **`application/`** | 📌 **Orquesta los casos de uso** y usa DTOs para transformar datos. |

---

## 🔴 **Ejemplo incorrecto (Entidad en `application/`)**
```python
# ❌ NO PONGAS LAS ENTIDADES AQUÍ
# src/application/entities/discount.py
class Discount:
    ...
```
⚠️ **Problema:**  
- `application/` **no** debe contener la lógica de negocio, solo coordinar la aplicación.  
- Si luego cambias la infraestructura (ej. cambias SQL por NoSQL), tu dominio no debería verse afectado.  

---

### 💡 **Conclusión**
✅ **Las entidades SIEMPRE deben estar en `domain/entities/`**  
✅ La capa de **aplicación (`application/`) no debe contener entidades de dominio**, sino **casos de uso y DTOs**.  
✅ Mantener el **dominio puro** hace que tu código sea más flexible y fácil de probar.  

---


En un **caso de uso**, lo ideal es utilizar un **DTO (Data Transfer Object)** en lugar de una **entidad de dominio** directamente.  

---

### 🔍 **¿Por qué usar un DTO en el caso de uso?**
1. **Encapsulación:** Evita exponer directamente la entidad de dominio y sus métodos.
2. **Separación de responsabilidades:** El caso de uso solo debe manejar datos de entrada y lógica de aplicación.
3. **Evolución del sistema:** Permite cambiar la estructura interna de la entidad sin afectar el caso de uso.
4. **Validación:** Puedes validar los datos antes de convertirlos en una entidad.

---

## ✅ **Ejemplo con DTO en Python**
Aquí se muestra cómo debe estructurarse correctamente el caso de uso `UpdateDiscount` en **Python**.

### 📌 **1. DTO**
```python
# src/application/dtos/update_discount_dto.py
from dataclasses import dataclass

@dataclass
class UpdateDiscountDTO:
    id: str
    percentage: float
```

---

### 📌 **2. Caso de Uso con DTO**
```python
# src/application/use_cases/update_discount.py
from src.application.dtos.update_discount_dto import UpdateDiscountDTO
from src.domain.repositories.discount_repository import DiscountRepository

class UpdateDiscount:
    def __init__(self, repository: DiscountRepository):
        self.repository = repository

    def execute(self, dto: UpdateDiscountDTO):
        discount = self.repository.get_by_id(dto.id)

        if not discount:
            raise ValueError("Discount not found")

        discount.update_percentage(dto.percentage)
        self.repository.update(discount)

        return discount
```

---

## **🔴 Ejemplo incorrecto (sin DTO)**
```python
# ❌ Esto es una mala práctica, ya que expone directamente la entidad
from src.domain.entities.discount import Discount
from src.domain.repositories.discount_repository import DiscountRepository

class UpdateDiscount:
    def __init__(self, repository: DiscountRepository):
        self.repository = repository

    def execute(self, discount: Discount):
        existing_discount = self.repository.get_by_id(discount.id)

        if not existing_discount:
            raise ValueError("Discount not found")

        existing_discount.update_percentage(discount.percentage)
        self.repository.update(existing_discount)

        return existing_discount
```
🔴 **Problema:** Expone la entidad de dominio al caso de uso, lo que rompe la separación de responsabilidades.

---

## **💡 Conclusión**
✅ Usa **DTOs** en los **casos de uso** para mantener **limpieza y desacoplamiento** en la arquitectura hexagonal.  
✅ La **entidad de dominio** solo se debe manejar dentro del **repositorio y la capa de dominio**.  

---

Sí, **lo correcto** es utilizar un `DiscountOutputDTO` en lugar de `DiscountDTO` para la salida del caso de uso.  

---

## ✅ **¿Por qué usar un DTO de salida en lugar de la entidad de dominio?**
1. **Separación de capas:** El dominio no debe ser afectado por cambios en la presentación o API.
2. **Evitar fugas de dominio:** Si la entidad `Discount` cambia, el DTO protege el resto del sistema de esos cambios.
3. **Flexibilidad:** Puedes transformar la salida antes de exponerla (ej. cambiar nombres de campos o tipos de datos).
4. **Seguridad:** Puedes excluir datos sensibles (ej. IDs internos o timestamps de auditoría).

---

## **📌 Implementación correcta con `DiscountOutputDTO`**
### 📂 **Estructura**
```
src/
│── application/
│   ├── dtos/
│   │   ├── create_discount_dto.py
│   │   ├── discount_output_dto.py  # ✅ DTO de salida
│   ├── use_cases/
│   │   ├── create_discount.py
│── domain/
│   ├── entities/
│   │   ├── discount.py
│── infrastructure/
│   ├── persistence/
│   │   ├── repositories/
│   │   │   ├── discount_repository.py
```

---

### **1️⃣ DTO de Salida**
```python
# src/application/dtos/discount_output_dto.py
from dataclasses import dataclass

@dataclass
class DiscountOutputDTO:
    id: str
    name: str
    percentage: float
```

---

### **2️⃣ Caso de Uso con `DiscountOutputDTO`**
```python
# src/application/use_cases/create_discount.py
from src.application.dtos.create_discount_dto import CreateDiscountDTO
from src.application.dtos.discount_output_dto import DiscountOutputDTO
from src.domain.repositories.discount_repository import DiscountRepository
from src.infrastructure.logger.discount_logger import DiscountLogger

class CreateDiscount:

    def __init__(self, repository: DiscountRepository):
        self.repository = repository

    async def execute(self, dto: CreateDiscountDTO) -> DiscountOutputDTO:

        if self.repository.get_by_name(dto.name):
            raise ValueError("There is already a discount with this name.")

        saved_discount = await self.repository.create(dto)

        DiscountLogger.log_creation(saved_discount)

        return DiscountOutputDTO(
            id=saved_discount.id,
            name=saved_discount.name,
            percentage=saved_discount.percentage
        )
```

---

### **🚀 Beneficios de esta implementación**
✅ **Independencia del dominio:** No devuelves una entidad directamente.  
✅ **Protección de datos:** Puedes modificar qué datos se exponen.  
✅ **Escalabilidad:** Si agregas más datos en `Discount`, no afectará las respuestas de la API.

---

### **💡 Conclusión**
Sí, **siempre es mejor usar un DTO de salida (`DiscountOutputDTO`)** en los casos de uso, en lugar de exponer directamente la entidad de dominio.  

---

### 🚀 **¿Quieres que te ayude a transformar este código a Java con DDD y Arquitectura Hexagonal?**