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
from DISClib.DataStructures import edge as ed
from DISClib.ADT import stack as st
from DISClib.ADT.graph import gr
from DISClib.ADT import map as m
from DISClib.DataStructures import mapentry as me
from DISClib.ADT import list as lt
from DISClib.DataStructures import listiterator as it
from DISClib.Algorithms.Graphs import scc
from DISClib.Algorithms.Graphs import bfs
from DISClib.Algorithms.Graphs import dijsktra as djk
from DISClib.Utils import error as error
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
                    'stations':None,
                    'births':None
                    }

        analyzer['stops'] = m.newMap(numelements=14000,
                                     maptype='PROBING',
                                     comparefunction=compareStopIds)

        analyzer['connections'] = gr.newGraph(datastructure='ADJ_LIST',
                                              directed=True,
                                              size=768,
                                              comparefunction=compareStopIds)
        analyzer['stations']=m.newMap(numelements=1536,
                                      maptype = "PROBING",
                                      loadfactor=0.5,
                                      comparefunction=compareStopIds)
        analyzer['births']=m.newMap(numelements=14,
                                    maptype = "PROBING",
                                    loadfactor= 0.5,
                                    comparefunction= compareStopIds)


        return analyzer
    except Exception as exp:
        error.reraise(exp, 'model:newAnalyzer')


def addTrip(citibike, trip):
    """
    """
    origin = trip['start station id']
    destination = trip['end station id']
    duration = int(trip['tripduration'])
    birth = int(trip["birth year"])
    addBirth(citibike, origin, destination, birth)
    addStation(citibike, origin)
    addStation(citibike, destination)
    addConnection(citibike, origin, destination, duration)

def addRoute(intro, origin):
    if m.get(intro,origin) is None:
        m.put(intro, origin, 1)
        intro_num =1
    else:
        m.put(intro, origin, me.getValue(m.get(intro,origin))+1)
        intro_num =me.getValue(m.get(intro,origin))+1
    return intro_num

def addMax(intro, intro_num, origin):
    if intro_num > me.getValue(m.get(intro, "Max"))[0]:
        m.put(intro, "Max", [intro_num, origin])

def addBirth(citibike,origin,destination,birth):
    age = 2020-birth
    rango = None
    if age<=10:
        rango = "0-10"
    elif age<=20:
        rango = "11-20"
    elif age <=30:
        rango = "21-30"
    elif age <=40:
        rango = "31-40"
    elif age <= 50:
        rango = "41-50"
    elif age <=60:
        rango = "51-60"
    else:
        rango = "60+"
    if m.get(citibike["births"], rango) is None:
        miniHash = m.newMap(numelements=2, 
                            maptype="CHAINING", 
                            loadfactor=1, 
                            comparefunction=compareStopIds)
        miniHashIntro = m.newMap(numelements=1536, 
                            maptype="PROBING", 
                            loadfactor=0.5, 
                            comparefunction=compareStopIds)
        miniHashOutro = m.newMap(numelements=1536, 
                            maptype="PROBING", 
                            loadfactor=0.5, 
                            comparefunction=compareStopIds)
        m.put(miniHash, "Intro", miniHashIntro)
        m.put(miniHash, "Outro", miniHashOutro)
        m.put(miniHashIntro, "Max", [0, None])
        m.put(miniHashOutro, "Max", [0,None])
        m.put(citibike["births"], rango, miniHash)
    tabla_rango = me.getValue(m.get(citibike["births"], rango))
    intro = me.getValue(m.get(tabla_rango,"Intro"))
    outro = me.getValue(m.get(tabla_rango,"Outro"))
    intro_num = addRoute(intro,origin)
    outro_num = addRoute(outro,destination)
    addMax(intro,intro_num,origin)
    addMax(outro,outro_num,destination)
        
def addStation(citibike, stationid):
    """
    Adiciona una estación como un vertice del grafo
    """
    
    if not gr.containsVertex(citibike['connections'], stationid):
        gr.insertVertex(citibike['connections'], stationid)
    return citibike

