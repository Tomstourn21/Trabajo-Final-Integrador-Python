"""
Sistema de Gestión de Hotel
----------------------------
Administra reservas y ocupación de habitaciones: registro de huéspedes,
check-in, check-out, control de disponibilidad, cálculo de estadías,
tipos de habitación y servicios adicionales, y estadísticas de ocupación.
"""

import time
from enum import Enum
from datetime import date, timedelta
from dataclasses import dataclass, field


# ============================================================
# ENUMS - Tipos y estados
# ============================================================

class TipoHabitacion(Enum):
    INDIVIDUAL = "Individual"
    DOBLE = "Doble"
    SUITE = "Suite"
    FAMILIAR = "Familiar"


class EstadoHabitacion(Enum):
    DISPONIBLE = "Disponible"
    OCUPADA = "Ocupada"
    MANTENIMIENTO = "En mantenimiento"


class EstadoReserva(Enum):
    ACTIVA = "Activa"
    FINALIZADA = "Finalizada"
    CANCELADA = "Cancelada"


# Precio base por noche según el tipo de habitación
PRECIOS_BASE = {
    TipoHabitacion.INDIVIDUAL: 15000,
    TipoHabitacion.DOBLE: 22000,
    TipoHabitacion.SUITE: 40000,
    TipoHabitacion.FAMILIAR: 32000,
}

CAPACIDAD_MAXIMA = {
    TipoHabitacion.INDIVIDUAL: 1,
    TipoHabitacion.DOBLE: 2,
    TipoHabitacion.SUITE: 2,
    TipoHabitacion.FAMILIAR: 4,
}


# ============================================================
# SERVICIOS ADICIONALES
# ============================================================

class Servicio:
    """Representa un servicio adicional que ofrece el hotel (spa, desayuno, etc.)"""

    def __init__(self, nombre, precio):
        self.nombre = nombre
        self.precio = precio

    def __repr__(self):
        return f"{self.nombre} (${self.precio})"


# Catálogo de servicios disponibles en el hotel
CATALOGO_SERVICIOS = {
    "desayuno": Servicio("Desayuno buffet", 3500),
    "spa": Servicio("Acceso a Spa", 8000),
    "cochera": Servicio("Cochera", 2500),
    "lavanderia": Servicio("Lavandería", 4000),
    "room_service": Servicio("Room Service", 5000),
}


# ============================================================
# HABITACIÓN
# ============================================================

class Habitacion:
    def __init__(self, numero, tipo: TipoHabitacion):
        self.numero = numero
        self.tipo = tipo
        self.precio_por_noche = PRECIOS_BASE[tipo]
        self.capacidad = CAPACIDAD_MAXIMA[tipo]
        self.estado = EstadoHabitacion.DISPONIBLE

    def esta_disponible(self):
        return self.estado == EstadoHabitacion.DISPONIBLE

    def ocupar(self):
        self.estado = EstadoHabitacion.OCUPADA

    def liberar(self):
        self.estado = EstadoHabitacion.DISPONIBLE

    def __repr__(self):
        return f"Hab. {self.numero} [{self.tipo.value}] - {self.estado.value}"


# ============================================================
# HUÉSPED
# ============================================================

class Huesped:
    def __init__(self, dni, nombre, apellido, email=None, telefono=None):
        self.dni = dni
        self.nombre = nombre
        self.apellido = apellido
        self.email = email
        self.telefono = telefono

    def __repr__(self):
        # Formato solicitado: Nombre Apellido
        return f"{self.nombre} {self.apellido}"


# ============================================================
# RESERVA / ESTADÍA
# ============================================================

