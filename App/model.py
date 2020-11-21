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
import config
from DISClib.ADT.graph import gr
from DISClib.ADT import map as m
from DISClib.DataStructures import mapentry as me
from DISClib.ADT import list as lt
from DISClib.ADT import minpq as mq
from DISClib.DataStructures import listiterator as it
from DISClib.Algorithms.Graphs import scc
from DISClib.Algorithms.Graphs import dijsktra as djk
from DISClib.Utils import error as error
from math import radians, cos, sin, asin, sqrt 
assert config

"""
En este archivo definimos los TADs que vamos a usar y las operaciones
de creacion y consulta sobre las estructuras de datos.
"""

# -----------------------------------------------------
#                       API
# -----------------------------------------------------

# Funciones para agregar informacion al grafo
def newAnalyzer():
    """ Inicializa el analizador

   stops: Tabla de hash para guardar los vertices del grafo
   connections: Grafo para representar las rutas entre estaciones
   components: Almacena la informacion de los componentes conectados
   paths: Estructura que almancena los caminos de costo minimo desde un
           vertice determinado a todos los otros vértices del grafo
    """
    try:
        analyzer = {
                    'stops': None,
                    'connections': None,
                    'components': None,
                    'paths': None,
                    'graph':None,
                    'location':None
                    }

        analyzer['stops'] = m.newMap(numelements=14000,
                                     maptype='PROBING',
                                     comparefunction=compareStopIds)

        analyzer['connections'] = gr.newGraph(datastructure='ADJ_LIST',
                                              directed=True,
                                              size=14000,
                                              comparefunction=compareStopIds)

        analyzer['location'] = m.newMap(numelements=14000,
                                     maptype='PROBING',
                                     comparefunction=compareStopIds)

        return analyzer
    except Exception as exp:
        error.reraise(exp, 'model:newAnalyzer')


def addTrip(citibike, trip):
    """
    """
    origin = trip['start station id']
    destination = trip['end station id']
    duration = int(trip['tripduration'])
    addStation(citibike, origin)
    addStation(citibike, destination)
    addConnection(citibike, origin, destination, duration)

def addStation(citibike, stationid):
    """
    Adiciona una estación como un vertice del grafo
    """
    #Para el reto calcular prom de tiempo entre los vertices y guardarlos.
    if not gr.containsVertex(citibike['connections'], stationid):
        gr.insertVertex(citibike['connections'], stationid)
    return citibike

def addConnection(citibike, origin, destination, duration):
    """
    Adiciona un arco entre dos estaciones
    """
    edge = gr.getEdge(citibike["connections"], origin, destination)
    if edge is None:
        gr.addEdge(citibike["connections"], origin, destination, duration)
    return citibike




# Funciones para agregar informacion al grafo

def addStopConnection(analyzer, lastservice, service):
    """
    Adiciona las estaciones al grafo como vertices y arcos entre las
    estaciones adyacentes.

    Los vertices tienen por nombre el identificador de la estacion
    seguido de la ruta que sirve.  Por ejemplo:

    75009-10

    Si la estacion sirve otra ruta, se tiene: 75009-101
    """
    try:
        origin = formatVertex(lastservice)
        destination = formatVertex(service)
        cleanServiceDistance(lastservice, service)
        distance = float(service['Distance']) - float(lastservice['Distance'])
        addStop(analyzer, origin)
        addStop(analyzer, destination)
        addConnection(analyzer, origin, destination, distance)
        addRouteStop(analyzer, service)
        addRouteStop(analyzer, lastservice)
        return analyzer
    except Exception as exp:
        error.reraise(exp, 'model:addStopConnection')


def addStop(analyzer, stopid):
    """
    Adiciona una estación como un vertice del grafo
    """
    try:
        if not gr.containsVertex(analyzer['connections'], stopid):
            gr.insertVertex(analyzer['connections'], stopid)
        return analyzer
    except Exception as exp:
        error.reraise(exp, 'model:addstop')


