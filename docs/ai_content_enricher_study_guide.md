# Documentación Técnica y Guía de Estudio: Módulo AiContentEnricher

Esta documentación recopila de manera integral la arquitectura, diseño, implementación, pruebas, análisis de dependencias estáticas y control de versiones del módulo `AiContentEnricher`, desarrollado dentro del proyecto backend `content-enrichment-backend`.

> ### ⚠️ Estado actual tras la refactorización MVP
>
> Esta guía describe la primera versión del módulo. Los siguientes puntos han
> cambiado y son los vigentes:
>
> | Antes | Ahora |
> |---|---|
> | `enrich_content` y `summarize_content` duplicaban el 95 % del código | Cada método conserva su propio prompt y sus parámetros de generación |
> | `except Exception: return text` (fallo silencioso) | Sin cambios: el fallo se registra en el log (`IA no disponible`) y se devuelve el texto original sin interrumpir el flujo |
> | Funciones de módulo `texto_valido` / `ajustar_longitud` | Métodos privados `_is_valid_text` / `_adjust_length` (la cobertura se prueba por el comportamiento público) |
> | Modelo hardcodeado en la firma | Sin cambios: valor por defecto `openai/gpt-oss-120b` en la firma de cada método |
> | `examples/demo_enricher_flow.py` y `scripts/check_models.py` | **Eliminados**: duplicaban la CLI o eran diagnóstico auxiliar |
>
> **Documentación vigente:** `README.md` (sección 🐛 Solución de problemas) y
> `docs/historias_usuario.md` (HU-07).

---

## 1. Definición y Propósito del Sistema

### ¿Qué es esta herramienta?
`AiContentEnricher` es un servicio backend desarrollado en Python encargado de transformar y elevar la calidad pedagógica de contenidos textuales (procedentes del módulo de scraping de Wikipedia) mediante Modelos de Lenguaje Grande (LLMs). 

### ¿Qué problema resuelve?
* **Ampliación didáctica:** Convierte resúmenes o párrafos enciclopédicos concisos en explicaciones ricas en conceptos clave, fórmulas técnicas y contexto histórico.
* **Tolerancia a fallos (*Graceful Degradation*):** Garantiza que la aplicación nunca se interrumpa por caídas de red, cuotas agotadas o errores de API; si la inteligencia artificial falla, el sistema devuelve intacto el texto original sin provocar errores críticos.
* **Control de decisiones del usuario:** Ofrece un punto de decisión en memoria donde el usuario revisa la salida generada y decide explícitamente si conserva el texto enriquecido por la IA o prefiere mantener la versión original antes de continuar en el pipeline.

---

## 2. Conceptos Clave y Glosario Técnico

* **Degradación Elegante (*Graceful Degradation*):** Capacidad de un sistema de continuar funcionando a un nivel reducido en lugar de colapsar cuando parte de sus componentes externos fallan.
* **Mocking:** Técnica de pruebas unitarias que simula el comportamiento de servicios externos (como la API de OpenAI o Groq) para evaluar la lógica interna sin realizar peticiones reales a la red ni consumir saldo.
* **Hardcoding vs. Parametrización Dinámica:** Se denomina *hardcoding* a la mala práctica de incrustar valores fijos o sensibles (como contraseñas, URLs o textos de negocio) directamente en el código fuente productivo. En contraste, un sistema desacoplado consume configuraciones mediante variables de entorno, inyección de dependencias o parámetros con valores predeterminados.
* **Conventional Commits:** Estándar formal para redactar mensajes de confirmación en Git (por ejemplo: `feat:`, `test:`, `refactor:`, `chore:`), facilitando la trazabilidad y la integración continua.
* **Inferencia de LLM:** Proceso mediante el cual un modelo de lenguaje procesa un texto de entrada (*prompt*) y calcula la respuesta probabilística correspondiente.
* **Groq Cloud:** Plataforma de cómputo de inferencia que proporciona compatibilidad total con la especificación de la API de OpenAI, permitiendo utilizar modelos abiertos de alta potencia a latencias mínimas.

---

## 3. Arquitectura del Módulo y Diagrama de Flujo

### Gráfico del Flujo Lógico