class Reserva:
    contador_id = 1

    def __init__(self, huesped: Huesped, habitacion: Habitacion, fecha_checkin: date):
        self.id = Reserva.contador_id
        Reserva.contador_id += 1
        self.huesped = huesped
        self.habitacion = habitacion
        self.fecha_checkin = fecha_checkin
        self.fecha_checkout = None
        self.servicios: list[Servicio] = []
        self.estado = EstadoReserva.ACTIVA

    def agregar_servicio(self, clave_servicio):
        servicio = CATALOGO_SERVICIOS.get(clave_servicio)
        if servicio is None:
            raise ValueError(f"Servicio '{clave_servicio}' no existe en el catálogo")
        
        # Problema 1: no se debe poder añadir más de un mismo servicio.
        if any(s.nombre == servicio.nombre for s in self.servicios):
            raise ValueError(f"El servicio '{servicio.nombre}' ya ha sido agregado a esta reserva.")
            
        self.servicios.append(servicio)
        return servicio

    def cerrar(self, fecha_checkout: date):
        self.fecha_checkout = fecha_checkout
        self.estado = EstadoReserva.FINALIZADA

    def cantidad_noches(self):
        fin = self.fecha_checkout if self.fecha_checkout else date.today()
        noches = (fin - self.fecha_checkin).days
        return max(noches, 1)  # mínimo se cobra 1 noche

    def costo_total(self):
        costo_habitacion = self.cantidad_noches() * self.habitacion.precio_por_noche
        costo_servicios = sum(s.precio for s in self.servicios)
        return costo_habitacion + costo_servicios

    def __repr__(self):
        return (f"Reserva #{self.id} - {self.huesped.apellido} - "
                f"Hab {self.habitacion.numero} - {self.estado.value}")


# ============================================================
# HOTEL (clase principal que orquesta todo)
# ============================================================

