# Desarrollo de una aplicación fullstack de reservas

Guía de clase en formato de tutorial para estudiantes del curso COMP2053 Fullstack Development.

Trabajarán en equipos de dos o tres personas para construir una aplicación que capture datos, compruebe disponibilidad, registre reservas y produzca un resumen diario. Elegirán uno de tres contextos. Los tres usan el mismo código y exactamente tres tablas. Al terminar, publicarán obligatoriamente el código en un repositorio de GitHub del equipo, entregarán una versión reproducible y explicarán sus decisiones mediante un video con demostración y un PowerPoint que pueda entenderse por sí solo.

## 1 ¿Cómo usar esta guía?

Luego de leer esta sección, lee detalladamente las secciones 2 a 6. Después desarrolla las etapas 1 a 8 en orden. Cada etapa presenta una meta, conceptos, acciones, una comprobación y una evidencia. Marca las comprobaciones antes de avanzar. Si algo falla, conserva el mensaje de error y consulta la sección de diagnóstico.

La carpeta `codigo` contiene una implementación completa de referencia, incluidos los SQL y las pruebas. Puedes ejecutarla al inicio para observar el resultado. Para aprender, construye tu copia por etapas, explica los fragmentos y realiza las pequeñas actividades señaladas. El código completo evita que una dificultad de transcripción detenga el aprendizaje. Copiarlo sin comprenderlo no demuestra las destrezas de la unidad.

**Ruta de trabajo.** Elegir proyecto; crear el repositorio del equipo en GitHub; acordar tareas; diseñar datos; crear base; conectar Flask; construir API; integrar interfaz; probar; documentar y presentar.

**Cómo retomar después de una pausa.** Deja escrito: archivo que estabas editando, último paso que funcionó, error pendiente y siguiente acción concreta. Al regresar, ejecuta primero la última comprobación que pasó.

## 2 Lo que aprenderás y cómo lo demostrarás

Al finalizar podrás:

1. Modelar personas, recursos y reservas con claves primarias, foráneas y restricciones de unicidad. Evidencia: diagrama y SQL ejecutable.
2. Implementar una API con Flask y SQLAlchemy que valide, persista y consulte datos. Evidencia: respuestas JSON y pruebas de casos válidos e inválidos.
3. Integrar formularios, JavaScript y AJAX para actualizar la interfaz sin recargar la página. Evidencia: una reserva visible inmediatamente y una solicitud en Network.
4. Aplicar decisiones UX accesibles y una distribución responsive. Evidencia: recorrido por teclado, mensajes comprensibles y comprobación en pantalla estrecha.
5. Procesar los registros (récords) mediante agrupaciones y porcentajes. Evidencia: resumen cuyo resultado coincida con un cálculo manual.
6. Explicar el recorrido de un dato y colaborar con una carga razonablemente equivalente. Evidencia: video, PowerPoint, bitácora y revisiones cruzadas.

**Activación de conocimientos previos, 10 minutos.**

- Dibuja qué ocurre al enviar un formulario HTML tradicional. Luego señala qué parte cambia al usar en jQuery `$.ajax` o `$.get` (en Javascript sería el comando `fetch`).
- Explica la diferencia entre clave primaria y foránea. No necesitas aprender otro lenguaje ni otro framework para esta unidad.

## 3 Elige uno de los tres proyectos

| Aspecto | A - Reservas de salas | B - Préstamo de computadoras | C - Citas de tutoría |
|---|---|---|---|
| Persona que solicita | Estudiante responsable | Estudiante que toma el equipo | Estudiante que recibe tutoría |
| Una fila de recursos | Una sala física | Una computadora con identificador único | Una persona tutora |
| Campo categoria | Tipo de sala | Tipo de equipo | Materia que atiende el tutor |
| Ejemplo de recurso | Sala A102 | Laptop EQ002 | Sam Torres |
| Ejemplo de categoría | Trabajo colaborativo | Linux | Bases de datos |
| Ejemplo de motivo | Preparar exposición del curso | Practicar consultas SQL | Repasar relaciones entre tablas |
| Script a ejecutar | sql/salas.sql | sql/equipos.sql | sql/tutorias.sql |
| PROYECTO en .env | salas | equipos | tutorias |
| DB_NAME en .env | fullstack_salas | fullstack_equipos | fullstack_tutorias |

- **A · Salas.** Una reserva bloquea la sala completa. Se registra a una persona responsable, no a cada asistente. El prototipo no administra capacidad ni asistencia.
- **B · Computadoras.** Se presta una unidad identificable durante una hora. EQ001 y EQ002 son unidades diferentes aunque tengan el mismo sistema operativo. El prototipo no administra entrega física, devolución tardía ni multas.
- **C · Tutorías.** Cada tutor aparece una sola vez y atiende una sola materia en este prototipo. La opción del formulario muestra nombre y materia, por lo que elegirla selecciona ambos. No dupliques al mismo tutor con otra materia: eso permitiría reservar a la misma persona dos veces. Administrar varias materias por tutor necesitaría rediseñar el modelo y queda fuera de esta unidad.

**Elección del equipo de trabajo.** Escriban el proyecto, sus integrantes y una razón relacionada con sus intereses. La opción elegida no cambia la cantidad de funcionalidades, las pruebas ni los puntos disponibles.

### ¿Qué es un .env?

Un archivo **.env** es un archivo de texto donde guardas la configuración que una aplicación necesita para funcionar en tu computadora. Su nombre viene de environment, que significa “ambiente”. En el proyecto de reservas, por ejemplo, Flask lee este archivo al iniciar para saber qué base de datos debe usar.

Cada línea tiene el formato `NOMBRE=valor`. Para el proyecto de salas, dos de esas líneas serían:

```text
PROYECTO=salas
DB_NAME=fullstack_salas
```

La primera línea selecciona el proyecto de salas y la segunda indica el nombre de su base de datos. Si tu equipo elige tutorías, cambia los valores a tutorias y fullstack_tutorias. Así puedes usar el mismo código para ambos proyectos.

### ¿Qué se sube a GitHub?

En GitHub se comparte `.env.example`, una plantilla con los nombres de las variables y valores de ejemplo. Cada integrante hace una copia en su computadora, la llama `.env` y escribe allí su configuración. Guarda la contraseña solo en esa copia local. El proyecto ya incluye un archivo `.gitignore` que le indica a Git que ignore `.env`. Al revisar los cambios en Git, debes ver la plantilla si la editaste. Tu archivo local `.env` no debe aparecer.

## 4 Alcance y reglas comunes

La aplicación funciona como un panel local para una persona operadora que registra solicitudes ficticias. Quien aparece en `personas` es solicitante, no una cuenta autenticada. Por esta razón la base tiene tres tablas y no requiere Flask-Login. Los conocimientos previos de autenticación siguen siendo pertinentes, pero no son requisito de esta unidad.

El producto mínimo debe permitir registrar personas, mostrar recursos con su categoría, consultar horarios, crear reservas, listar las reservas de una fecha, cancelar una reserva futura y calcular un resumen diario. Los recursos se administran mediante el SQL inicial. No se exige crear una pantalla de mantenimiento del catálogo ni un CRUD completo de cada tabla.

