# Primera clase

1. Elijan salas, computadoras o tutorías y asignen las tareas de la sección 5 de la guía.
2. Antes de editar el código, creen **un único repositorio de GitHub por equipo** y den acceso a cada integrante y al docente. Pueden trabajar en un repositorio privado.
3. Un integrante crea la copia del equipo. Para una copia pública, abran el [repositorio base del curso](https://github.com/javierdastas/comp2053), seleccionen **Fork**, escojan un nombre y pulsen **Create fork**. Continúen con el paso 4. Para un repositorio privado o independiente, [descarguen el código base en ZIP](https://github.com/javierdastas/comp2053/archive/refs/heads/main.zip), extráiganlo y creen un repositorio vacío en GitHub. Desde la carpeta que contiene este archivo, ejecuten los siguientes comandos. Sustituyan `URL_DEL_EQUIPO` por la dirección HTTPS del nuevo repositorio.

```bash
git init -b main
git add .
git status --short
git commit -m "Inicia el proyecto con la base del curso"
git remote add origin URL_DEL_EQUIPO
git push -u origin main
```

4. Cada integrante que necesite su copia local clona el repositorio **del equipo** con `git clone URL_DEL_EQUIPO`. Comprueben que GitHub muestra los archivos dentro de `codigo/sql`, los formularios y las pruebas. Abran una rama para su primera tarea y acuerden quién la revisará. [Procedimiento de GitHub en la guía](Leccion_fullstack.md#repositorio-github-obligatorio-y-copia-de-la-base)
5. Sigan la instalación desde `codigo`. Elijan una sola variante SQL. Para las credenciales de desarrollo, creen archivos locales excluidos de Git. [Instalación](codigo/README.md)
6. Al final del encuentro registren qué funcionó, qué queda por construir y en qué archivo retomarán el trabajo. [Bitácora](plantillas/Bitacora_equipo.md)

## Qué deben desarrollar

El código inicial permite ejecutar y estudiar el flujo completo. En su copia, adapten los datos, construyan el filtro del listado descrito en la etapa 6, comprueben una decisión de interfaz y añadan una prueba propia. Identifiquen en sus pull requests la parte que implementaron y el resultado que obtuvieron. [Tutorial y rúbricas](Leccion_fullstack.md)