class Hotel:
    def __init__(self, nombre):
        self.nombre = nombre
        self.habitaciones: list[Habitacion] = []
        self.huespedes: dict[str, Huesped] = {}      # dni -> Huesped
        self.reservas: list[Reserva] = []            # historial completo
        self.reservas_activas: dict[str, Reserva] = {}  # numero_habitacion -> Reserva

    # ---------- Gestión de habitaciones ----------
    def agregar_habitacion(self, numero, tipo: TipoHabitacion):
        habitacion = Habitacion(numero, tipo)
        self.habitaciones.append(habitacion)
        return habitacion

    def habitaciones_disponibles(self, tipo: TipoHabitacion = None):
        return [h for h in self.habitaciones
                if h.esta_disponible() and (tipo is None or h.tipo == tipo)]

    def buscar_habitacion(self, numero):
        for h in self.habitaciones:
            if h.numero == numero:
                return h
        return None

    # ---------- Gestión de huéspedes ----------
    def registrar_huesped(self, dni, nombre, apellido, email=None, telefono=None):
        if dni in self.huespedes:
            return self.huespedes[dni]
        huesped = Huesped(dni, nombre, apellido, email, telefono)
        self.huespedes[dni] = huesped
        return huesped

    # ---------- Check-in / Check-out ----------
    def check_in(self, dni_huesped, numero_habitacion, fecha_checkin=None):
        fecha_checkin = fecha_checkin or date.today()
        huesped = self.huespedes.get(dni_huesped)
        if huesped is None:
            raise ValueError("El huésped no está registrado")

        habitacion = self.buscar_habitacion(numero_habitacion)
        if habitacion is None:
            raise ValueError("La habitación no existe")
        if not habitacion.esta_disponible():
            raise ValueError(f"La habitación {numero_habitacion} no está disponible")

        habitacion.ocupar()
        reserva = Reserva(huesped, habitacion, fecha_checkin)
        self.reservas.append(reserva)
        self.reservas_activas[numero_habitacion] = reserva
        return reserva

    def check_out(self, numero_habitacion, fecha_checkout=None):
        fecha_checkout = fecha_checkout or date.today()
        reserva = self.reservas_activas.get(numero_habitacion)
        if reserva is None:
            raise ValueError("No hay una reserva activa para esa habitación")

        reserva.cerrar(fecha_checkout)
        reserva.habitacion.liberar()
        del self.reservas_activas[numero_habitacion]
        return reserva

    # ---------- Servicios adicionales ----------
    def agregar_servicio_a_estadia(self, numero_habitacion, clave_servicio):
        reserva = self.reservas_activas.get(numero_habitacion)
        if reserva is None:
            raise ValueError("No hay una reserva activa para esa habitación")
        return reserva.agregar_servicio(clave_servicio)

    # ---------- Estadísticas de ocupación ----------
    def estadisticas_ocupacion(self):
        total = len(self.habitaciones)
        ocupadas = len([h for h in self.habitaciones if h.estado == EstadoHabitacion.OCUPADA])
        disponibles = len([h for h in self.habitaciones if h.estado == EstadoHabitacion.DISPONIBLE])
        mantenimiento = len([h for h in self.habitaciones
                             if h.estado == EstadoHabitacion.MANTENIMIENTO])

        porcentaje_ocupacion = (ocupadas / total * 100) if total > 0 else 0

        por_tipo = {}
        for tipo in TipoHabitacion:
            habitaciones_tipo = [h for h in self.habitaciones if h.tipo == tipo]
            ocupadas_tipo = [h for h in habitaciones_tipo
                             if h.estado == EstadoHabitacion.OCUPADA]
            if habitaciones_tipo:
                por_tipo[tipo.value] = {
                    "total": len(habitaciones_tipo),
                    "ocupadas": len(ocupadas_tipo),
                    "porcentaje": round(len(ocupadas_tipo) / len(habitaciones_tipo) * 100, 1)
                }

        return {
            "total_habitaciones": total,
            "ocupadas": ocupadas,
            "disponibles": disponibles,
            "en_mantenimiento": mantenimiento,
            "porcentaje_ocupacion_general": round(porcentaje_ocupacion, 1),
            "por_tipo": por_tipo,
        }

    def mostrar_estadisticas(self):
        stats = self.estadisticas_ocupacion()
        print(f"\n=== Estadísticas de ocupación - {self.nombre} ===")
        print(f"Total de habitaciones: {stats['total_habitaciones']}")
        print(f"Ocupadas: {stats['ocupadas']}")
        print(f"Disponibles: {stats['disponibles']}")
        print(f"En mantenimiento: {stats['en_mantenimiento']}")
        print(f"Ocupación general: {stats['porcentaje_ocupacion_general']}%")
        print("\nOcupación por tipo de habitación:")
        for tipo, datos in stats["por_tipo"].items():
            print(f"  {tipo}: {datos['ocupadas']}/{datos['total']} ({datos['porcentaje']}%)")


# ============================================================
# CARGA INICIAL DE DATOS DEL HOTEL
# ============================================================

def crear_hotel_de_ejemplo():
    """Crea un hotel con habitaciones precargadas de distintos tipos."""
    hotel = Hotel("Hotel Resistencia Plaza")
    hotel.agregar_habitacion(101, TipoHabitacion.INDIVIDUAL)
    hotel.agregar_habitacion(102, TipoHabitacion.INDIVIDUAL)
    hotel.agregar_habitacion(201, TipoHabitacion.DOBLE)
    hotel.agregar_habitacion(202, TipoHabitacion.DOBLE)
    hotel.agregar_habitacion(301, TipoHabitacion.SUITE)
    hotel.agregar_habitacion(302, TipoHabitacion.SUITE)
    hotel.agregar_habitacion(401, TipoHabitacion.FAMILIAR)
    return hotel


# ============================================================
# FUNCIONES AUXILIARES DE ENTRADA POR CONSOLA
# ============================================================

def pedir_entero(mensaje, minimo=None, maximo=None):
    """Pide un número entero por consola, repreguntando si es inválido o fuera de rango."""
    while True:
        valor = input(mensaje).strip()
        if not valor.isdigit():
            print("  -> Por favor ingresá un número válido.")
            continue
        numero = int(valor)
        if minimo is not None and numero < minimo:
            print(f"  -> El valor debe ser al menos {minimo}.")
            continue
        if maximo is not None and numero > maximo:
            print(f"  -> El valor no puede ser mayor a {maximo}.")
            continue
        return numero


