/**
 * Centralización de Reglas de Negocio en el Frontend (SIA).
 * Única Fuente de Verdad: Consume dinámicamente `/api/configuracion/reglas/`
 * alimentado directamente desde `settings.py` del Backend.
 */
import { reactive } from 'vue'

export const reglas = reactive({
  limite_caja_chica: 1000.0,
  umbral_cotizaciones: 500.0,
  min_cotizaciones: 3,
  categorias_prioridad_alta: ['RED', 'SERVIDORES'],
  sla_horas: { ALTA: 4, MEDIA: 24, BAJA: 72 },
  transiciones_estado: {
    ABIERTO: ['EN_PROCESO'],
    EN_PROCESO: ['RESUELTO'],
    RESUELTO: ['CERRADO', 'EN_PROCESO'],
    CERRADO: ['EN_PROCESO'],
  },
  dias_reapertura: 7,
  max_tickets_tecnico: 5,
  umbral_aprobacion_jefe: 300.0,
  fondo_mensual: 5000.0,
  min_password_length: 10,
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
      if (res.ok) {
        const datos = await res.json()
        Object.assign(reglas, datos)
        reglas.cargado = true
      }
    } catch (e) {
      console.warn('No se pudo sincronizar reglas desde el backend. Usando valores por defecto.', e)
    }
    return reglas
  })()

  return cargaEnCurso
}

// Iniciar carga inmediata
cargarReglas()

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
