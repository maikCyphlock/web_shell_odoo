# Web Shell Odoo: Tu Consola Python en el Navegador para Debuggear Odoo Como un Pro

## ¿Alguna vez quisiste ejecutar código Python directamente en tu Odoo sin abrir la terminal?

Si eres desarrollador Odoo, sabes lo frustrante que puede ser tener que abrir un terminal SSH, conectarte al servidor y ejecutar comandos de Python para probar ideas, inspeccionar datos o debuggear problemas.

**Web Shell Odoo** cambia todo eso. Imagina tener una consola Python potente integrada directamente en tu navegador, con acceso completo al entorno de Odoo, resaltado de sintaxis y todo lo que necesitas para ser más productivo.

## ¿Qué es Web Shell Odoo?

Web Shell Odoo es un módulo de desarrollo que te proporciona:

- **Consola Python Flotante**: Ejecuta código Python con acceso directo al entorno de Odoo (`env`, `request`, etc.)
- **Visor de Logs en Tiempo Real**: Monitorea los logs de Odoo directamente desde tu navegador
- **Editor Ace Integrado**: Resaltado de sintaxis y experiencia de edición profesional
- **UI Minimalista**: Diseño moderno y plano que se integra perfectamente con el backend de Odoo

## ¿Por Qué Te Encantará Usarlo?

### 1. **Sin Más Saltos entre el Browser y la Terminal**

Antes: Abrir terminal → SSH → Python shell → Escribir código → Copiar/pegar resultado → Volver al browser
Ahora: Presiona un botón → Escribe Python en tu browser → Ves el resultado instantáneamente

### 2. **Acceso Completo a Odoo**

```python
# Ejemplos de lo que puedes hacer desde el shell:

# Buscar registros
partners = env['res.partner'].search([('customer_rank', '>', 0)])

# Crear registros
new_partner = env['res.partner'].create({
    'name': 'Nuevo Cliente',
    'email': 'cliente@ejemplo.com'
})

# Inspeccionar modelos
env.cr.execute("SELECT COUNT(*) FROM res_partner")
count = env.cr.fetchone()
```

### 3. **Logs en Vivo, Siempre Visibles**

¿Tienes un problema con un cronjob? ¿Quieres ver qué está pasando con una integración externa? El visor de logs te muestra todo en tiempo real, directamente en tu navegador. No más abriendo archivos de log gigantescos o corriendo `tail -f` en la terminal.

### 4. **Herramientas de Debug Profesionales**

El módulo incluye herramientas avanzadas:

- **ORM Profiler**: Analiza el rendimiento de tus consultas ORM
- **Explorador de Entorno**: Navega por la estructura de datos de Odoo
- **Visor de Cache**: Inspecciona y depura la caché de Odoo
- **Graph Viewer**: Visualiza las relaciones entre tus modelos

## Seguridad Sin Compromisos

Entiendo lo que estás pensando: *"¿Ejecutar Python arbitrario en el browser? ¿Es seguro?"*

La respuesta es: **Sí, con las protecciones adecuadas.**

Web Shell Odoo incluye múltiples capas de seguridad:

| Característica | Descripción | Configuración |
|----------------|-------------|---------------|
| **Audit Logging** | Todos los comandos ejecutados se registran | Automático (busca `WEB_SHELL AUDIT` en logs) |
| **Timeout** | Los comandos tienen tiempo máximo de ejecución | `ir.config_parameter` → `web_shell.timeout` (default: 30s) |
| **Patrones Bloqueados** | Comandos peligrosos están bloqueados | `ir.config_parameter` → `web_shell.blocked_patterns` |

Patrones bloqueados por defecto:
```
os.system, os.popen, subprocess, shutil.rmtree, __import__
```

## Casos de Uso Reales

### Debuggear Problemas de Producción

```python
# Encuentra registros duplicados
partners = env['res.partner'].search([])
email_counts = {}
for p in partners:
    email_counts[p.email] = email_counts.get(p.email, 0) + 1
emails_dup = [e for e, c in email_counts.items() if c > 1]
```

### Probar Nuevas Funcionalidades

```python
# Prueba un nuevo método antes de implementarlo
product = env['product.product'].search([], limit=1)
result = product.calculate_discounted_price(20)  # Tu nuevo método
```

### Migraciones de Datos

```python
# Actualiza masivamente registros
env['sale.order'].search([('state', '=', 'draft')]).write({
    'note': 'Actualizado automáticamente'
})
```

## Instalación en 3 Minutos

1. Copia el directorio `web_shell` en tu ruta de `addons` de Odoo
2. Reinicia el servidor Odoo
3. Activa el modo desarrollador en Odoo
4. Ve a **Apps** → **Actualizar Lista de Aplicaciones**
5. Busca "Web Shell" y haz clic en **Instalar**

¡Eso es todo! Ya tienes tu consola Python lista para usar.

## El Veredicto

Web Shell Odoo no es solo otra herramienta de desarrollo. Es un **cambio de juego** para los desarrolladores Odoo.

En lugar de perder tiempo cambiando entre contextos, puedes quedarte en tu flujo de trabajo natural: browser → idea → prueba → resultado.

¿Listo para boostear tu productividad como desarrollador Odoo?

**Instala Web Shell Odoo hoy y empieza a debuggear como un verdadero profesional.**

---

*Desarrollado por MAIKOL AGUILAR (@maikCyphlock) • Licencia OPL-1*