def mostrar_precios_y_servicios():
    """Muestra el precio base de cada tipo de habitación y el catálogo de servicios."""
    print("\n--- Precios por tipo de habitación (por noche) ---")
    for tipo in TipoHabitacion:
        print(f"  {tipo.value:<12} capacidad {CAPACIDAD_MAXIMA[tipo]} pers. "
              f"- ${PRECIOS_BASE[tipo]}")

    print("\n--- Servicios adicionales disponibles ---")
    for clave, servicio in CATALOGO_SERVICIOS.items():
        print(f"  [{clave}] {servicio.nombre} - ${servicio.precio}")


def mostrar_habitaciones_disponibles(hotel: Hotel, tipo: TipoHabitacion = None):
    disponibles = hotel.habitaciones_disponibles(tipo)
    if not disponibles:
        print("  No hay habitaciones disponibles de ese tipo en este momento.")
    else:
        print("\n--- Habitaciones disponibles ---")
        for h in disponibles:
            print(f"  N° {h.numero} - {h.tipo.value} - ${h.precio_por_noche}/noche "
                  f"(capacidad {h.capacidad} pers.)")
    return disponibles


def elegir_tipo_por_cantidad_personas(cantidad_personas):
    """
    Devuelve los tipos de habitación permitidos según la cantidad de personas.
    Implementa las reglas de negocio específicas solicitadas.
    """
    tipos_permitidos = []
    
    # Problema 2: Reglas de asignación de habitaciones
    if cantidad_personas == 1:
        # 1 persona no puede pedir una habitación familiar, doble o suite, solo individual.
        tipos_permitidos = [TipoHabitacion.INDIVIDUAL]
    
    elif cantidad_personas == 2:
        # 2 personas no pueden pedir una habitación familiar pero pueden pedir 2 individuales.
        # Nota: Como el sistema reserva 1 habitación a la vez, aquí habilitamos solo las que NO son familiares.
        # Las 2 individuales se manejarían haciendo dos reservas por separado.
        tipos_permitidos = [TipoHabitacion.DOBLE, TipoHabitacion.SUITE, TipoHabitacion.INDIVIDUAL]
    
    elif cantidad_personas == 3:
        # 3 personas pueden pedir una habitación familiar, o también una doble/suite y una individual.
        tipos_permitidos = [TipoHabitacion.FAMILIAR, TipoHabitacion.DOBLE, TipoHabitacion.SUITE, TipoHabitacion.INDIVIDUAL]
    
    elif cantidad_personas == 4:
        # 4 personas pueden pedir la habitación familiar, o 2 dobles/suites, o una doble y 2 individuales.
        tipos_permitidos = [TipoHabitacion.FAMILIAR, TipoHabitacion.DOBLE, TipoHabitacion.SUITE, TipoHabitacion.INDIVIDUAL]
    
    else:
        # Para más de 4 personas, aplicamos el criterio general de capacidad
        tipos_permitidos = [tipo for tipo in TipoHabitacion if CAPACIDAD_MAXIMA[tipo] >= cantidad_personas]

    # Filtramos por capacidad real (aunque las reglas anteriores ya lo consideran)
    return [tipo for tipo in tipos_permitidos if CAPACIDAD_MAXIMA[tipo] >= cantidad_personas]