Reglas que todos los equipos deben implementar:

- Cada reserva dura exactamente 60 minutos. Comienza en una hora exacta entre las 08:00 y las 16:00; la última termina a las 17:00.
- Todos los días tienen el mismo horario en este modelo simplificado. Se aceptan fechas desde hoy hasta hoy más 30 días, inclusive, y solo bloques que todavía no han comenzado.
- Todas las horas corresponden a Puerto Rico. La base usa `DATETIME` local bajo esta convención. La interfaz no debe convertir estas cadenas mediante la zona del navegador.
- Un recurso admite una reserva por hora. Una persona solicitante también admite una reserva por hora, aunque intente elegir otro recurso.
- El correo se recorta y convierte a minúsculas antes de guardar. No puede repetirse. El nombre admite 2 a 80 caracteres; el correo, hasta 120; el motivo, 5 a 200.
- Una cancelación elimina la fila de `reservas`, libera el bloque y actualiza el resumen. Se pide confirmación. No existe historial de cancelaciones ni estado de entrega en este alcance.
- El resumen cuenta las reservas que siguen registradas para la fecha seleccionada. Incluye los bloques de ese día que ya pasaron; por ello no representa disponibilidad restante en tiempo real.

**Decisión de arquitectura.** Una hora exacta más una duración fija permite resolver conflictos con `UNIQUE(recurso_id, inicio)`. Si el proyecto admitiera 09:30 o duraciones variables, esta regla dejaría de detectar todos los solapamientos. Ese cambio no forma parte del trabajo requerido.

**Límite de uso.** Es un prototipo educativo local con datos ficticios. Un servicio público necesitaría autenticación, autorización de operaciones y otras decisiones de despliegue. No publiques este panel como un sistema real de estudiantes. En la presentación explica esta limitación de alcance.

## 5 Organización equitativa del equipo

Usen `plantillas/Bitacora_equipo.md`. Dividan el trabajo en entregables comprobables. Una tarea incluye implementación, una comprobación y revisión de otra persona. Los puntos de esfuerzo sirven para balancear carga relativa; no son horas ni nota.

| Tarea de tres puntos | Entregable | Equipo de 2 | Equipo de 3 |
|---|---|---|---|
| T1 Requisitos y boceto | Flujo, reglas y boceto | A | A |
| T2 Modelo y SQL | Tres tablas y semillas | B | B |
| T3 Configuración y conexión | .env.example y arranque | A | C |
| T4 Captura de personas | POST y validación | B | A |
| T5 Disponibilidad | GET y bloques horarios | A | B |
| T6 Crear reservas | POST y conflictos | B | C |
| T7 Formulario y accesibilidad | HTML y CSS | A | C |
| T8 Integración AJAX | Envíos y mensajes | B | B |
| T9 Listado y cancelación | GET, DELETE e interfaz | A | A |
| T10 Resumen y pruebas | Agregación y evidencias | B | C |
| T11 Instalación y PowerPoint | README y resumen autónomo | A | B |
| T12 Guion y edición de video | Video con demo y subtítulos | B | A |

**Posibles divisiones del equipo de trabajo:** En pareja, cada integrante tiene seis tareas y 18 puntos. En un trío, cada integrante tiene cuatro tareas y 12 puntos. La responsabilidad principal no significa trabajar sin apoyo. En el video y la revisión técnica participan todos, aunque una persona integre el archivo final.

**Rotación de revisión.** En pareja, A revisa a B y B a A. En trío, A revisa a B, B a C y C a A. Cada integrante debe implementar código y revisar una parte de otra capa. Nadie queda asignado solamente a tomar notas o diseñar las diapositivas.

**Acuerdos prácticos.** Reserven diez minutos por encuentro para distribuir y cerrar tareas. Mantengan las columnas Pendiente, En curso, Para revisar y Terminado. Eviten editar simultáneamente la misma función de `app.py` o la misma parte de otro archivo; integren cambios pequeños y prueben después de cada integración. Usen obligatoriamente Git y GitHub: es recomendable utilizar un “Branch” (rama) por tarea, mensajes comprensibles y pull requests revisados antes de unir cambios. La cantidad de commits no mide por sí sola el aporte.

**Rebalanceo.** Al terminar cada encuentro comparen esfuerzo real y bloqueos. Si alguien necesita más tiempo, dividan una tarea o intercambien responsabilidades con acuerdo escrito. No se exige divulgar diagnósticos. La equidad se aprecia en complejidad, revisión, aprendizaje y evidencia, no en velocidad ni cantidad de líneas.

## 6 Apoyos para distintas formas de aprender