def addRouteStop(analyzer, service):
    """
    Agrega a una estacion, una ruta que es servida en ese paradero
    """
    entry = m.get(analyzer['stops'], service['BusStopCode'])
    if entry is None:
        lstroutes = lt.newList(cmpfunction=compareroutes)
        lt.addLast(lstroutes, service['ServiceNo'])
        m.put(analyzer['stops'], service['BusStopCode'], lstroutes)
    else:
        lstroutes = entry['value']
        info = service['ServiceNo']
        if not lt.isPresent(lstroutes, info):
            lt.addLast(lstroutes, info)
    return analyzer

def addlocation(analyzer, trip):
    """
    Agrega a una estacion, su posición en latitud y longitud
    """
    entry1 = m.get(analyzer['location'], trip['end station id'])
    entry2 =  m.get(analyzer['location'], trip['start station id'])
    if entry1 is None:
        m.put(analyzer['location'], trip["end station id"], (float(trip["end station latitude"]),float(trip["end station longitude"])))
    if entry2 is None:
        m.put(analyzer['location'], trip["start station id"], (float(trip["start station latitude"]),float(trip["start station longitude"])))
    return analyzer


def addRouteConnections(analyzer):
    """
    Por cada vertice (cada estacion) se recorre la lista
    de rutas servidas en dicha estación y se crean
    arcos entre ellas para representar el cambio de ruta
    que se puede realizar en una estación.
    """
    lststops = m.keySet(analyzer['stops'])
    stopsiterator = it.newIterator(lststops)
    while it.hasNext(stopsiterator):
        key = it.next(stopsiterator)
        lstroutes = m.get(analyzer['stops'], key)['value']
        prevrout = None
        routeiterator = it.newIterator(lstroutes)
        while it.hasNext(routeiterator):
            route = key + '-' + it.next(routeiterator)
            if prevrout is not None:
                addConnection(analyzer, prevrout, route, 0)
                addConnection(analyzer, route, prevrout, 0)
            prevrout = route


#

# ==============================
# Funciones de consulta
# ==============================


def connectedComponents(analyzer):
    """
    Calcula los componentes conectados del grafo
    Se utiliza el algoritmo de Kosaraju
    """
    analyzer['components'] = scc.KosarajuSCC(analyzer['connections'])
    return scc.connectedComponents(analyzer['components'])


def minimumCostPaths(analyzer, initialStation):
    """
    Calcula los caminos de costo mínimo desde la estacion initialStation
    a todos los demas vertices del grafo
    """
    analyzer['paths'] = djk.Dijkstra(analyzer['connections'], initialStation)
    return analyzer


def hasPath(analyzer, destStation):
    """
    Indica si existe un camino desde la estacion inicial a la estación destino
    Se debe ejecutar primero la funcion minimumCostPaths
    """
    return djk.hasPathTo(analyzer['paths'], destStation)


def minimumCostPath(analyzer, destStation):
    """
    Retorna el camino de costo minimo entre la estacion de inicio
    y la estacion destino
    Se debe ejecutar primero la funcion minimumCostPaths
    """
    path = djk.pathTo(analyzer['paths'], destStation)
    return path


def totalStops(analyzer):
    """
    Retorna el total de estaciones (vertices) del grafo
    """
    return gr.numVertices(analyzer['connections'])


def totalConnections(analyzer):
    """
    Retorna el total arcos del grafo
    """
    return gr.numEdges(analyzer['connections'])

def totalTrips(analyzer):
    master = analyzer["connections"]
    vertex = gr.vertices(master)
    iterator = it.newIterator(vertex)
    trips = []
    while it.hasNext(iterator):
        element = it.next(iterator)
        adjacents = gr.adjacents(master,element)
        iterator2 = it.newIterator(adjacents)
        while it.hasNext(iterator2) and element != None:
            element2 = it.next(iterator2)
            pair = (element,element2)
            if pair not in trips and (element2,element) not in trips:
                trips.append(pair)
    return len(trips)


def servedRoutes(analyzer):
    """
    Retorna la estación que sirve a mas rutas.
    Si existen varias rutas con el mismo numero se
    retorna una de ellas
    """
    lstvert = m.keySet(analyzer['stops'])
    itlstvert = it.newIterator(lstvert)
    maxvert = None
    maxdeg = 0
    while(it.hasNext(itlstvert)):
        vert = it.next(itlstvert)
        lstroutes = m.get(analyzer['stops'], vert)['value']
        degree = lt.size(lstroutes)
        if(degree > maxdeg):
            maxvert = vert
            maxdeg = degree
    return maxvert, maxdeg