def elegir_servicios_deseados():
    """Permite al usuario elegir uno o varios servicios por clave, ingresando 'fin' para terminar."""
    seleccionados = []
    print("\nIngresá la clave del servicio que querés agregar (ej: 'desayuno').")
    print("Escribí 'fin' cuando termines, o 'ninguno' si no querés servicios adicionales.")
    while True:
        clave = input("Servicio deseado: ").strip().lower()
        if clave in ("fin", "ninguno", ""):
            break
        if clave not in CATALOGO_SERVICIOS:
            print(f"  -> '{clave}' no es un servicio válido. Opciones: "
                  f"{', '.join(CATALOGO_SERVICIOS.keys())}")
            continue
        
        # Problema 1: no se debe poder añadir más de un mismo servicio.
        if clave in seleccionados:
            print(f"  -> El servicio '{CATALOGO_SERVICIOS[clave].nombre}' ya está en tu lista.")
            continue
            
        seleccionados.append(clave)
        print(f"  -> Agregado: {CATALOGO_SERVICIOS[clave].nombre}")
    return seleccionados


# ============================================================
# FLUJO PRINCIPAL: RESERVAR UNA HABITACIÓN
# ============================================================

def realizar_reserva(hotel: Hotel):
    print("\n=== NUEVA RESERVA ===")

    # 1. El sistema presenta precios, servicios y habitaciones disponibles
    mostrar_precios_y_servicios()
    mostrar_habitaciones_disponibles(hotel)

    # 2. El usuario ingresa la cantidad de personas
    cantidad_personas = pedir_entero("\n¿Para cuántas personas es la reserva? ", minimo=1)

    tipos_posibles = elegir_tipo_por_cantidad_personas(cantidad_personas)
    if not tipos_posibles:
        print("No hay ningún tipo de habitación con esa capacidad. Reserva cancelada.")
        return

    # Mostrar solo las habitaciones disponibles que alcanzan para esa cantidad de personas
    opciones = []
    for tipo in tipos_posibles:
        opciones.extend(hotel.habitaciones_disponibles(tipo))

    if not opciones:
        print("No hay habitaciones disponibles con capacidad suficiente en este momento.")
        return

    print(f"\nHabitaciones disponibles para {cantidad_personas} persona(s):")
    for h in opciones:
        print(f"  N° {h.numero} - {h.tipo.value} - ${h.precio_por_noche}/noche "
              f"(capacidad {h.capacidad} pers.)")

    numeros_validos = [h.numero for h in opciones]
    while True:
        numero_habitacion = pedir_entero("\nIngresá el número de habitación que elegís: ")
        if numero_habitacion in numeros_validos:
            break
        print("  -> Ese número no está en la lista de disponibles. Intentá de nuevo.")

    # 3. Datos del huésped
    print("\n--- Datos del huésped ---")
    
    # Problema 1: dni debe tener si o si 8 digitos
    while True:
        dni = input("DNI: ").strip()
        if dni.isdigit() and len(dni) == 8:
            break
        print("  -> Error: El DNI debe tener exactamente 8 dígitos.")
        
    # Problema 2: nombre y apellido NO pueden llevar números
    while True:
        nombre = input("Nombre: ").strip()
        # Debe contener solo letras y espacios
        if all(c.isalpha() or c.isspace() for c in nombre) and nombre != "":
            break
        print("  -> Error: El nombre solo puede contener letras y espacios.")
        
    while True:
        apellido = input("Apellido: ").strip()
        # Debe contener solo letras y espacios
        if all(c.isalpha() or c.isspace() for c in apellido) and apellido != "":
            break
        print("  -> Error: El apellido solo puede contener letras y espacios.")
        
    # Problema 2: los nombres y apellidos deben empezar con mayúscula (Title Case)
    hotel.registrar_huesped(dni, nombre.title(), apellido.title())

    # 4. Cantidad de noches (para estimar el costo)
    # Problema 2: límite de noches (por ejemplo, 90 noches como máximo)
    noches = pedir_entero("¿Cuántas noches se va a hospedar? ", minimo=1, maximo=90)

    # 5. Servicios deseados
    servicios_elegidos = elegir_servicios_deseados()

    # 6. Confirmar check-in
    reserva = hotel.check_in(dni, numero_habitacion, date.today())
    for clave in servicios_elegidos:
        reserva.agregar_servicio(clave)

    costo_habitacion = noches * reserva.habitacion.precio_por_noche
    costo_servicios = sum(CATALOGO_SERVICIOS[c].precio for c in servicios_elegidos)
    costo_estimado = costo_habitacion + costo_servicios

    print("\n=== RESUMEN DE LA RESERVA ===")
    print(f"Huésped: {reserva.huesped}")
    print(f"Habitación: N° {reserva.habitacion.numero} ({reserva.habitacion.tipo.value})")
    print(f"Noches: {noches}")
    print(f"Servicios: {[CATALOGO_SERVICIOS[c].nombre for c in servicios_elegidos] or 'Ninguno'}")
    print(f"Costo estimado total: ${costo_estimado}")
    print("Check-in realizado con éxito.")