```mermaid
flowchart TD
    Start([Inicio: Enriquecer con IA]) --> TakeMem[/El sistema toma el texto guardado en memoria/]
    
    TakeMem --> CheckEmpty{¿La memoria esta vacia?}
    
    CheckEmpty -- Si --> LogEmpty[Log: Memoria vacia]
    LogEmpty --> ReturnOrig[Devolver el texto original sin cambios]
    
    CheckEmpty -- No --> CheckLen{¿El texto es demasiado largo y supera el limite de lectura de la IA?}
    
    CheckLen -- Si --> Trim[El sistema recorta el texto a un tamaño seguro]
    Trim --> SendAI[El sistema envia el texto a la IA]
    CheckLen -- No --> SendAI
    
    SendAI --> CheckSuccess{¿La IA respondio correctamente?}
    
    CheckSuccess -- Servidor caido --> LogFail[Log: IA no disponible]
    LogFail --> ReturnOrig
    
    CheckSuccess -- Exito --> Recv[Recibe el texto ampliado hasta 10000 caracteres]
    
    Recv --> LogSuccess[Log: IA respondio con exito]
    Recv --> Pause[Pausa: Presiona ENTER para continuar]
    
    Pause --> AskUser[/El sistema pregunta al usuario qué version conservar/]
    LogSuccess --> AskUser
    
    AskUser --> Choice{¿Que eligio el usuario?}
    
    Choice -- Opcion 1 --> KeepAI[Se queda con el texto mejorado por IA]
    Choice -- Opcion 2 --> KeepOrig[Se queda con el texto original]
    
    KeepAI --> FinalReady([Texto listo en memoria])
    KeepOrig --> FinalReady
    ReturnOrig --> FinalReady
```
## 4. Implementación del Código Productivo

### Archivo: `src/enricher.py`

```python
import logging
import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

# Logger configurado según las especificaciones del flujo
logger = logging.getLogger(__name__)
if not logger.handlers:
    handler = logging.StreamHandler()
    formatter = logging.Formatter("[%(levelname)s] %(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)


class AiContentEnricher:
    """Servicio responsable de enriquecer y resumir texto mediante modelos de IA."""

    def __init__(self, api_key: str | None = None, base_url: str | None = None) -> None:
        """Inicializa el cliente OpenAI validando credenciales y URL base."""
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.base_url = base_url or os.getenv("OPENAI_BASE_URL")

        if not self.api_key:
            raise ValueError(
                "API key not found. Ensure it is configured in .env or passed to constructor."
            )

        self.client = OpenAI(
            api_key=self.api_key,
            base_url=self.base_url,
        )

    def _is_valid_text(self, text: str | None) -> bool:
        """Valida que la entrada contenga caracteres no vacíos."""
        if not text or not isinstance(text, str):
            return False
        return bool(text.strip())

    def _adjust_length(self, text: str, max_characters: int = 10000) -> str:
        """Recorta de forma segura el texto si supera la longitud máxima."""
        if len(text) > max_characters:
            return text[:max_characters].strip()
        return text

    def enrich_content(self, text: str, model: str = "qwen/qwen3.8-27b") -> str:
        """Enriquece el contenido pedagógicamente invocando la IA."""
        if not self._is_valid_text(text):
            logger.warning("Memoria vacía")
            return text

        prepared_text = self._adjust_length(text)

        system_prompt = (
            "Eres un asistente educativo especializado en investigación y síntesis académica. "
            "Tu tarea es enriquecer el contenido proporcionado: amplía los conceptos clave, "
            "añade contexto histórico o técnico relevante y organiza la información con claridad, "
            "manteniendo un tono didáctico, riguroso y estructurado."
        )

        try:
            response = self.client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"Contenido a enriquecer:\n\n{prepared_text}"},
                ],
                temperature=0.7,
            )
            enriched_content = response.choices[0].message.content
            if enriched_content:
                logger.info("IA respondió con éxito")
                return enriched_content.strip()

            logger.warning("IA no disponible")
            return text
        except Exception:
            logger.warning("IA no disponible")
            return text

    def summarize_content(self, text: str, model: str = "qwen/qwen3.8-27b") -> str:
        """Genera un resumen analítico estructurado a partir del texto de entrada."""
        if not self._is_valid_text(text):
            logger.warning("Memoria vacía")
            return text

        prepared_text = self._adjust_length(text)

        system_prompt = (
            "Eres un asistente educativo especializado en síntesis de información. "
            "Tu tarea es generar un resumen conciso y estructurado del contenido proporcionado, "
            "destacando los puntos principales, definiciones clave y conclusiones esenciales."
        )

        try:
            response = self.client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"Contenido a resumir:\n\n{prepared_text}"},
                ],
                temperature=0.5,
            )
            summary = response.choices[0].message.content
            if summary:
                logger.info("IA respondió con éxito")
                return summary.strip()

            logger.warning("IA no disponible")
            return text
        except Exception:
            logger.warning("IA no disponible")
            return text
        ```
