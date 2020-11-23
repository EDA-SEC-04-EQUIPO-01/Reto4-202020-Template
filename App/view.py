"""
 * Copyright 2020, Departamento de sistemas y Computación
 * Universidad de Los Andes
 *
 *
 * Desarrolado para el curso ISIS1225 - Estructuras de Datos y Algoritmos
 *
 *
 * This program is free software: you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this program.  If not, see <http://www.gnu.org/licenses/>.
 * Contribución de:
 *
 * Dario Correal
 *
 """


import sys
import config
from App import controller
from DISClib.ADT import stack
import timeit
assert config

"""
La vista se encarga de la interacción con el usuario.
Presenta el menu de opciones  y  por cada seleccion
hace la solicitud al controlador para ejecutar la
operación seleccionada.
"""

# ___________________________________________________
#  Variables
# ___________________________________________________


# ___________________________________________________
#  Menu principal
# ___________________________________________________
initialStation = None
recursionLimit = 20000

def printMenu():
    print("\n")
    print("*******************************************")
    print("Bienvenido")
    print("1- Inicializar Analizador")
    print("2- Cargar información de buses de New York")
    print("3- Calcular la cantidad de clusters de viajes")
    print("4- Establecer estación base:")
    print("5- Hay camino entre estacion base y estación: ")
    print("6- Ruta de costo mínimo desde la estación base y estación: ")
    print("7- Estación que sirve a mas rutas: ")
    print("0- Salir")
    print("*******************************************")


def optionTwo():
    print("\nCargando información de transporte de New York ....")

    controller.loadTrips(cont)

    numedges = controller.totalConnections(cont)
    numvertex = controller.totalStops(cont)
    numtrips = controller.totalTrips(cont)
    print('Numero de vertices: ' + str(numvertex))
    print('Numero de arcos: ' + str(numedges))
    print('Numero de viajes: ' + str(numtrips))
    print('El limite de recursion actual: ' + str(sys.getrecursionlimit()))
    sys.setrecursionlimit(recursionLimit)
    print('El limite de recursion se ajusta a: ' + str(recursionLimit))


def optionThree():
    id1 = input("Introduzca una estación: ")
    id2 = input("Introduzca la otra estación para saber si pertenecen al mismo cluster: ")
    clustered = controller.clusteredStations(cont, id1, id2)
    print('El número clusters en el grafo es: ' + str(clustered[0]))
    if clustered[1]==True:
        print("Las estaciones", id1, "y", id2, "pertenecen al mismo cluster.")
    elif clustered[1]=="":
        print("Alguna de las estaciones no existe en nuestra base de datos.")
    else:
        print("Las estaciones no pertenecen al mismo cluster")


def optionFour():  #N
    rango_min=int(input("Ingresa el tiempo minimo  para hacer una ruta: "))
    rango_max=int(input("Ingresa el tiempo maximo para hacer una ruta: "))
    # controller.minimumCostPaths(cont, initialStation)
    respuesta = controller.recorrer_dfo(cont, initialStation)
    print("la respuesta es: ", respuesta)
    # rango_min, rango_max


def optionFive():
    haspath = controller.hasPath(cont, destStation)
    print('Hay camino entre la estación base : ' +
          'y la estación: ' + destStation + ': ')
    print(haspath)


def optionSix():
    path = controller.minimumCostPath(cont, destStation)
    if path is not None:
        pathlen = stack.size(path)
        print('El camino es de longitud: ' + str(pathlen))
        while (not stack.isEmpty(path)):
            stop = stack.pop(path)
            print(stop)
    else:
        print('No hay camino')



def optionSeven():   #N
    validacion = controller.rango_edad(anios)
    if validacion[0]:
        print(validacion[1], "hasta ", validacion[2])
        #tupla con valor 0 el nombre de la parada y 1 la cantidad
        inicio = controller.buscarInicio(cont, validacion[1], validacion[2])
        print(inicio)
        final = controller.buscarFinal(cont, validacion[1], validacion[2])
        print(final)
        camino = 0 #usar min cost path
        print(camino)
    else:
        print("No ingresaste un rango valido, revisa las opciones de nuevo.")



"""
Menu principal
"""
while True:
    printMenu()
    inputs = input('Seleccione una opción para continuar\n>')

    if int(inputs[0]) == 1:
        print("\nInicializando....")
        # cont es el controlador que se usará de acá en adelante
        cont = controller.init()

    elif int(inputs[0]) == 2:
        executiontime = timeit.timeit(optionTwo, number=1)
        print("Tiempo de ejecución: " + str(executiontime))

    elif int(inputs[0]) == 3:
        executiontime = timeit.timeit(optionThree, number=1)
        print("Tiempo de ejecución: " + str(executiontime))

    #N
    elif int(inputs[0]) == 4:      
        msg = "Estación Base: BusStopCode-ServiceNo (Ej: 75009-10): "
        initialStation = input(msg)
        executiontime = timeit.timeit(optionFour, number=1)
        print("Tiempo de ejecución: " + str(executiontime))

    elif int(inputs[0]) == 5:
        destStation = input("Estación destino (Ej: 15151-10): ")
        executiontime = timeit.timeit(optionFive, number=1)
        print("Tiempo de ejecución: " + str(executiontime))

    elif int(inputs[0]) == 6:
        destStation = input("Estación destino (Ej: 15151-10): ")
        executiontime = timeit.timeit(optionSix, number=1)
        print("Tiempo de ejecución: " + str(executiontime))

    #N
    elif int(inputs[0]) == 7:
        print("Los rango de edad son: \n0-10\n11-20\n21-30\n31-40\n41-50\n51-60\n60+")
        anios = input("Ingresa tu rango de edad: ")
        executiontime = timeit.timeit(optionSeven, number=1)
        print("Tiempo de ejecución: " + str(executiontime))

    else:
        sys.exit(0)
sys.exit(0)

