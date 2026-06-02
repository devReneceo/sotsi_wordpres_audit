# Uso de Claude + AI Project Operations Platform (SOTSI)

## ¿Qué es esto?

Claude ya está conectado al sistema de gestión de proyectos de SOTSI mediante nuestra plataforma interna.

El objetivo es simplificar la administración del proyecto utilizando IA como interfaz principal.

En lugar de abrir el CRM constantemente para actualizar tareas o generar reportes, podemos hacerlo conversando con Claude en lenguaje natural.

Claude puede:

* Consultar tareas
* Consultar avance del proyecto
* Crear tareas
* Actualizar tareas
* Registrar bloqueos
* Generar reportes
* Generar minutas
* Mantener una memoria histórica del proyecto
* Ayudar a planificar trabajo futuro

---

# Regla Principal

Hablen con Claude como si fuera un miembro más del equipo.

No es necesario conocer comandos técnicos ni nombres de herramientas.

Simplemente describan lo que hicieron o necesitan.

> Tip: cuando pregunten por "sus" tareas, mencionen su nombre (ej. "What's assigned to Joel?"), porque el sistema identifica a las personas por nombre.

---

# Registrar Avance Diario

Al finalizar el día:

Ejemplo:

Today I completed:

* Contact Form
* ActiveCampaign Integration

I was blocked by API Access.

Update my tasks and add a journal entry.

Claude puede:

* Actualizar tareas
* Registrar bloqueos
* Actualizar el Journal del proyecto
* Generar un resumen diario

---

# Consultar Trabajo Pendiente

Ejemplos:

What tasks are assigned to me?

What should I work on next?

What are my priorities this week?

Do I have any blocked tasks?

---

# Crear Nuevas Tareas

Ejemplo:

For SOTSI:

Create a task to implement SEO, AEO and GEO on the new website.

Estimate the effort in hours and assign it to Joel.

Claude puede:

* Crear la tarea
* Estimar el esfuerzo (horas aproximadas de la tarea)
* Asignar responsables
* Definir prioridad
* Agregar criterios de aceptación (en la descripción)

---

# Después de una Reunión

Simplemente pegar las notas o transcripción.

Ejemplo:

Please review these meeting notes and:

* Extract action items
* Create missing tasks
* Assign owners
* Estimate effort
* Generate a summary

[PEGAR REUNIÓN]

Claude puede:

* Crear tareas automáticamente
* Detectar responsables
* Registrar fechas y decisiones importantes en la memoria del proyecto
* Generar minuta
* Registrar decisiones importantes

---

# Reportar Problemas o Bloqueos

Ejemplo:

The Homepage cannot be completed because the client has not provided images.

Please update the project and mark the task as blocked.

Claude puede:

* Marcar tareas bloqueadas
* Registrar riesgos
* Actualizar el contexto del proyecto

---

# Generar Reportes

Ejemplos:

Generate my weekly report.

Summarize my work from the last 7 days.

Generate a project status report.

What's the overall progress and what's blocked?

---

# Memoria del Proyecto

Una de las ventajas más importantes es que Claude puede ayudar a mantener memoria histórica del proyecto.

Por ejemplo:

* Decisiones tomadas en reuniones
* Riesgos identificados
* Bloqueos importantes
* Cambios de alcance
* Estrategias aprobadas

Esto permitirá que futuras conversaciones tengan más contexto y que los reportes sean más precisos.

---

# Buenas Prácticas

✅ Registrar avances diariamente.

✅ Pegar minutas o notas de reuniones.

✅ Reportar bloqueos cuando ocurran.

✅ Registrar trabajo terminado el mismo día.

✅ Pedir a Claude generar resúmenes semanales.

✅ Utilizar lenguaje natural.

---

# Objetivo Final

Mantener una fuente centralizada de información del proyecto donde:

* Las tareas estén actualizadas.
* Las reuniones queden documentadas.
* Las decisiones importantes queden registradas.
* Los reportes puedan generarse automáticamente.

Mientras más utilicemos Claude para registrar avances y reuniones, más útil y precisa será la memoria histórica del proyecto y más fáciles serán los reportes futuros.

---

# Próximamente (en desarrollo, todavía NO disponible)

Estas funciones aún no están listas. Por favor no dependan de ellas todavía:

* **Registro de horas trabajadas (time tracking)** — registrar las horas reales que cada persona dedica por día/semana y poder preguntar "¿cuántas horas registré esta semana?". Hoy el sistema solo guarda un **estimado de esfuerzo** por tarea, no las horas trabajadas.
* **Fechas límite en tareas** — asignar y dar seguimiento a due-dates por tarea con recordatorios. Por ahora las fechas importantes se guardan en la memoria/journal del proyecto, no como vencimiento de cada tarea.
