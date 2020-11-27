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

import config as cf
from App import model
import csv
import os

"""
El controlador se encarga de mediar entre la vista y el modelo.
Existen algunas operaciones en las que se necesita invocar
el modelo varias veces o integrar varias de las respuestas
del modelo en una sola respuesta.  Esta responsabilidad
recae sobre el controlador.
"""

# ___________________________________________________
#  Inicializacion del catalogo
# ___________________________________________________


def init():
    """
    Llama la funcion de inicializacion  del modelo.
    """
    # analyzer es utilizado para interactuar con el modelo
    analyzer = model.newAnalyzer()
    return analyzer


# ___________________________________________________
#  Funciones para la carga de datos y almacenamiento
#  de datos en los modelos
# ___________________________________________________

def loadTrips(citibike):
    for filename in os.listdir(cf.data_dir):
        if filename.endswith('.csv'):
            print('Cargando archivo: ' + filename)
            loadFile(citibike, filename)
    model.addComponents(citibike)
    return citibike

def loadFile(citibike, tripfile):

    tripfile = cf.data_dir + tripfile
    input_file = csv.DictReader(open(tripfile, encoding="utf-8"),
                                delimiter=",")
    for trip in input_file:
        model.addTrip(citibike, trip)
        model.addlocation(citibike,trip)
    return citibike



# ___________________________________________________
#  Funciones para consultas
# ___________________________________________________


def totalStops(analyzer):
    """
    Total de paradas de autobus
    """
    return model.totalStops(analyzer)


def totalConnections(analyzer):
    """
    Total de enlaces entre las paradas
    """
    return model.totalConnections(analyzer)

def totalTrips(analyzer):
    """
    Total viajes entre las paradas
    """
    return model.totalTrips(analyzer)

def criticalStations(analyzer):
    return model.criticalStations(analyzer)

def touristicRoute(latIn, lonIn, latFn, lonFn, analyzer):
    return model.touristicRoute(latIn, lonIn, latFn, lonFn, analyzer)


def clusteredStations(analyzer, id1, id2):
    return model.clusteredStations(analyzer, id1, id2)


def minimumCostPaths(analyzer, initialStation):
    """
    Calcula todos los caminos de costo minimo de initialStation a todas
    las otras estaciones del sistema
    """
    return model.minimumCostPaths(analyzer, initialStation)


def hasPath(analyzer, destStation):
    """
    Informa si existe un camino entre initialStation y destStation
    """
    return model.hasPath(analyzer, destStation)


def minimumCostPath(analyzer, destStation):
    """
    Retorna el camino de costo minimo desde initialStation a destStation
    """
    return model.minimumCostPath(analyzer, destStation)


def servedRoutes(analyzer):
    """
    Retorna el camino de costo minimo desde initialStation a destStation
    """
    maxvert, maxdeg = model.servedRoutes(analyzer)
    return maxvert, maxdeg

def routeByResistance(citibike,initialStation,resistanceTime):
    return model.routeByResistance(citibike,initialStation,resistanceTime)

def validar(anios):
    if (anios == "0-10") or (anios == "11-20") or (anios == "21-30") or (anios == "31-40") or (anios == "41-50") or (anios == "51-60") or (anios == "60+"):
        return True
    else:
        return False


def hayarEstaciones(cont, initialStation):
    return model.hayarEstaciones(cont, initialStation)

def comprobarCamino(cont, initialStation, salidas):
    return model.comprobarCamino(cont, initialStation, salidas)

def hayarMinCiclos(cont, initialStation, ciclos_existen):
    return model.hayarMinCiclos(cont, initialStation, ciclos_existen)

def recorrer_rangos(cont, rango):
    return model.estaciones_por_rango(cont, rango)

def buscarInicio(citibike, fecha1, fecha2):
    return model.buscarInicio(citibike, fecha1, fecha2)

def validarID(initialStation,cont):
    return model.validarID(initialStation, cont)

def buscarFinal(citibike, fecha1, fecha2):
    return model.buscarFinal(citibike, fecha1, fecha2)

def mejorCamino(cont, estacion_inicio, estacion_final):
    grafo = minimumCostPaths(cont, estacion_inicio)
    return minimumCostPath(grafo, estacion_final)

def ciclosEnRango(listaCiclos, tiempo_min, tiempo_max):
    return model.ciclosEnRango(listaCiclos, tiempo_min, tiempo_max)

def stationsForPublicity(citibike, ageRange):
    return model.stationsForPublicity(citibike,ageRange)

def bikesForMaintenance(citibike, bikeId, date):
    return model.bikesForMaintenance(citibike,bikeId,date)