```
---
# 5. Auditoría de Buenas Prácticas: Desacoplamiento y Cero Hardcoding
Uno de los pilares de este desarrollo es garantizar que ningún dato crítico o de negocio quede acoplado en el código:
## 1. En el módulo productivo (src/enricher.py)
Credenciales 100% dinámicas: No existen claves de API ni URLs expuestas en el código fuente. Se recuperan en tiempo de ejecución desde variables de entorno con os.getenv().

2. Inyección de dependencias: La clase AiContentEnricher admite parámetros opcionales (api_key, base_url) en su constructor __init__, permitiendo conectarse a diferentes proveedores sin modificar su código.

3. Modelo configurable: El parámetro model dispone de un valor predeterminado funcional ("qwen/qwen3.8-27b"), pero puede sobreescribirse en cada llamada al método si se requiere otro modelo.

4. Límites parametrizables: El límite de seguridad de caracteres cuenta con un valor por omisión (max_characters=10000) ajustable según las necesidades de la capa superior.

## 2 . En el script de demostración interactiva (examples/demo_enricher_flow.py)
No contiene temas fijos ni textos precargados: solicita dinámicamente el concepto al usuario mediante input() por consola con validación de no vacíos.

## 3. En la suite de pruebas (tests/test_enricher.py)
Emplea cadenas ficticias para claves de prueba ("sk-fake-test-key") y respuestas simuladas ("Texto enriquecido por IA"), aislándose estrictamente de llamadas reales a la red mediante mocks.

# 6. Configuración de Entorno e Integración con Groq Cloud
Para dotar al sistema de respuestas de IA en tiempo real sin incurrir en costes, se integró el proveedor Groq a través de variables de entorno:
Archivo .env
```
OPENAI_API_KEY=gsk_**************************************
OPENAI_BASE_URL=[https://api.groq.com/openai/v1](https://api.groq.com/openai/v1)
```
Modelo seleccionado: Se configuró qwen/qwen3.8-27b, el cual cuenta con capacidades avanzadas de síntesis didáctica y estructuración formal.

# 7. Suite de Pruebas Unitarias Automatizadas

Archivo: tests/test_enricher.py
Se implementó una batería de 8 tests unitarios con pytest y unittest.mock para verificar de forma aislada e instantánea todos los caminos de ejecución:

## 1.test_initialization_without_key:
Comprueba que se lance ValueError si falta la clave de API.

## 2.test_is_valid_text:
Verifica que cadenas vacías o con solo espacios no sean procesadas.

## 3.test_adjust_length:
Comprueba que textos extensos se recorten estrictamente al límite de seguridad (10.000 caracteres).

## 4.test_enrich_content_invalid_text:
Garantiza que entradas inválidas devuelvan el texto original.

## 5.test_enrich_content_success: 
Valida mediante un mock que la respuesta enriquecida sea extraída y devuelta con éxito.

## 6.test_enrich_content_fallback_error:
Simula un error de red 500 y comprueba que se active la degradación elegante devolviendo el texto original.

## 7.test_summarize_content_success: 
Comprueba la generación y retorno de resúmenes estructurados.

## 8.test_summarize_content_fallback_error: 
Comprueba la degradación elegante en el método de resumen ante caídas de la API.

Resultado de ejecución:
```
python -m pytest -v
============================= 8 passed in 1.67s =============================
```
(Todos los tests aprobados al 100%)[cite: 2].

# 8. Demostración Interactiva en Vivo (Live Demo)
Para la defensa técnica del proyecto ante el equipo y evaluadores, se estructuró un script específico dentro de la carpeta examples/ que solicita el texto por consola de forma dinámica:
Archivo: examples/demo_enricher_flow.py
```
import sys
from pathlib import Path

# Permite resolver importaciones de 'src' independientemente del directorio de ejecución
sys.path.append(str(Path(__file__).resolve().parent.parent))

from src.enricher import AiContentEnricher


def run_manual_flow():
    print("=" * 60)
    print("INTERACTIVE LIVE DEMO: AI CONTENT ENRICHER")
    print("=" * 60)

    # 1. Solicita dinámicamente el texto al usuario por terminal
    original_text = ""
    while not original_text:
        original_text = input("\nIntroduce el texto o concepto a enriquecer: ").strip()
        if not original_text:
            print("⚠️️ El texto no puede estar vacío. Por favor, escribe un concepto.")

    print("\n[Texto capturado dinámicamente]:")
    print(original_text)

    enricher = AiContentEnricher()

    # 2. Solicitud de enriquecimiento a la IA
    print("\nSending text to AI...")
    enriched_text = enricher.enrich_content(original_text)

    print("\n[Result returned by module]:")
    print(enriched_text)

    # 3. Pausa controlada para revisión pedagógica
    input("\nPause: Press ENTER to continue...")

    # 4. Decisión interactiva del usuario
    print("\nSystem question:")
    print("¿Qué versión quieres conservar?")
    print("Option 1: Enriquecida por la IA")
    print("Option 2: Original")

    choice = input("Select an option (1 or 2): ").strip()

    # 5. Asignación definitiva en memoria
    if choice == "1":
        final_memory_text = enriched_text
        print("\n✔ Selected AI enriched text.")
    else:
        final_memory_text = original_text
        print("\n✔ Selected original text.")

    print("\n[Final text ready in memory for next step]:")
    print(final_memory_text)
    print("\n" + "=" * 60)


if __name__ == "__main__":
    run_manual_flow()
```
# 9. Registro de Commits y Control de Versiones

Todo el proceso de desarrollo en la rama feature/aiContentEnricher fue registrado con trazabilidad estricta bajo el estándar Conventional Commits:   
```
test: add unit tests with mocks for enricher module (aa2c720)[cite: 1]
Creación de tests/test_enricher.py cubriendo validaciones, recortes, llamadas simuladas y tolerancia a fallos[cite: 1].
```
```
feat: add interactive flow demo script and refactor enricher methods (c066a6a)
```
```
Refactorización integral del código a inglés técnico y nomenclatura snake_case.
```
```
Incorporación de manejadores de logging según estados de flujo ([INFO] y [WARNING]).
```
```
Creación del directorio examples/ y adición inicial de la demo.
```
```
chore: remove redundant manual test file from root (1efd670
Limpieza del archivo temporal duplicado en la raíz para mantener la estructura del repositorio ordenada y limpia
```
```
feat: make demo enricher script dynamic with interactive terminal prompt
Adaptación del script de demo para capturar el concepto en vivo por consola sin hardcoding.
```
```
docs: add comprehensive study guide and technical architecture for aiContentEnricher
Incorporación del manual técnico completo con diagrama de flujo integrado.
```
## 10. Comandos de Referencia
Ejecutar todos los tests unitarios:
```
python -m pytest -v
```
Ejecutar la demostración interactiva en vivo:
```
python examples/demo_enricher_flow.py
```
Verificar el estado limpio del repositorio:
```
git status
```
Publicar la rama en GitHub (cuando el equipo dé la aprobación final):
```
git push origin feature/aiContentEnricher
```
---


---

## 🧪 Criterios de Aceptación y Escenarios BDD (Gherkin)

Para validar que el módulo cumple con todos los requerimientos funcionales y de resiliencia esperados por el equipo, el comportamiento del sistema se estructuró bajo especificaciones Gherkin, respaldadas al 100% por la suite de pruebas unitarias automatizadas (`tests/test_enricher.py`):

### Escenario 1: Enriquecimiento pedagógico exitoso
```gherkin
Característica: Enriquecimiento pedagógico de contenido

  Escenario: La IA amplía correctamente un texto de Wikipedia
    Dado que el servicio "AiContentEnricher" dispone de credenciales válidas
    Y recibe un texto válido sobre un concepto de estudio
    Cuando el sistema solicita el enriquecimiento al modelo de lenguaje
    Entonces el servicio devuelve el contenido ampliado con explicaciones didácticas
    Y emite un log informativo de éxito en la consola
```
Validación técnica: Cubierto en test_enrich_content_success con respuesta mockeada.

### Escenario 2: Generación de resumen estructurado

```
Escenario: La IA sintetiza el contenido en un resumen didáctico
    Dado que el módulo recibe un artículo o sección extensa
    Cuando solicita la función de resumen
    Entonces la IA devuelve un párrafo conciso con las ideas clave destacadas
    Y preserva la coherencia y fidelidad del contenido original

```
### Escenario 4: Validación de entradas vacías o no válidas

```
Escenario: Recepción de contenido nulo o compuesto únicamente por espacios
    Dado que el módulo recibe una entrada de texto vacía
    Cuando se ejecuta el filtro preventivo de validación
    Entonces emite el aviso "[WARNING] Memoria vacía"
    Y evita realizar llamadas innecesarias a la red o consumo de API
```
Validación técnica:
Cubierto en test_enrich_content_empty_text.

### Escenario 5: Decisión interactiva de persistencia en memoria (Live Demo)

```
Escenario: El usuario elige en consola la versión final a procesar
    Dado que el usuario visualiza en terminal la comparativa de textos
    Cuando selecciona conservar la versión enriquecida o la original
    Entonces la variable de memoria del sistema almacena la opción elegida
    Y confirma en pantalla que el texto queda listo para las siguientes fases
```
Validación técnica:
Verificado en el script ejecutable examples/demo_enricher_flow.py.

## Configuración Técnica y Resiliencia del Módulo AI

### 1. Proveedor e Inferencia Compatible (Groq / OpenAI API)
El módulo `AiContentEnricher` utiliza el cliente de OpenAI configurado contra el endpoint de inferencia de Groq mediante variables de entorno:
- `OPENAI_BASE_URL`: `https://api.groq.com/openai/v1`
- `OPENAI_API_KEY`: Clave de acceso a Groq.

#### Modelos de Texto Habilitados vs. Especializados
El catálogo de modelos disponibles varía según el nivel de suscripción y cambios de API. Se debe diferenciar entre modelos aptos para generación/síntesis textual y modelos de tareas específicas:
- **Aptos para Chat y Enriquecimiento:**
  - `qwen/qwen3.8-27b` (Modelo predeterminado por su capacidad didáctica y estructuración).
  - `openai/gpt-oss-120b` (Alternativa de alto rendimiento para textos extensos).
  - `openai/gpt-oss-20b` (Alternativa ligera y de baja latencia).
- **No Aptos para este Flujo:**
  - `whisper-large-v3` / `whisper-large-v3-turbo` (Exclusivos para transcripción de audio).
  - `meta-llama/llama-prompt-guard-*` y modelos `safeguard` (Filtros de moderación y seguridad, no devuelven contenido enriquecido).

> **Herramienta de Diagnóstico (`check_models.py`):**  
> Se incluye un script auxiliar en la raíz para consultar en tiempo real los identificadores exactos de los modelos habilitados para la clave en uso:
> ```bash
> python check_models.py
> ```

---

### 2. Prevención de Truncamiento (`max_tokens`)
Para evitar cortes abruptos en respuestas complejas (por ejemplo, en secciones de conclusiones o esquemas analíticos largos), se especifica de forma explícita el parámetro `max_tokens` en las llamadas a `chat.completions.create`:
- **`enrich_content`**: `max_tokens=4096` para permitir un desarrollo exhaustivo y contextualizado.
- **`summarize_content`**: `max_tokens=1500` para garantizar resúmenes concisos pero completos.

---

### 3. Arquitectura de Resiliencia (*Graceful Degradation*)
El servicio implementa una estrategia de tolerancia a fallos ante caídas de red, problemas de cuota o errores 404 de modelo:
1. **Validación Previa:** Comprueba que el texto de entrada no esté vacío ni compuesto únicamente de espacios en blanco mediante `_is_valid_text()`.
2. **Control de Longitud:** Limita el tamaño de entrada mediante `_adjust_length()` para no saturar la ventana de contexto.
3. **Fallback Automático:** En caso de excepción durante la petición HTTP, el error se captura, se registra con nivel `WARNING` en el logger del sistema y la función devuelve el texto original intacto, garantizando que el flujo de la aplicación no se detenga.

---

### 4. Guía de Ejecución de Pruebas
Para evitar problemas de resolución de rutas (`ModuleNotFoundError: No module named 'src'`) al ejecutar la suite de pruebas unitarias y de integración desde terminales de sistema (como PowerShell o Bash):
- **Ejecución recomendada:**
  ```bash
  python -m pytest
  
Modo detallado:

```
python -m pytest -v

```







