# Caso Arandu — reglas del dominio v1

Version 1 · 16 de septiembre de 2026. Especificacion del caso troncal, independiente del lenguaje y
del framework. Insumo de: demo de S1, ejercicio de S2, modulo con defectos sembrados de S5, parcial,
Tarea 2 y final del Taller IV; y del proyecto completo del Taller I.

**Nombres declarados:** el caso se llama **Arandu** y el instituto ficticio, **Instituto Arandu**.
Decidido el 18-09-2026.

## 1. El escenario

Un estudiante se inscribe a las materias de un periodo academico. El sistema acepta o rechaza cada
solicitud segun ocho reglas. Nada mas. No hay pagos, aranceles, equivalencias, lista de espera ni
autenticacion en la v1.

## 2. Entidades

| Entidad | Campos minimos |
|---|---|
| **Estudiante** | id · plan de estudios · historial academico (materia, periodo, nota final) |
| **Materia** | codigo · plan · correlativas requeridas (lista de codigos) |
| **Comision** | id · materia · cupo (entero >= 0) · franjas horarias (dia de semana, hora inicio, hora fin) |
| **Periodo** | id · apertura de inscripcion · cierre de inscripcion · plazo de baja |
| **Inscripcion** | estudiante · comision · periodo · estado (activa / dada de baja) · instante de solicitud |

Todas las marcas de tiempo se interpretan en **America/Asuncion**. Los fixtures fijan un "ahora"
explicito: el sistema nunca lee el reloj real, lo recibe. Esa decision es la que hace deterministas
las pruebas, y conviene decirlo en S1: es el primer criterio de verificabilidad del taller.

## 3. Las reglas

**R1 · Ventana de inscripcion.** Una solicitud se acepta solo si su instante cae dentro del intervalo
`[apertura, cierre]` del periodo, **ambos extremos incluidos**. Fuera de la ventana se rechaza sin
excepcion: no hay rol, permiso ni caso especial que la abra.

**R2 · Correlatividad.** Una materia con correlativas requeridas admite inscripcion solo si el
estudiante tiene **todas** ellas aprobadas al momento de la solicitud. *Aprobada* = nota final
registrada en un periodo anterior e igual o mayor al minimo del plan. **Cursada y no aprobada no
habilita.** Lista de correlativas vacia = sin restriccion.

**R3 · Cupo.** Cada comision tiene un cupo entero >= 0. Cada inscripcion **activa** ocupa un lugar;
una inscripcion dada de baja **no** ocupa lugar y libera el cupo de inmediato. Cuando las
inscripciones activas igualan el cupo, se rechaza. Cupo 0 rechaza siempre. Sin lista de espera.

**R4 · Maximo de materias.** Un estudiante no puede superar **6 inscripciones activas** en el mismo
periodo. Las bajas no cuentan.

**R5 · Choque de horarios.** Dos comisiones chocan si comparten al menos un dia de la semana y sus
intervalos horarios se solapan en ese dia. Dos intervalos se solapan si `inicio_A < fin_B` **y**
`inicio_B < fin_A`. El contacto exacto extremo con extremo —una clase termina 20:00 y otra empieza
20:00— **no es choque**. Se rechaza la solicitud que choque con cualquier inscripcion activa del
mismo estudiante en el mismo periodo.

**R6 · Baja.** Un estudiante puede darse de baja de una inscripcion activa hasta el **plazo de baja**
del periodo, inclusive. Despues se rechaza la baja. Una baja efectuada libera cupo (R3) y deja de
contar para R4 y R5.

**R7 · Unicidad.** Un estudiante no puede tener dos inscripciones activas a la **misma materia** en
el mismo periodo, aunque sean comisiones distintas.

**R8 · Orden de evaluacion.** Las reglas se evaluan en este orden y se rechaza con **el primer motivo
que aplique**, no con la lista de todos los motivos:

`R1 -> R2 -> R7 -> R4 -> R5 -> R3`

Este orden es parte del contrato, no un detalle de implementacion: hace que el motivo de rechazo sea
determinista y por lo tanto verificable. Una implementacion que rechaza por cupo cuando ademas habia
choque de horarios esta mal, aunque rechace.

## 4. Casos limitrofes, resueltos de antemano

- Solicitud **exactamente** en el instante de apertura o de cierre -> se acepta (R1, inclusive).
- Baja **exactamente** en el plazo -> se acepta (R6, inclusive).
- Clases contiguas sin espacio entre ellas -> no es choque (R5).
- Cupo lleno pero con una baja previa -> hay lugar (R3).
- Correlativa cursada y reprobada -> se rechaza (R2).
- Materia sin correlativas -> R2 no aplica, sigue la evaluacion.
- Reinscripcion a una materia de la que se dio de baja en el mismo periodo -> permitida si R1 a R5 lo
  permiten; R7 solo mira inscripciones **activas**.

## 5. Fuera de alcance en la v1

Lista de espera · aranceles y pagos · equivalencias entre planes · autenticacion y roles ·
notificaciones · historico de auditoria · concurrencia real entre solicitudes simultaneas.

La concurrencia es tentadora y hay que resistirla: convierte el caso en un problema de sistemas
distribuidos y el taller no es sobre eso.