def criticalStations(analyzer):
    vertexs = gr.vertices(analyzer["connections"])
    indegree = mq.newMinPQ(compareinverted)
    outdegree = mq.newMinPQ(compareinverted)
    degree = mq.newMinPQ(comparenormal)
    iterator = it.newIterator(vertexs)
    res1 = lt.newList()
    res2 = lt.newList()
    res3 = lt.newList()
    while it.hasNext(iterator):
        element = it.next(iterator)
        ins = (element,int(gr.indegree(analyzer["connections"],element)))
        out = (element,int(gr.outdegree(analyzer["connections"],element)))
        deg = (element,int(gr.indegree(analyzer["connections"],element))+int(gr.outdegree(analyzer["connections"],element)))
        mq.insert(indegree,ins)
        mq.insert(outdegree,out)
        mq.insert(degree,deg)

    for a in range(1,4):
        lt.addLast(res1,mq.delMin(indegree))
        lt.addLast(res2,mq.delMin(outdegree))
        lt.addLast(res3,mq.delMin(degree)) 
        
    return (res1,res2,res3)

def distance(lat1, lat2, lon1, lon2):
    if type(lat1) == float and type(lon1) == float:
        lon1 = radians(lon1) 
        lon2 = radians(lon2) 
        lat1 = radians(lat1) 
        lat2 = radians(lat2)    
        dlon = lon2 - lon1  
        dlat = lat2 - lat1 
        a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
        c = 2 * asin(sqrt(a))   
        r = 6371
        return(c * r)
    else:
        return "a" 

def touristicRoute(latIn, lonIn, latFn, lonFn, analyzer):
    vertexs = gr.vertices(analyzer["connections"])
    iterator = it.newIterator(vertexs)
    sal = ()
    lleg = ()
    while it.hasNext(iterator):
        element = it.next(iterator)
        locationp = m.get(analyzer["location"],element)
        location = me.getValue(locationp)

        distance1 = distance(latIn,location[0],lonIn,location[1])
        distance2 = distance(latFn,location[0],lonFn,location[1])

        if sal == ():
            sal = (element,distance1)
        elif distance1 < sal[1]:
            sal = (element,distance1)

        if lleg == ():
            lleg = (element,distance2)
        elif distance2 < lleg[1]:
            lleg = (element,distance2)

    analyzer = minimumCostPaths(analyzer,sal[0])
    minpath = minimumCostPath(analyzer,lleg[0])
    time = djk.distTo(analyzer["paths"],lleg[0])

    return (sal[0],lleg[0],minpath,time)




# ==============================
# Funciones Helper
# ==============================

def cleanServiceDistance(lastservice, service):
    """
    En caso de que el archivo tenga un espacio en la
    distancia, se reemplaza con cero.
    """
    if service['Distance'] == '':
        service['Distance'] = 0
    if lastservice['Distance'] == '':
        lastservice['Distance'] = 0


def formatVertex(service):
    """
    Se formatea el nombrer del vertice con el id de la estación
    seguido de la ruta.
    """
    name = service['BusStopCode'] + '-'
    name = name + service['ServiceNo']
    return name


# ==============================
# Funciones de Comparacion
# ==============================

def compareStations(stop, keyvaluestop):
    """
    Compara dos estaciones
    """
    
    try:
        addTrip(stop, keyvaluestop);
    except:
        print("error")


def compareStopIds(stop, keyvaluestop):
    """
    Compara dos estaciones
    """
    stopcode = keyvaluestop['key']
    if (stop == stopcode):
        return 0
    elif (stop > stopcode):
        return 1
    else:
        return -1


def compareroutes(route1, route2):
    """
    Compara dos rutas
    """
    if (route1 == route2):
        return 0
    elif (route1 > route2):
        return 1
    else:
        return -1

def comparenormal(tup1, tup2):
    num1 = tup1[1]
    num2 = tup2[1]
    if (num1 == num2):
        return 0
    elif (num1 > num2):
        return 1
    else:
        return -1
        
def compareinverted(tup1, tup2):
    num1 = tup1[1]
    num2 = tup2[1]
    if (num1 == num2):
        return 0
    elif (num1 > num2):
        return -1
    else:
        return 1
        