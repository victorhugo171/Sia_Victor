/**
 * Centralización de Reglas de Negocio en el Frontend (SIA).
 * Única Fuente de Verdad: Consume dinámicamente `/api/configuracion/reglas/`
 * alimentado directamente desde `settings.py` del Backend.
 */
import { reactive } from 'vue'

export const reglas = reactive({
  limite_caja_chica: null,
  umbral_cotizaciones: null,
  min_cotizaciones: null,
  categorias_prioridad_alta: [],
  sla_horas: {},
  transiciones_estado: {},
  dias_reapertura: null,
  max_tickets_tecnico: null,
  umbral_aprobacion_jefe: null,
  fondo_mensual: null,
  min_password_length: null,
  cargado: false,
})

let cargaEnCurso = null

export async function cargarReglas(forzar = false) {
  if (cargaEnCurso && !forzar) {
    return cargaEnCurso
  }

  cargaEnCurso = (async () => {
    try {
      const res = await fetch('/api/configuracion/reglas/')
      if (!res.ok) throw new Error(`HTTP ${res.status}`)
      const datos = await res.json()
      if (!datos || typeof datos !== 'object' || !datos.sla_horas || !datos.transiciones_estado) {
        throw new Error('La respuesta de configuración está incompleta.')
      }
      Object.assign(reglas, datos)
      reglas.cargado = true
    } catch (e) {
      console.error('No se pudo cargar la configuración de reglas desde el backend.', e)
    }
    return reglas
  })()

  return cargaEnCurso
}

export function formatearBs(valor) {
  const n = Number(valor || 0)
  return `Bs. ${n.toFixed(2)}`
}

export function useReglas() {
  return {
    reglas,
    cargarReglas,
    formatearBs,
  }
}

export default reglas
