Cuartos = [
    {"numero": 101, "tipo": "Simple", "precio": 500000, "disponible": True},
    {"numero": 102, "tipo": "Doble", "precio": 800000, "disponible": True},
    {"numero": 201, "tipo": "Suite", "precio": 1500000, "disponible": True}
]
huespedes_activos = []

def Num_dni():
    while True:
        dni = input("Ingrese su numero de documento: ")
    
        if len(dni) == 8 and dni.isdigit():
            return int(dni)
        else:
            print("Error: El DNI ingresado no es válido.")
    

def mostrar_disponibles():
    print("\n--- Cuartos Disponibles ---")
    for hab in Cuartos:
        if hab["disponible"]:
            print(f"Cuarto {hab['numero']} - Tipo: {hab['tipo']} - Precio: ${hab['precio']}")

def registro_entrada():
    try:
        num_hab = int(input("¿En que cuarto desea hospedarse?: "))
        
        
        for hab in Cuartos:
            if hab["numero"] == num_hab:
                if hab["disponible"]:
                    print(f"Le gustaria hospedarse en el cuarto {num_hab} por ${hab['precio']} la noche?:")
                    opcion = input()
                    if opcion.lower() in ["si", "sí"]:
                        nombre = input("Nombre del huésped: ")
                        dni = Num_dni()
                        hab["disponible"] = False
                    
                        huespedes_activos.append({"nombre": nombre, "habitacion": num_hab, "dni": dni})
                        print(f"Cuarto {num_hab} registrado a nombre de {nombre}.")
                    return
                else:
                    print("Error: El cuarto ya se encuentra reservado.")
                    return
        print("Error: Cuarto no encontrado.")
    except ValueError:
        print("Error: Ingrese un número válido.")

def registro_salida():
    try:
        num_hab = int(input("Número de Cuarto5 en el que se hospedo: "))
        dias = int(input("Cantidad de dias que se hospedo: "))
    
        for hab in Cuartos:
            if hab["numero"] == num_hab:
                for h in huespedes_activos:
                    if h["habitacion"] == num_hab:
                        total = hab["precio"] * dias
                        hab["disponible"] = True
                        huespedes_activos.remove(h)
                   
                        with open("historial_pagos.txt", "a") as archivo:
                            archivo.write(f"Huesped: {h['nombre']}, Total: ${total}\n")
                    
                        print(f"Salida Registrada. Total a pagar: ${total}")
                        return
        print("No se encontró un huésped en ese Cuarto.")
    except ValueError:
        print("Error: Ingrese un número válido.")

def mostrar_estadisticas():
    total_hab = len(Cuartos)
    ocupadas = 0
    for hab in Cuartos:
        if not hab["disponible"]:
            ocupadas += 1
    
    print(f"\n--- Estadísticas ---")
    print(f"Ocupación actual: {ocupadas} de {total_hab} Cuartos")

while True:
    print("\n--- SISTEMA DE GESTIÓN HOTELERA ---")
    print("1. Ver disponibilidad")
    print("2. Registrar_Entrada")
    print("3. Registrar_Salida")
    print("4. Cuartos_Ocupados")
    print("5. Salir")
    
    opcion = input("Seleccione una opción: ")
    
    if opcion == "1":
        mostrar_disponibles()
    elif opcion == "2":
        registro_entrada()
    elif opcion == "3":
        registro_salida()
    elif opcion == "4":
        mostrar_estadisticas()
    elif opcion == "5":
        print("Saliendo del sistema...")
        break # Finaliza el bucle
    else:
        print("Opción no válida.")