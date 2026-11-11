"use strict";
const $ = (id) => document.getElementById(id);
let consultaHorario = 0;
let consultaLista = 0;

function informar(texto, error = false) {
  $("mensaje").textContent = error ? "" : texto;
  $("error").textContent = error ? texto : "";
  if (error) $("error").focus();
}

async function api(url, opciones = {}) {
  let respuesta;
  try { respuesta = await fetch(url, opciones); }
  catch { throw new Error("No hay conexión con Flask. Verifica el servidor e intenta de nuevo."); }
  if (respuesta.status === 204) return null;
  const datos = await respuesta.json();
  if (!respuesta.ok) throw new Error(datos.error || "No se pudo completar la solicitud.");
  return datos;
}

function enviar(url, datos) {
  return api(url, {method: "POST", headers: {"Content-Type": "application/json"}, body: JSON.stringify(datos)});
}

async function cargarPersonas(seleccion = $("persona").value) {
  const personas = await api("/api/personas");
  $("persona").replaceChildren(new Option("Selecciona una persona", ""));
  for (const p of personas) $("persona").add(new Option(`${p.nombre} (${p.email})`, p.id));
  $("persona").value = seleccion;
}

async function horarios() {
  const turno = ++consultaHorario;
  $("hora").disabled = true;
  $("crear-reserva").disabled = true;
  $("hora").replaceChildren(new Option("Selecciona recurso y fecha", ""));
  if (!$("recurso").value || !$("fecha").value) return;
  $("ayuda-hora").textContent = "Consultando horarios…";
  try {
    const params = new URLSearchParams({recurso_id: $("recurso").value, fecha: $("fecha").value});
    const bloques = await api(`/api/disponibilidad?${params}`);
    if (turno !== consultaHorario) return; // Descarta respuestas de una selección anterior.
    $("hora").replaceChildren(new Option("Selecciona una hora disponible", ""));
    for (const b of bloques) {
      const opcion = new Option(`${b.hora} — ${b.estado}`, b.hora);
      opcion.disabled = !b.disponible;
      $("hora").add(opcion);
    }
    const hay = bloques.some((b) => b.disponible);
    $("hora").disabled = !hay;
    $("crear-reserva").disabled = !hay;
    $("ayuda-hora").textContent = hay ? "Cada bloque dura una hora. La reserva se confirma al guardarla." : "No quedan bloques disponibles. Prueba otra fecha o recurso.";
  } catch (error) {
    if (turno === consultaHorario) {
      $("ayuda-hora").textContent = "No se pudieron cargar los horarios.";
      throw error;
    }
  }
}

async function listar() {
  const turno = ++consultaLista;
  const params = new URLSearchParams({fecha: $("fecha").value});
  const [reservas, resumen] = await Promise.all([api(`/api/reservas?${params}`), api(`/api/resumen?${params}`)]);
  if (turno !== consultaLista) return;
  $("resumen").textContent = `${resumen.fecha}: ${resumen.total} reservas de ${resumen.capacidad} bloques diarios (${resumen.porcentaje} %).`;
  $("por-recurso").replaceChildren();
  for (const fila of resumen.por_recurso) {
    const li = document.createElement("li");
    li.textContent = `${fila.recurso}: ${fila.reservas} reservas`;
    $("por-recurso").append(li);
  }
  $("reservas").replaceChildren();
  if (!reservas.length) {
    const li = document.createElement("li");
    li.textContent = "No hay reservas para esta fecha.";
    $("reservas").append(li);
  }
  for (const r of reservas) {
    const li = document.createElement("li");
    const titulo = document.createElement("p");
    titulo.textContent = `#${r.id} · ${r.inicio.replace("T", " ")} · ${r.recurso} · ${r.persona}`;
    const detalle = document.createElement("p");
    detalle.textContent = r.motivo; // Trata los datos como texto, nunca como HTML.
    const boton = document.createElement("button");
    boton.type = "button";
    boton.textContent = `Cancelar reserva ${r.id}`;
    boton.addEventListener("click", async () => {
      if (!window.confirm(`¿Cancelar la reserva ${r.id}? Se eliminará y se liberará su hora.`)) return;
      boton.disabled = true;
      try {
        await api(`/api/reservas/${r.id}`, {method: "DELETE"});
        informar(`Reserva ${r.id} cancelada.`);
        await Promise.all([listar(), horarios()]);
        $("titulo-lista").focus();
      } catch (error) { informar(error.message, true); boton.disabled = false; }
    });
    li.append(titulo, detalle, boton);
    $("reservas").append(li);
  }
}

$("form-persona").addEventListener("submit", async (evento) => {
  evento.preventDefault();
  const boton = evento.submitter;
  boton.disabled = true;
  try {
    const p = await enviar("/api/personas", {nombre: $("nombre").value, email: $("email").value});
    await cargarPersonas(String(p.id));
    $("form-persona").reset();
    informar("Persona registrada y seleccionada en el paso 2.");
    $("persona").focus();
  } catch (error) { informar(error.message, true); }
  finally { boton.disabled = false; }
});

$("form-reserva").addEventListener("submit", async (evento) => {
  evento.preventDefault();
  $("crear-reserva").disabled = true;
  try {
    const r = await enviar("/api/reservas", {persona_id: $("persona").value, recurso_id: $("recurso").value,
      fecha: $("fecha").value, hora: $("hora").value, motivo: $("motivo").value});
    informar(`Reserva ${r.id} creada. Revisa la lista del paso 3.`);
    $("motivo").value = "";
    await listar();
  } catch (error) { informar(error.message, true); }
  finally { try { await horarios(); } catch (error) { informar(error.message, true); } }
});

$("recurso").addEventListener("change", () => horarios().catch((e) => informar(e.message, true)));
$("fecha").addEventListener("change", () => {
  $("reservas").replaceChildren(); $("resumen").textContent = "Cargando fecha seleccionada…";
  $("por-recurso").replaceChildren();
  Promise.all([horarios(), listar()]).catch((e) => informar(e.message, true));
});
$("ver-horarios").addEventListener("click", () => horarios().catch((e) => informar(e.message, true)));
$("actualizar").addEventListener("click", () => listar().catch((e) => informar(e.message, true)));

async function iniciar() {
  const recursos = await api("/api/recursos");
  for (const r of recursos) $("recurso").add(new Option(`${r.nombre} — ${r.categoria}`, r.id));
  await Promise.all([cargarPersonas(), listar()]);
}
iniciar().catch((error) => informar(error.message, true));