def addConnection(citibike, origin, destination, duration):
    """
    Adiciona un arco entre dos estaciones
    """
    
    if origin != destination:
        edge = gr.getEdge(citibike ["connections"], origin, destination)

        if edge is None:
            if m.get(citibike["stations"], origin) is None:
                repetitions = m.newMap(numelements=1536,
                                    maptype="PROBING", 
                                    loadfactor=0.5, 
                                    comparefunction=compareStopIds)
                m.put(citibike["stations"],origin, repetitions)
            repetitions = me.getValue(m.get(citibike["stations"], origin))
            m.put(repetitions,destination, [duration, 1])
            gr.addEdge(citibike["connections"], origin, destination, duration)
        else:
            one_rep = m.get(citibike["stations"],origin)
            repetitions = me.getValue(one_rep)
            two_rep = m.get(repetitions, destination)
            repetitions_destination = me.getValue(two_rep)
            repetitions_destination[0]+=duration
            repetitions_destination[1]+=1
            duration = repetitions_destination[0]/repetitions_destination[1]
            ed.setWeight(edge, duration)
    return citibike

def addComponents(citibike):
    citibike['components'] = scc.KosarajuSCC(citibike['connections'])
# ==============================
# Funciones de consulta
# ==============================

def connectedComponents(analyzer):
    """
    Calcula los componentes conectados del grafo
    Se utiliza el algoritmo de Kosaraju
    """
    return scc.connectedComponents(analyzer['components'])

def clusteredStations(citibike, id1,id2):
    try:
        clusters = connectedComponents(citibike)
        isThereCluster = scc.stronglyConnected(citibike["components"], id1,id2)
        retorno = (clusters, isThereCluster)
    except:
        retorno = (clusters, "")
    return retorno

def getElement(entry):
    try:
        return me.getValue(entry)
    except:
        return None

def routeByResistance(citibike, initialStation, resistanceTime):
    graph_dfs = bfs.BreadhtFisrtSearch(citibike["connections"], initialStation)
    keySet =m.keySet(graph_dfs["visited"])
    valueSet = m.valueSet(graph_dfs["visited"])
    iterator = it.newIterator(keySet)
    iterator2 = it.newIterator(valueSet)
    while it.hasNext(iterator):
        element = it.next(iterator)
        element2 = it.next(iterator2)
        print(bfs.pathTo(graph_dfs, element))
        print(element2)
        
        

def routeByResistance2(citibike, initialStation, resistanceTime):
    dijsktra = djk.Dijkstra(citibike["connections"], initialStation)
    vertices = gr.vertices(citibike["connections"])
    iterator = it.newIterator(vertices)
    trueStations = st.newStack()
    stops = m.newMap(numelements=768,
                    maptype="CHAINING",
                    loadfactor=1,
                    comparefunction=compareStopIds)
    while it.hasNext(iterator):
        element = it.next(iterator)
        if element != initialStation and djk.hasPathTo(dijsktra, element) is True:
            if m.get(stops, element) is None or getElement(m.get(stops, element))["value"] is False:
                if djk.distTo(dijsktra,element) <= resistanceTime:
                    pila= djk.pathTo(dijsktra,element)
                    pila2 = djk.pathTo(dijsktra,element)
                    size_pila = 0
                    repetition = False
                    lon_pila = st.size(pila)
                    watcher = {"value": True}
                    while size_pila < lon_pila and repetition == False:
                        pop = st.pop(pila)["vertexB"]
                        if m.get(stops,pop) is None or getElement(m.get(stops,pop))["value"] is False:
                            m.put(stops,pop,watcher)
                        else:
                            repetition = True
                            watcher["value"]=False
                        size_pila +=1
                    if repetition == False:
                        st.push(trueStations, pila2)
    return trueStations
                    


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
        addTrip(stop, keyvaluestop)
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
        