def realizar_checkout(hotel: Hotel):
    print("\n=== CHECK-OUT ===")
    if not hotel.reservas_activas:
        print("No hay huéspedes alojados actualmente.")
        return

    print("Habitaciones con estadía activa:")
    for numero, reserva in hotel.reservas_activas.items():
        print(f"  N° {numero} - {reserva.huesped}")

    numero_habitacion = pedir_entero("\nIngresá el número de habitación a liberar: ")
    try:
        reserva = hotel.check_out(numero_habitacion, date.today())
    except ValueError as error:
        print(f"Error: {error}")
        return

    print(f"\n{reserva}")
    print(f"Noches de estadía: {reserva.cantidad_noches()}")
    print(f"Servicios consumidos: {reserva.servicios}")
    print(f"Costo total de la estadía: ${reserva.costo_total()}")


# ============================================================
# SIMULACIÓN AUTOMÁTICA (demo sin intervención del usuario)
# ============================================================

def pausa(segundos=1.0):
    """Pequeña pausa para que la simulación se pueda leer paso a paso."""
    time.sleep(segundos)


def simulacion_reserva_hotel(hotel: Hotel = None):
    """
    Corre una simulación completa del sistema, de punta a punta,
    sin pedir ningún dato por teclado. Sirve como demostración del
    funcionamiento: registro de huésped, consulta de disponibilidad,
    check-in con servicios, estadísticas y check-out.
    """
    if hotel is None:
        hotel = crear_hotel_de_ejemplo()

    print("\n" + "=" * 60)
    print(" SIMULACIÓN AUTOMÁTICA DE RESERVA DE HOTEL")
    print("=" * 60)

    # --- Escenario simulado ---
    escenario = {
        "dni": "35789456",
        "nombre": "Martín",
        "apellido": "Ibarra",
        "cantidad_personas": 3,
        "noches": 4,
        "servicios": ["desayuno", "spa", "cochera"],
    }

    # 1. El sistema muestra precios, servicios y habitaciones disponibles
    print(f"\n[Paso 1] El sistema presenta la información general del hotel...")
    pausa()
    mostrar_precios_y_servicios()
    mostrar_habitaciones_disponibles(hotel)

    # 2. Simula el ingreso de la cantidad de personas
    cantidad_personas = escenario["cantidad_personas"]
    print(f"\n[Paso 2] El huésped indica que la reserva es para "
          f"{cantidad_personas} personas...")
    pausa()

    tipos_posibles = elegir_tipo_por_cantidad_personas(cantidad_personas)
    opciones = []
    for tipo in tipos_posibles:
        opciones.extend(hotel.habitaciones_disponibles(tipo))

    if not opciones:
        print("No hay habitaciones disponibles con capacidad suficiente. "
              "Simulación finalizada.")
        return

    print(f"\nHabitaciones que alcanzan para {cantidad_personas} persona(s):")
    for h in opciones:
        print(f"  N° {h.numero} - {h.tipo.value} - ${h.precio_por_noche}/noche "
              f"(capacidad {h.capacidad} pers.)")

    habitacion_elegida = opciones[0]  # el sistema simula elegir la primera disponible
    print(f"\n-> Se selecciona automáticamente la habitación N° "
          f"{habitacion_elegida.numero} ({habitacion_elegida.tipo.value})")
    pausa()

    # 3. Registro del huésped
    print(f"\n[Paso 3] Registrando huésped: {escenario['nombre']} {escenario['apellido']} "
          f"(DNI {escenario['dni']})...")
    hotel.registrar_huesped(escenario["dni"], escenario["nombre"], escenario["apellido"])
    pausa()

    # 4. Servicios deseados
    print(f"\n[Paso 4] El huésped solicita los siguientes servicios: "
          f"{', '.join(escenario['servicios'])}")
    pausa()

    # 5. Check-in
    print(f"\n[Paso 5] Realizando check-in...")
    reserva = hotel.check_in(escenario["dni"], habitacion_elegida.numero, date.today())
    for clave in escenario["servicios"]:
        reserva.agregar_servicio(clave)
    pausa()

    noches = escenario["noches"]
    costo_habitacion = noches * reserva.habitacion.precio_por_noche
    costo_servicios = sum(CATALOGO_SERVICIOS[c].precio for c in escenario["servicios"])
    costo_estimado = costo_habitacion + costo_servicios

    print("\n=== RESUMEN DE LA RESERVA (simulada) ===")
    print(f"Huésped: {reserva.huesped}")
    print(f"Habitación: N° {reserva.habitacion.numero} ({reserva.habitacion.tipo.value})")
    print(f"Noches estimadas: {noches}")
    print(f"Servicios: {[CATALOGO_SERVICIOS[c].nombre for c in escenario['servicios']]}")
    print(f"Costo estimado total: ${costo_estimado}")

    # 6. Estadísticas con el huésped ya alojado
    print(f"\n[Paso 6] Estadísticas de ocupación luego del check-in:")
    pausa()
    hotel.mostrar_estadisticas()

    # 7. Simulación del check-out, unos días después
    fecha_checkout_simulada = date.today() + timedelta(days=noches)
    print(f"\n[Paso 7] Simulando el paso del tiempo... llega la fecha de check-out "
          f"({fecha_checkout_simulada}).")
    pausa()

    reserva_cerrada = hotel.check_out(habitacion_elegida.numero, fecha_checkout_simulada)
    print(f"\n{reserva_cerrada}")
    print(f"Noches de estadía real: {reserva_cerrada.cantidad_noches()}")
    print(f"Servicios consumidos: {reserva_cerrada.servicios}")
    print(f"Costo total final de la estadía: ${reserva_cerrada.costo_total()}")

    # 8. Estadísticas finales
    print(f"\n[Paso 8] Estadísticas de ocupación luego del check-out:")
    pausa()
    hotel.mostrar_estadisticas()

    print("\n" + "=" * 60)
    print(" FIN DE LA SIMULACIÓN")
    print("=" * 60)

    return hotel


def menu_principal():
    hotel = crear_hotel_de_ejemplo()

    while True:
        print(f"\n============ {hotel.nombre} ============")
        print("1. Reservar una habitación (check-in)")
        print("2. Hacer check-out")
        print("3. Ver habitaciones disponibles")
        print("4. Ver estadísticas de ocupación")
        print("5. Ejecutar simulación automática de una reserva")
        print("6. Salir")

        opcion = input("Elegí una opción: ").strip()

        if opcion == "1":
            realizar_reserva(hotel)
        elif opcion == "2":
            realizar_checkout(hotel)
        elif opcion == "3":
            mostrar_habitaciones_disponibles(hotel)
        elif opcion == "4":
            hotel.mostrar_estadisticas()
        elif opcion == "5":
            simulacion_reserva_hotel(hotel)
        elif opcion == "6":
            print("¡Gracias por usar el sistema del hotel!")
            break
        else:
            print("Opción inválida, probá de nuevo.")


if __name__ == "__main__":
    menu_principal()