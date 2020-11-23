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
from DISClib.ADT import list as lt
from DISClib.DataStructures import listiterator as it
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
    print("2- Cargar información de buses de singapur")
    print("3- Calcular componentes conectados")
    print("4- Establecer estación base:")
    print("5- Conocer estaciones más concurridas y la menos concurridas: ")
    print("6- Ruta de costo mínimo desde la estación base y estación: ")
    print("7- Estación que sirve a mas rutas: ")
    print("8- Ruta turística más eficiente: ")
    print("0- Salir")
    print("*******************************************")


def optionTwo():
    print("\nCargando información de transporte de singapur ....")
    controller.loadTrips(cont) 
    numedges = controller.totalConnections(cont)
    numvertex = controller.totalStops(cont)
    #numtrips = controller.totalTrips(cont)
    print('Numero de vertices: ' + str(numvertex))
    print('Numero de arcos: ' + str(numedges))
    #print('Numero de viajes: ' + str(numtrips))
    print('El limite de recursion actual: ' + str(sys.getrecursionlimit()))
    sys.setrecursionlimit(recursionLimit)
    print('El limite de recursion se ajusta a: ' + str(recursionLimit))


def optionThree():
    print('El número de componentes conectados es: ' +
          str(controller.connectedComponents(cont)))


def optionFour():
    controller.minimumCostPaths(cont, initialStation)


def optionFive():
    critical = controller.criticalStations(cont)
    print("\nLas estaciones Top de llegada son: \n")
    iterator = it.newIterator(critical[0])
    while it.hasNext(iterator):
        a = it.next(iterator)
        print("Estación {0} con {1} llegadas.".format(a[0],a[1]))
    
    print("\nLas estaciones Top de salida son: \n")
    iterator = it.newIterator(critical[1])
    while it.hasNext(iterator):
        a = it.next(iterator)
        print("Estación {0} con {1} salidas.".format(a[0],a[1]))

    print("\nLas estaciones menos concurridas son: \n")
    iterator = it.newIterator(critical[2])
    while it.hasNext(iterator):
        a = it.next(iterator)
        print("Estación {0} con {1} llegadas y salidas.".format(a[0],a[1]))

    
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


def optionSeven():
    maxvert, maxdeg = controller.servedRoutes(cont)
    print('Estación: ' + maxvert + '  Total rutas servidas: '
          + str(maxdeg))

def optionEight():
    try:
        lat1 = float(input("Inserte la latitud de salida: "))
        lon1 = float(input("Inserte la longitud de salida: "))
        lat2 = float(input("Inserte la latitud de llegada: "))
        lon2 = float(input("Inserte la longitud de llegada: "))
        res = controller.touristicRoute(lat1,lon1,lat2,lon2,cont)
        print("La estación más cercana a la posición {0}, {1} (salida) es: {2}".format(lat1,lon1,res[0]))
        print("La estación más cercana a la posición {0}, {1} (llegada) es: {2}".format(lat2,lon2,res[1]))
        if res[2] != None:
            print("La ruta más corta desde la estación {0} hasta la estación {1} es {2}.\nEsta ruta tiene una duración de {3}.".format(res[0],res[1],res[2],res[3]))
        else:
            print("No existe una ruta entre estas dos estaciones.")
    except:
        print("Ingrese valores válidos")
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

    elif int(inputs[0]) == 4:
        msg = "Estación Base: BusStopCode-ServiceNo (Ej: 75009-10): "
        initialStation = input(msg)
        executiontime = timeit.timeit(optionFour, number=1)
        print("Tiempo de ejecución: " + str(executiontime))

    elif int(inputs[0]) == 5:
        executiontime = timeit.timeit(optionFive, number=1)
        print("Tiempo de ejecución: " + str(executiontime))

    elif int(inputs[0]) == 6:
        destStation = input("Estación destino (Ej: 15151-10): ")
        executiontime = timeit.timeit(optionSix, number=1)
        print("Tiempo de ejecución: " + str(executiontime))

    elif int(inputs[0]) == 7:
        executiontime = timeit.timeit(optionSeven, number=1)
        print("Tiempo de ejecución: " + str(executiontime))

    elif int(inputs[0]) == 8:
        executiontime = timeit.timeit(optionEight, number=1)
        print("Tiempo de ejecución: " + str(executiontime))

    else:
        sys.exit(0)
sys.exit(0)