El diseño ofrece opciones de participación, representación y expresión, en consonancia con las orientaciones de CAST. No presupone que todos los estudiantes neurodivergentes necesiten los mismos apoyos. El docente mantiene los objetivos y conversa de forma privada sobre los apoyos individuales que correspondan. Fuente: [CAST UDL Guidelines](https://udlguidelines.cast.org/).

- El equipo decide su agenda y su ritmo de trabajo. Sigan las etapas en orden y comprueben el resultado de cada una antes de avanzar.
- Encontrarán los criterios de evaluación en la sección 16 de esta guía, también disponible en GitHub.
- Se combina explicación escrita, fragmentos de código, demostración comentada y práctica. El material editable permite ampliar texto, usar lectura asistida, asistencia de IA y cambiar la presentación visual.
- Se propone trabajar en bloques de 25 a 30 minutos y hacer pausas breves acordadas. El cronómetro es una opción, no una obligación.
- Las instrucciones nombran los archivos y los resultados esperados. Se ofrecen ejemplos completos, listas de verificación y una plantilla para dejar el siguiente paso por escrito.
- Para el trabajo en grupo; se permite participar por voz, texto, comunicación aumentativa, segmentos grabados y utilizar asistencia de IA con el fin de aclarar dudas.
- Para el código; los mensajes de la aplicación deben decir qué ocurrió y cómo continuar, sin depender únicamente de colores. Se preservan los datos cuando falla el envío.
- Pueden grabar y editar el video por segmentos. La cámara es opcional. Muestren la aplicación en ejecución e incluyan subtítulos revisados y una transcripción, como indica la rúbrica de la nota 1. Cada integrante demuestra su comprensión técnica. No se evalúan el contacto visual, la rapidez de respuesta, el acento ni la fluidez oral.

**Rutina de cada encuentro grupal.** Agenda y recuperación del trabajo pasado; explicación y demostración (si es necesario); práctica o demostración guiada (si es necesario); aplicación en equipo; revisión de acuerdos y registro de los siguientes pasos. Ajusten esta estructura según los temas acordados.

## 7 Etapa 1 - Analizar el problema y preparar el entorno

**Meta.** Explicar qué construirán y abrir el proyecto con sus herramientas listas.

**Conceptos.** Una arquitectura por capas separa responsabilidades. HTML y CSS presentan información; JavaScript responde a interacciones y realiza solicitudes; Flask expone rutas y valida; SQLAlchemy comunica objetos con tablas; MySQL o MariaDB conserva los datos. Jinja genera el HTML inicial en el servidor. Las posteriores respuestas JSON se procesan en el navegador.

**Recorrido de una reserva.** Formulario del navegador; `fetch` con JSON; ruta Flask; validación; transacción SQLAlchemy; INSERT en la base; respuesta 201; actualización del DOM y del resumen. La respuesta de error interrumpe el guardado y explica qué corregir.

**Acciones.** Desde el primer encuentro, sigan `INICIO.md` para crear el repositorio del equipo y clonarlo. Elaboren un boceto con tres secciones: registrar persona, crear reserva y consultar/cancelar. Escriban una historia: “Como persona operadora, quiero reservar un recurso para un estudiante en una hora disponible, para evitar asignaciones duplicadas”. Su aceptación exige una fila nueva, una confirmación y el bloqueo de la hora.

Instalen Git, creen o comprueben sus cuentas de GitHub, instalen Python 3.11 o posterior, un editor y MySQL 8.4 o MariaDB 10.11 o posterior. Las versiones de las dependencias fijadas en `requirements.txt` son una base de referencia, no una afirmación de que sean las más recientes.

Estructura mínima entregable:

```text
codigo/
  app.py
  models.py
  requirements.txt
  .env.example
  .gitignore
  README.md
  templates/index.html
  static/app.js
  static/styles.css
  sql/salas.sql
  sql/equipos.sql
  sql/tutorias.sql
  sql/usuario_app.sql
  tests/test_app.py
```

En VS Code, hagan clic derecho en la carpeta `codigo` y seleccionen `Open in Integrated Terminal`. Si usan otro editor, abran una terminal en esa carpeta. Ejecuten el bloque que corresponda a su sistema:

En macOS o Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
cp .env.example .env
```

En Windows PowerShell:

```powershell
py -m venv .venv
.venv\Scripts\python.exe -m pip install -r requirements.txt
Copy-Item .env.example .env
```

Si PowerShell restringe la activación, pueden ejecutar directamente `.venv\Scripts\python.exe`; no es necesario cambiar la política de todo el equipo. `tzdata` permite resolver la zona horaria también en sistemas que no traen esa base de zonas.

**Comprobación.** `python -c "import flask, flask_sqlalchemy, pymysql"` termina sin error; en Windows usa el Python del entorno. Cada persona puede describir al menos una responsabilidad de cada capa.

**Evidencia.** Guarden las capturas de pantalla y anoten las tareas realizadas y los acuerdos. Al cerrar, registren qué script SQL necesitarán en la etapa 2.

## 8 Etapa 2 - Diseñar y crear las tres tablas

**Meta.** Crear una base nueva y comprender sus relaciones.

**Conceptos.** Una clave primaria identifica una fila. Una clave foránea exige que el registro (récord) relacionado exista. `UNIQUE` impide duplicados. Una relación uno a muchos permite que una persona tenga varias reservas y que un recurso aparezca en varias reservas, en horarios diferentes.

Modelo común:

```text
personas  1 -------- N reservas N -------- 1 recursos
id PK                  id PK                  id PK
nombre                 persona_id FK          nombre UNIQUE
email UNIQUE           recurso_id FK          categoria
                       inicio
                       motivo
```

| Tabla | Campos y tipos | Función |
|---|---|---|
| personas | id INT; nombre VARCHAR(80); email VARCHAR(120) | Datos del solicitante |
| recursos | id INT; nombre VARCHAR(80); categoria VARCHAR(60) | Catálogo de salas, equipos o tutores |
| reservas | id INT; persona_id INT; recurso_id INT; inicio DATETIME; motivo VARCHAR(200) | Relación entre solicitante, recurso y bloque |

**Acciones.** Abran el SQL de su proyecto y localicen las tres sentencias `CREATE TABLE`. Identifiquen cada PK, FK y `UNIQUE`. Ejecuten únicamente la variante elegida con una cuenta que pueda crear bases. Los scripts crean una base nueva y no incluyen `DROP DATABASE`.

Con el cliente MySQL, desde `codigo`:

```bash
mysql -u root -p
```

Dentro del cliente, ejecuta una sola opción:

```sql
SOURCE sql/salas.sql;
-- Alternativas: SOURCE sql/equipos.sql; o SOURCE sql/tutorias.sql;
SHOW TABLES;
SELECT * FROM personas;
SELECT * FROM recursos;
```

En MariaDB puedes usar el comando `mariadb -u root -p`. En Workbench abre el archivo de la variante y ejecútalo completo. Si el laboratorio usa otra cuenta administradora, usa la indicada por el docente.

El núcleo de `reservas` es el mismo en las tres opciones:

```sql
CREATE TABLE reservas (
  id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
  persona_id INT NOT NULL,
  recurso_id INT NOT NULL,
  inicio DATETIME NOT NULL,
  motivo VARCHAR(200) NOT NULL,
  CONSTRAINT fk_reserva_persona
    FOREIGN KEY (persona_id) REFERENCES personas(id),
  CONSTRAINT fk_reserva_recurso
    FOREIGN KEY (recurso_id) REFERENCES recursos(id),
  CONSTRAINT uq_recurso_inicio UNIQUE (recurso_id, inicio),
  CONSTRAINT uq_persona_inicio UNIQUE (persona_id, inicio)
) ENGINE=InnoDB;
```

Este fragmento explica la tabla; no lo ejecutes de nuevo después del script completo. Los valores `NULL` no se admiten en los campos de negocio. Un índice único evita registros (récords) repetidos incluso cuando dos solicitudes llegan casi al mismo tiempo. Fuente técnica: [MySQL sobre restricciones de unicidad](https://dev.mysql.com/doc/refman/8.4/en/constraint-primary-key.html).

**Cuenta de la aplicación.** Copia `sql/usuario_app.sql` a `sql/usuario_app.local.sql`. Edita la copia local con la clave y el nombre de la base en `GRANT`. Ejecuta solo la copia con la cuenta administradora. Git excluye los archivos `*.local.sql`. Si el docente ya asignó un usuario, utiliza ese. Después copia sus datos a `.env`. La aplicación solo necesita SELECT, INSERT y DELETE en su propia base.

```text
PROYECTO=salas
DB_HOST=127.0.0.1
DB_PORT=3306
DB_NAME=fullstack_salas
DB_USER=fullstack_app
DB_PASSWORD=tu_clave_local
```

Para equipos o tutorías cambia tanto `PROYECTO` como `DB_NAME`. No compartas `.env` ni una clave real en el repositorio. Entrega `.env.example` con valores de ejemplo. La base correcta debe contener solo las semillas de tu variante.

**Aplicación de destreza.** Añadan un cuarto recurso ficticio al INSERT del SQL que entregarán. Para probarlo en la base ya creada ejecuten solo ese nuevo INSERT. En tutorías, mantengan una persona tutora única con una materia. No añadan una cuarta tabla. Después, el resumen tendrá 36 bloques posibles por día, en lugar de 27.

**Comprobación.** `SHOW TABLES` muestra exactamente `personas`, `recursos` y `reservas`. Hay dos personas iniciales, al menos cuatro recursos después de la actividad y ninguna reserva inicial. Expliquen por qué `categoria` cambia de significado sin cambiar el esquema.

**Evidencia.** Diagrama, captura o salida de las consultas, SQL actualizado y nombre del motor con su versión.

## 9 Etapa 3 - Conectar Flask y representar los datos

**Meta.** Conectar Flask con la base y reconocer la correspondencia entre clases y tablas.

**Conceptos.** Un ORM permite construir consultas mediante objetos Python. El modelo no sustituye las restricciones de la base. `commit` confirma una transacción; `rollback` descarta la transacción fallida para que la sesión pueda volver a usarse.

**Acciones.** Construyan `models.py` a partir del archivo de referencia. Relacionen cada atributo con el SQL. En particular:

```python
class Reserva(db.Model):
    __tablename__ = "reservas"
    id = db.Column(db.Integer, primary_key=True)
    persona_id = db.Column(
        db.Integer, db.ForeignKey("personas.id"), nullable=False)
    recurso_id = db.Column(
        db.Integer, db.ForeignKey("recursos.id"), nullable=False)
    inicio = db.Column(db.DateTime, nullable=False)
    motivo = db.Column(db.String(200), nullable=False)
    __table_args__ = (
        db.UniqueConstraint("recurso_id", "inicio",
                            name="uq_recurso_inicio"),
        db.UniqueConstraint("persona_id", "inicio",
                            name="uq_persona_inicio"),
    )
```

El archivo completo también incluye relaciones y `to_dict`, que transforma la reserva en datos serializables a JSON. No copies únicamente este fragmento como si fuera todo el archivo.

Construyan la configuración de `app.py` usando `create_app`. La función permite crear la aplicación normal o una instancia aislada para pruebas. La extensión se conecta después de definir la configuración:

```python
app.config["SQLALCHEMY_DATABASE_URI"] = URL.create(
    "mysql+pymysql",
    username=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD"),
    host=os.getenv("DB_HOST", "127.0.0.1"),
    database=os.getenv("DB_NAME"),
    query={"charset": "utf8mb4"},
)
db.init_app(app)
```

`URL.create` maneja contraseñas con caracteres que causarían problemas si se concatenaran manualmente en una URL. La implementación completa incluye puerto y valores predeterminados.

**Comprobación.** Desde `codigo`, inicia `python -m flask --app app:create_app run`. En Windows usa `.venv\Scripts\python.exe -m flask --app app:create_app run`. Abre `http://127.0.0.1:5000/api/recursos` después de integrar la ruta de la etapa 4; debe mostrar el catálogo elegido. El servidor se inicia localmente, sin `--host=0.0.0.0` y sin modo debug.

**Nota de integración.** Puedes usar desde ahora los archivos completos para ejecutar la referencia y luego estudiar cada ruta. Si construyes por partes, Flask arrancará antes de que todas las pantallas estén listas; verifica las rutas ya implementadas de forma individual. No uses `db.create_all()` como reemplazo del SQL requerido para la entrega.

**Evidencia.** Cada persona explica una clase, una relación y el propósito de la configuración. Consulta complementaria: [inicio de Flask-SQLAlchemy](https://flask-sqlalchemy.palletsprojects.com/en/stable/quickstart/).

## 10 Etapa 4 - Construir la API y validar entradas

**Meta.** Completar el contrato de intercambio entre navegador y servidor.

**Conceptos.** Un endpoint es una ruta con una operación HTTP. JSON transporta datos; no es código HTML. `GET` consulta, `POST` crea y `DELETE` elimina. La validación HTML mejora la interacción, pero Flask debe validar otra vez porque cualquier cliente puede enviar una solicitud sin usar el formulario.

| Método y ruta | Datos de entrada | Resultado esperado |
|---|---|---|
| GET /api/personas | Ninguno | 200 y lista de personas |
| POST /api/personas | nombre, email en JSON | 201; 400 si inválido; 409 si correo repetido |
| GET /api/recursos | Ninguno | 200 y catálogo con categoría |
| GET /api/disponibilidad | fecha y recurso_id en query string | 200 y nueve bloques; 400 o 404 |
| GET /api/reservas | fecha; recurso_id opcional | 200 y lista de esa fecha |
| POST /api/reservas | persona_id, recurso_id, fecha, hora, motivo | 201; 400; 404; 409 |
| DELETE /api/reservas/id | Identificador en la ruta | 204 sin cuerpo; 400 si comenzó; 404 si falta |
| GET /api/resumen | fecha en query string | 200 y conteos con porcentaje |

Un fallo de conexión o consulta de base de datos devuelve 503 con un mensaje general; los detalles técnicos quedan en la terminal. Una ruta inexistente devuelve 404. No expongas contraseñas ni trazas en mensajes de la interfaz.

**Acciones.** Implementen primero `GET /api/recursos` y `GET /api/personas`. Luego `POST /api/personas`. Usen las funciones auxiliares del archivo de referencia para comprobar tipo de JSON, longitudes y formato de correo. No conviertan ciegamente todos los valores a enteros: `true`, valores vacíos y números decimales deben rechazarse.

```python
@app.get("/api/recursos")
def recursos():
    filas = db.session.scalars(
        select(Recurso).order_by(Recurso.nombre)).all()
    return jsonify([
        {"id": r.id, "nombre": r.nombre,
         "categoria": r.categoria}
        for r in filas
    ])
```

Después construyan la reserva. Este fragmento se ejecuta dentro de la ruta, una vez validados los datos y la existencia de las relaciones:

```python
reserva = Reserva(persona_id=pid, recurso_id=rid,
                  inicio=inicio, motivo=motivo)
db.session.add(reserva)
try:
    db.session.commit()
except IntegrityError:
    db.session.rollback()
    return jsonify(error="La persona o el recurso ya tiene una reserva."), 409
return jsonify(reserva.to_dict()), 201
```

**Piensa antes de ejecutar.** Dos pestañas muestran 09:00 disponible. La primera guarda y la segunda intenta guardar un instante después. Una consulta previa de disponibilidad no basta. La restricción única decide qué escritura puede conservarse y la segunda recibe 409. La interfaz debe actualizar horarios después del intento.

Prueba una creación desde la consola del navegador abierta en la página local. Sustituye la fecha por mañana en Puerto Rico, dentro del límite permitido:

```javascript
const respuesta = await fetch('/api/reservas', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({
    persona_id: 1, recurso_id: 1,
    fecha: 'AAAA-MM-DD', hora: '09:00',
    motivo: 'Practicar consultas SQL'
  })
});
console.log(respuesta.status, await respuesta.json());
```

Sustituye `AAAA-MM-DD` por la fecha de mañana en formato año-mes-día. Si usas tutorías, adapta el motivo a la materia; la forma del JSON no cambia.

**Aplicación de destreza.** Antes de leer `fecha_valida`, escriban tres valores que debería rechazar. Compárenlos con la implementación y ejecuten al menos uno. Expliquen por qué una FK y una validación de formato cumplen funciones diferentes.

**Comprobación.** Una reserva válida devuelve 201. Repetir recurso y hora con otra persona devuelve 409. Elegir dos recursos distintos para la misma persona y hora también devuelve 409. Una hora 09:30 devuelve 400. Tras el conflicto, una reserva distinta debe seguir funcionando gracias al rollback.

**Evidencia.** Tabla de solicitudes con datos enviados, código de estado y resultado. Fuente de consulta: [restricciones en SQLAlchemy](https://docs.sqlalchemy.org/en/20/core/constraints.html).

## 11 Etapa 5 - Crear formularios y conectar AJAX

**Meta.** Usar los endpoints desde una interfaz accesible que conserve el contexto.

**Conceptos.** `fetch` realiza la solicitud de forma asíncrona. `await` espera el resultado dentro de una función `async`. `preventDefault` evita el envío tradicional del formulario. Actualizar el DOM cambia lo que se ve sin recargar el documento. `fetch` no convierte automáticamente un estado 400 o 409 en una excepción; por eso se revisa `response.ok`.

**Acciones.** Construyan `templates/index.html` y `static/styles.css`. Usen la misma interfaz en las tres opciones: Jinja sustituye título y etiquetas según `PROYECTO`. La categoría se muestra junto al recurso. Cada entrada necesita una etiqueta visible conectada a su identificador.

```html
<label for="motivo">Motivo breve</label>
<textarea id="motivo" required minlength="5" maxlength="200"
          aria-describedby="ayuda-motivo"></textarea>
<p id="ayuda-motivo">Entre 5 y 200 caracteres.</p>
<p id="mensaje" role="status" aria-live="polite"></p>
<p id="error" role="alert" tabindex="-1"></p>
```

La etiqueta permite identificar el control; la ayuda explica la entrada. La confirmación informa sin interrumpir y el error recibe foco para facilitar su localización. Comprueben el comportamiento con teclado y, cuando esté disponible, un lector de pantalla. Referencias: [etiquetas de W3C WAI](https://www.w3.org/WAI/tutorials/forms/labels/) y [notificaciones de formularios](https://www.w3.org/WAI/tutorials/forms/notifications/).

En `static/app.js`, construyan primero un pequeño cliente HTTP:

```javascript
async function api(url, opciones = {}) {
  const respuesta = await fetch(url, opciones);
  if (respuesta.status === 204) return null;
  const datos = await respuesta.json();
  if (!respuesta.ok) throw new Error(datos.error);
  return datos;
}
```

La versión completa añade un mensaje para fallos de conexión. Una respuesta 204 no contiene JSON; intentar convertirla produciría un error innecesario.

Conecten el evento `submit` del formulario. Lean los valores, envíen JSON, muestren el resultado y actualicen las listas. Mantengan los datos escritos si hay un error. Deshabiliten temporalmente el botón durante el envío y habilítenlo según la disponibilidad al finalizar.

```javascript
formulario.addEventListener('submit', async (evento) => {
  evento.preventDefault();
  // Leer campos y construir el objeto de entrada.
  // Enviar con POST; comprobar respuesta.
  // Mostrar confirmación o error y actualizar la lista.
});
```

Este fragmento muestra la estructura del evento; el manejador ejecutable completo está en `static/app.js`, bajo `form-reserva`. Implementen y expliquen sus pasos, en vez de dejar estos comentarios como solución final.

Para mostrar entradas del usuario usen nodos y `textContent`:

```javascript
const detalle = document.createElement('p');
detalle.textContent = reserva.motivo;
```

No concatenen el motivo dentro de `innerHTML`. La interfaz debe representar etiquetas escritas por una persona como texto, no ejecutarlas.

**Decisiones tecnológicas.** Esta referencia usa CSS propio y `fetch`, sin dependencias de CDN. Bootstrap y jQuery ya estudiados pueden emplearse si el equipo los prefiere y conserva el contrato y la accesibilidad. Si usa Bootstrap, incluya los archivos locales necesarios o documente la dependencia. Si usa jQuery AJAX, mantenga JSON, códigos de estado y actualización del DOM. No se exige combinar ambas bibliotecas con `fetch` para obtener puntos.

**Responsive y adaptive.** El CSS reduce o amplía anchos y tamaños de forma fluida. Un breakpoint a 52rem cambia las secciones de una a dos columnas. Expliquen esta decisión de distribución usando el vocabulario trabajado en el curso.

**Comprobación.** Registren una persona desde el formulario; debe quedar seleccionada en el paso 2. Cambien recurso y fecha; los horarios deben actualizarse. Al guardar, aparece la reserva sin recargar la página. Revisen 360px y 1280px de ancho, zoom de 200 %, navegación con Tab y foco visible. No debe perderse información ni depender solo del color.

**Evidencia.** Captura de pantalla estrecha, lista de comprobación de teclado y solicitud POST visible en Network. Consulta: [Flask con JavaScript, fetch y JSON](https://flask.palletsprojects.com/en/stable/patterns/javascript/).

## 12 Etapa 6 - Procesar y consultar los datos

**Meta.** Transformar registros (récords) en información comprobable.

**Conceptos.** `JOIN` relaciona registros (récords); `COUNT` cuenta; `GROUP BY` agrupa. En SQLAlchemy, las relaciones permiten mostrar el nombre de la persona y del recurso. El resumen agrupa por recurso y después incluye los recursos que tienen cero reservas.

**Acciones.** Implementen las rutas de disponibilidad, listado, cancelación y resumen. La fecha elegida filtra la lista completa y el resumen. El formulario filtra la disponibilidad de un recurso. Estas son consultas diferentes y sus etiquetas deben dejarlo claro.

El resumen se basa en esta operación, equivalente a la consulta ORM del código:

```sql
SELECT recurso_id, COUNT(*) AS total
FROM reservas
WHERE inicio >= '2030-04-02 00:00:00'
  AND inicio <  '2030-04-03 00:00:00'
GROUP BY recurso_id;
```

Las fechas de esta consulta son ejemplos; usa el día de tus pruebas. Para un día completo, capacidad = número de recursos × 9 bloques. Porcentaje = reservas registradas ÷ capacidad × 100. Con tres recursos y dos reservas: 2 ÷ 27 × 100 = 7.4 %, redondeado a un decimal. Con el cuarto recurso de la actividad: 2 ÷ 36 × 100 = 5.6 %.

```python
conteos = dict(db.session.execute(
    select(Reserva.recurso_id, func.count(Reserva.id))
    .where(Reserva.inicio >= desde, Reserva.inicio < hasta)
    .group_by(Reserva.recurso_id)
).all())
```

La implementación recorre el catálogo para mostrar también los ceros. No almacena porcentajes en una cuarta tabla: se calculan a partir de los datos existentes.

**Programación en equipo: filtro del listado.** La referencia ya acepta `recurso_id` en `GET /api/reservas`. Conecten esa capacidad a un nuevo selector en la sección 3 de la interfaz. Asignen una etiqueta visible con el nombre de su dominio, por ejemplo “Filtrar por sala”. La primera opción será “Todos”, con valor vacío. Rellenen el selector con el catálogo que recibe `iniciar()`. Al cambiarlo, ejecuten `listar()`.

Dentro de `listar()`, creen parámetros independientes para la lista. Mantengan `params` para el resumen de todos los recursos de la fecha. Usen este patrón después de agregar el selector con identificador `filtro-recurso`:

```javascript
const paramsLista = new URLSearchParams(params);
const filtro = document.getElementById('filtro-recurso');
if (filtro.value) paramsLista.set('recurso_id', filtro.value);
const [reservas, resumen] = await Promise.all([
  api(`/api/reservas?${paramsLista}`),
  api(`/api/resumen?${params}`)
]);
```

Prueben con dos reservas en recursos distintos. Al seleccionar uno, debe quedar una fila y el resumen diario debe seguir contando dos. Al volver a “Todos”, deben reaparecer las dos. Actualicen la explicación visible de la sección 3 y redacten un mensaje específico para un filtro sin resultados. En tutorías el selector muestra tutor y materia. En equipos muestra identificador y tipo. Guarden este cambio en un pull request con su comprobación.

**Cancelación.** La interfaz solicita confirmación y envía `DELETE /api/reservas/id`. Flask comprueba que exista y que no haya comenzado; luego elimina y confirma. La interfaz procesa 204 sin buscar JSON, actualiza lista y horarios y coloca el foco en el encabezado del listado. Cancelar dos veces el mismo identificador produce 404 en el segundo intento.

**Aplicación de destreza.** Registren dos reservas para mañana en recursos y personas válidos. Calculen a mano el conteo por recurso y el porcentaje. Cancelen una y repitan el cálculo. No cuenten cancelaciones como reservas conservadas.

**Comprobación.** Coinciden cálculo manual, respuesta JSON y pantalla. Un recurso sin reservas muestra cero. Tras cancelar, el bloque se puede volver a reservar. Si el día no tiene reservas, la interfaz presenta un mensaje explícito.

**Evidencia.** Una tabla con valores antes y después, y una explicación de por qué estos resultados constituyen procesamiento de datos.

## 13 Etapa 7 - Probar e integrar

**Meta.** Encontrar problemas antes de la demostración y comprobar una instalación reproducible.

**Acciones.** Ejecuten `python -m pytest -q` desde `codigo`. El archivo `tests/test_app.py` crea SQLite en memoria y fija el reloj para que las pruebas no dependan del día. No utiliza ni borra su base de trabajo. Estas pruebas rápidas no prueban el SQL de instalación en MySQL/MariaDB; deben completar también las pruebas de integración en el motor de entrega.

| Caso | Acción | Resultado que deben observar |
|---|---|---|
| P1 Instalación limpia | Ejecutar el SQL elegido en una base nueva | Exactamente tres tablas y catálogo correcto |
| P2 Alta y persistencia | Crear persona y reserva; recargar | Datos conservados |
| P3 Correo duplicado | Repetir correo con cambios de mayúsculas | 409 y ninguna persona adicional |
| P4 Recurso ocupado | Misma hora y recurso, otra persona | 409 y una sola reserva en ese bloque |
| P5 Persona ocupada | Misma persona y hora, otro recurso | 409 |
| P6 Hora y fecha | 09:30, hora pasada o fecha fuera del límite | 400 y sin insertar |
| P7 Datos inválidos | Motivo vacío, identificador inexistente o JSON inválido | 400 o 404 según el caso |
| P8 Cancelación | Cancelar futura y consultar otra vez | 204; bloque libre; conteo reducido |
| P9 Resumen | Dos reservas, luego cancelar una | Conteos y porcentaje exactos |
| P10 Accesibilidad | Tab, Enter, zoom 200 % y 360px | Controles utilizables y foco visible |
| P11 Dos solicitudes | Dos clientes envían la misma hora y recurso | Una 201 y otra 409; una sola fila |
| P12 Pérdida de conexión | Detener Flask e intentar enviar | Mensaje comprensible; datos del formulario conservados |
| P13 Texto como datos | Motivo con texto `<b>prueba</b>` | Se ve literalmente; no se interpreta como HTML |
| P14 Recuperación | Crear una reserva válida después de un 409 | 201; sesión utilizable tras rollback |

Para P11, abran dos pestañas y preparen el mismo bloque con personas distintas. Envíen casi simultáneamente. Verifiquen además en SQL que el conteo del recurso y hora sea uno. Un intento secuencial demuestra unicidad, pero no sustituye la comprobación con solicitudes concurrentes. Registren cuál hicieron.

**Prueba de instalación por otra persona.** Una persona que no configuró inicialmente debe seguir el README, usar una base nueva y demostrar una reserva completa. No borren una base existente solo para repetir el ensayo; utilicen una copia del SQL con un nuevo nombre y documenten el cambio temporal.

**Revisión cruzada.** Cada integrante explica una ruta escrita por otra persona y propone una prueba que podría hacerla fallar. Registren resultado esperado, observado, responsable y corrección en `plantillas/Plan_pruebas.md`. No escriban “todo funciona” sin evidencia.

**Comprobación.** El equipo completa la matriz, distingue resultados automáticos de manuales y resuelve los defectos que impiden el flujo principal. Un defecto pendiente se declara con su efecto y forma de reproducirlo.

**Evidencia.** Resultados de pytest, versión del motor, pruebas manuales, salida de SQL y bitácora de integración.

## 14 Etapa 8 - Documentar y preparar la entrega

**Meta.** Entregar un proyecto que otra persona pueda comprender, ejecutar y evaluar.

**Acciones.** Completen el README con propósito, integrantes, proyecto elegido, requisitos, configuración, SQL, ejecución, pruebas, endpoints y limitaciones. Usen rutas relativas dentro del repositorio. Mantengan credenciales fuera del ZIP. Si modificaron dependencias, registren las versiones probadas.

**IMPORTANTE:**

- La entrega principal y obligatoria es el enlace al repositorio GitHub del equipo, la etiqueta `v1.0-entrega` y el SHA del commit evaluado.
- El ZIP sirve como copia de respaldo y no sustituye el repositorio.

Mantengan esta organización:

```text
Equipo_Proyecto/
  codigo/                 Código completo y SQL de la variante
  documentacion/
    README.md             Puede enlazar al README de codigo
    diagrama_datos.png    O diagrama legible dentro del PPTX
    bitacora.md
    pruebas.md
  presentacion/
    resumen.pptx
    video.mp4             O enlace con acceso verificado
    transcripcion.txt
    subtitulos.vtt        O subtítulos revisados integrados
```

Pueden conservar los tres SQL como referencia, pero señalen claramente cuál se ejecuta. El ZIP no incluye `.venv`, `.env`, cachés ni datos personales. El SQL de entrega debe crear la base, las tres tablas, restricciones y datos ficticios de prueba. No se acepta únicamente un volcado binario ni únicamente `db.create_all()`.

**Personalización requerida.** Incorporen el cuarto recurso de la etapa 2 y el filtro de la etapa 6, adapten el título y los ejemplos a su contexto, documenten una decisión de UX y añadan al menos una prueba propia a la matriz. No se pide ampliar la cantidad de tablas ni construir funcionalidades extras. Las extensiones no sustituyen los requisitos mínimos.

**Comprobación final.** Una persona externa al paso de configuración puede seguir el README. Los enlaces del video funcionan con los permisos de acceso del docente. El PowerPoint explica la solución sin reproducir el video. Todos verifican el contenido del ZIP antes de enviarlo.

### Repositorio GitHub obligatorio y copia de la base

Cada equipo mantiene un único repositorio de proyecto en GitHub. Una persona lo crea y añade a sus compañeros como colaboradores; el docente debe poder leerlo durante la evaluación. Puede ser privado con acceso al docente o público si el equipo así lo decide. No publiquen datos personales, credenciales ni grabaciones de integrantes sin el acuerdo correspondiente. El video puede alojarse en el servicio autorizado por el curso y enlazarse desde el repositorio.

El docente comparte la base como repositorio o como paquete descargable. `INICIO.md` explica cómo crear el repositorio GitHub del equipo en ambos casos. Contiene el tutorial, el código de referencia, los SQL y las plantillas. Si está configurado como plantilla, seleccionen **Use this template**, luego **Create a new repository**, asignen un nombre como `equipo-03-reservas-salas` y creen una copia bajo la cuenta o la organización acordada. Si usan un fork en su lugar, identifiquen que es una derivación y mantengan la atribución. No entreguen el enlace al repositorio del profesor como si fuera el trabajo del equipo.

Clonen su propio repositorio. Sustituyan los marcadores de estos comandos por su URL y nombre reales:

```bash
git clone https://github.com/USUARIO/REPOSITORIO.git
cd REPOSITORIO
git switch -c tarea/formulario-personas
```

Después de un cambio comprobado, seleccionen solo los archivos correspondientes:

```bash
git status
git add codigo/templates/index.html codigo/static/styles.css
git commit -m "Agrega etiquetas y ayudas al formulario"
git push -u origin tarea/formulario-personas
```

Abran un pull request desde esa rama hacia `main`, expliquen cambio y prueba, y soliciten la revisión de otro integrante. Tras atender observaciones, integren el cambio. Antes de la próxima tarea actualicen su copia:

```bash
git switch main
git pull --ff-only
git switch -c tarea/validar-horarios
```

Cada integrante debe tener al menos un pull request de una contribución técnica y una revisión de otra persona. El trabajo conjunto se registra en la bitácora; no se exige dividir artificialmente un aporte ni igualar el número de commits. GitHub Desktop puede sustituir los comandos si produce el mismo historial verificable. Usen su cuenta personal para conservar la autoría.

Antes de entregar, comprueben que `main` contiene todos los cambios y que las pruebas pasan. Marquen la versión que mostrarán en el video:

```bash
git switch main
git pull --ff-only
git tag -a v1.0-entrega -m "Versión evaluada del proyecto"
git push origin v1.0-entrega
git rev-parse HEAD
```

Completen `ENTREGA.md` con los integrantes, enlaces a pull requests, revisiones y nombre de la etiqueta antes del último commit. Después de etiquetar, entreguen la URL de GitHub, la etiqueta y el SHA que imprimió `git rev-parse HEAD` en el espacio de entrega del curso. Así el SHA identifica exactamente el contenido evaluado. El PowerPoint y el video deben corresponder a ese commit. Si necesitan corregir después de entregar, acuerden una nueva etiqueta; no muevan silenciosamente la anterior. Un repositorio vacío, un ZIP subido como único archivo o un enlace sin acceso no permiten verificar el desarrollo. Mantengan el código fuente visible en sus carpetas.

Fuente para el procedimiento: [repositorios desde una plantilla](https://docs.github.com/en/repositories/creating-and-managing-repositories/creating-a-repository-from-a-template) y [GitHub flow](https://docs.github.com/en/get-started/using-github/github-flow). El esquema de entrega y las evidencias individuales son requisitos de esta actividad.

## 15 Video y PowerPoint para la primera nota

El video dura aproximadamente 10 a 12 minutos por equipo, con ajustes acordados cuando sean necesarios. La demostración “en vivo” significa que se observa la aplicación ejecutándose y respondiendo durante la grabación, con interacción real. No requiere una transmisión en directo. Se pueden grabar segmentos y editar transiciones; las operaciones centrales deben verse de forma continua y con resultados legibles.

Guion sugerido:

| Tramo orientativo | Contenido y evidencia |
|---|---|
| 0:00 a 1:00 | Problema, usuarios, proyecto e integrantes |
| 1:00 a 3:00 | Arquitectura, tecnologías y recorrido de una reserva |
| 3:00 a 4:30 | Tres tablas, relaciones y restricciones contra duplicados |
| 4:30 a 8:30 | Demo funcional: alta, disponibilidad, reserva, conflicto, cancelación y resumen |
| 8:30 a 10:30 | Network o código relevante, pruebas y decisiones de accesibilidad |
| 10:30 a 12:00 | Aportes individuales, limitaciones y aprendizaje |

**IMPORTANTE: En la demo usen una fecha futura, un motivo ficticio y dos personas.** Muestren al menos una solicitud HTTP con estado y respuesta. Si necesitan enviar un conflicto que la interfaz ya bloquea, expliquen cómo lo provocan desde una segunda pestaña o la consola. No sustituyan el flujo completo por capturas estáticas.

El PowerPoint tendrá unas diez diapositivas. La plantilla adjunta ofrece el orden y preguntas de apoyo; el equipo sustituye las indicaciones por evidencia de su proyecto. Cada captura lleva una explicación. El lector no debe depender de lo que se dijo en el video.

1. **Identificación**: nombre, contexto, integrantes y enlace al código y al video.
2. **Problema y alcance**: quién usa el panel, qué resuelve y qué queda fuera.
3. **Flujo funcional**: pasos y resultados observables del usuario.
4. **Arquitectura y tecnologías**: función concreta de cada componente.
5. **Modelo de datos**: tres tablas, PK, FK y unicidad.
6. **API**: ejemplos de solicitud, respuesta y estados relevantes.
7. **Evidencia funcional**: capturas del alta, reserva y resultado, con explicación.
8. **Procesamiento y calidad**: cálculo verificable, conflictos y resultados de pruebas.
9. **UX y accesibilidad**: decisiones, evidencia de teclado y adaptación de pantalla.
10. **Reproducción y reflexión**: pasos de arranque, aportes, limitaciones y fuentes.

Usen tipografía legible, contraste suficiente y texto conciso. Añadan texto alternativo a imágenes relevantes. Revisen los subtítulos del video, en especial nombres de tecnologías. La narración puede realizarse con voz propia, síntesis de voz o apoyos de comunicación; cada integrante identifica su aporte y demuestra comprensión técnica.

## 16 Dos notas independientes

**Cada componente del proyecto se evalúa sobre 100 puntos y se registra como una nota separada del curso.**

Para cada criterio se asigna un nivel y se multiplica por su máximo: **Completo 1.00**, evidencia correcta y todos sus indicadores; **Mayormente logrado 0.75**, evidencia verificable con omisiones menores; **En desarrollo 0.50**, evidencia parcial con errores que afectan la explicación o el funcionamiento; **Sin evidencia 0**, falta o no puede verificarse. Se suman los resultados y se redondea la nota final a un decimal. El docente explica qué indicador falta cuando no asigna el nivel completo.

### Nota 1 - Presentación con video y PowerPoint

| Criterio | Máximo | Indicadores del nivel completo |
|---|---|---|
| Explicación técnica | 20 | Relaciona tecnologías con funciones; sigue un dato desde formulario hasta SQL; explica API y restricciones con ejemplos correctos |
| Demostración grabada | 20 | Aplicación ejecutándose; muestra alta, consulta, reserva, conflicto, cancelación y resumen con resultados visibles |
| PowerPoint autónomo | 20 | Resume problema, arquitectura, datos, API, evidencia, instalación y limitaciones; se comprende sin el video |
| Comunicación accesible | 15 | Video legible y organizado; subtítulos revisados y transcripción; diapositivas con contraste, tamaño adecuado y alternativas textuales |
| Calidad de la evidencia y reflexión | 10 | Presenta pruebas reales, una decisión justificada y una limitación; atribuye fuentes y código reutilizado |
| Comprensión individual | 15 | Cada integrante explica una contribución propia, una conexión con otra capa y una prueba pertinente mediante el formato de comunicación elegido |
| Total | 100 | 85 puntos de evidencia grupal y 15 individuales |

**IMPORTANTE:**

- Los primeros cinco criterios se comparten dentro del equipo. El último se asigna a cada integrante por su evidencia.
- El video y el PowerPoint son obligatorios: sin PowerPoint, su criterio recibe cero; sin video, la demostración recibe cero.
- Otros criterios se puntúan solo con la evidencia que efectivamente exista, sin descuentos arbitrarios adicionales.

### Nota 2 - Desarrollo y funcionamiento

| Criterio | Máximo | Indicadores del nivel completo |
|---|---|---|
| Flujo funcional integrado | 25 | Alta, disponibilidad, reserva, consulta y cancelación funcionan y conservan datos tras recargar |
| Modelo y scripts SQL | 20 | Exactamente tres tablas; PK, FK y restricciones correctas; script instala variante y semillas; no permite doble reserva |
| API y validación | 15 | Contrato consistente; valida en servidor; maneja 201, 204, 400, 404 y 409; recupera la sesión tras conflicto |
| Interfaz y accesibilidad | 15 | Formularios etiquetados; mensajes claros; AJAX actualiza; teclado y foco utilizables; diseño usable en pantalla estrecha |
| Procesamiento y reproducibilidad | 15 | Resumen correcto; pruebas registradas; repositorio GitHub accesible con etiqueta y SHA; README permite instalar; pruebas y resumen correctos; configuración sin secretos |
| Trabajo individual verificable | 10 | Implementa código con autoría identificable, abre al menos un pull request, revisa uno de otra persona y registra decisiones y rebalanceo |
| Total | 100 | 90 puntos de evidencia grupal y 10 individuales |

**IMPORTANTE:**

- La nota de desarrollo se basa en el código y su ejecución, aunque la presentación tenga dificultades.
- La presentación se evalúa con su propia rúbrica. No se exige que un estudiante grabe más minutos ni escriba más líneas para acreditar un aporte comparable.
- Una contribución en pareja puede documentarse como trabajo compartido, indicando qué razonó y verificó cada persona.

## 17 Diagnóstico de problemas frecuentes

| Error/Comportamiento | Comprobación y próxima acción |
|---|---|
| ModuleNotFoundError | Usa el Python del entorno e instala requirements.txt desde codigo |
| Access denied | Prueba iniciar sesión con el usuario de la aplicación. Revisa usuario, clave y host en .env. Si faltan permisos sobre la base elegida, revisa GRANT con la cuenta administradora. |
| Unknown database | Ejecuta la variante SQL y verifica DB_NAME |
| Table already exists o database exists | El script ya se ejecutó; no lo repitas sobre la misma base; usa la existente o una base nueva para el ensayo |
| JSON con datos de otro proyecto | Revisa PROYECTO y DB_NAME juntos; reinicia Flask |
| 400 al crear | Lee el campo que indica el mensaje; verifica hora exacta, motivo y fecha futura |
| 409 en una hora que parecía libre | Otro envío ocupó la persona o el recurso; actualiza horarios y cambia el bloque |
| Página sin datos y 503 | Verifica que MySQL/MariaDB esté iniciado y revisa el mensaje técnico en la terminal |
| Cancelación correcta pero error de JSON | No intentes convertir a JSON una respuesta 204 |
| Cambios de JavaScript no aparecen | Guarda el archivo y recarga evitando caché; revisa Console y Network |
| Fecha cambió desde que abrí la página | Recarga para actualizar los límites del formulario; el servidor valida con la fecha vigente |

Al pedir ayuda compartan: paso, resultado esperado, resultado observado, código de estado y fragmento mínimo. Excluyan contraseñas y `.env`.

## 18 Glosario y fuentes de consulta

| Concepto | Definición |
|---|---|
| API REST | Interfaz que organiza operaciones sobre recursos usando HTTP |
| Endpoint | Combinación de ruta y método |
| JSON | Formato de intercambio de datos |
| DOM | Representación del documento que JavaScript puede modificar |
| ORM | Herramienta para trabajar con registros (récords) mediante objetos |
| Transacción | Unidad de trabajo que se confirma o revierte |
| Restricción | Regla que la base aplica a los datos |
| AJAX | Intercambio asíncrono que permite actualizar la interfaz sin recargar toda la página |

Esta secuencia, sus actividades y rúbricas son una propuesta docente para el contexto descrito. Las fuentes siguientes respaldan los mecanismos técnicos y los principios generales de accesibilidad; no prescriben estas duraciones ni esta ponderación.

- CAST. [UDL Guidelines](https://udlguidelines.cast.org/). Opciones para participación, representación y expresión.
- W3C WAI. [Etiquetas de formularios](https://www.w3.org/WAI/tutorials/forms/labels/), [validación](https://www.w3.org/WAI/tutorials/forms/validation/) y [notificaciones](https://www.w3.org/WAI/tutorials/forms/notifications/).
- Pallets. [JavaScript, fetch y JSON en Flask](https://flask.palletsprojects.com/en/stable/patterns/javascript/) y [Flask-SQLAlchemy](https://flask-sqlalchemy.palletsprojects.com/en/stable/quickstart/).
- SQLAlchemy. [Definición de restricciones](https://docs.sqlalchemy.org/en/20/core/constraints.html).
- MySQL. [Restricciones PRIMARY KEY y UNIQUE](https://dev.mysql.com/doc/refman/8.4/en/constraint-primary-key.html).

Fuentes consultadas el 10 de noviembre de 2026. Revisa `VERIFICACION.md` para conocer qué se ejecutó al preparar el material y qué debe comprobarse en el laboratorio.
