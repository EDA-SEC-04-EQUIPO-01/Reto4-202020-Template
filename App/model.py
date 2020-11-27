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
from DISClib.ADT import stack
import config
from DISClib.DataStructures import edge as ed
from DISClib.ADT import stack as st
from DISClib.ADT.graph import gr
from DISClib.ADT import map as m
from DISClib.DataStructures import mapentry as me
from DISClib.ADT import list as lt
from DISClib.ADT import minpq as mq
from DISClib.DataStructures import listiterator as it
from DISClib.Algorithms.Graphs import scc
from DISClib.Algorithms.Graphs import bfs
from DISClib.Algorithms.Graphs import dfo
from DISClib.Algorithms.Graphs import dijsktra as djk
from DISClib.Utils import error as error
import datetime
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
                    'connections': None,
                    'components': None,
                    'paths': None,
                    'location':None,
                    'stations':None,
                    'births':None,
                    'bikes':None
                    }


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
        analyzer['bikes']=m.newMap(numelements=1536,
                                   maptype = "PROBING",
                                   loadfactor=0.5,
                                   comparefunction=compareStopIds)

        analyzer['location'] = m.newMap(numelements=14000,
                                     maptype='PROBING',
                                     comparefunction=compareStopIds)

        return analyzer
    except Exception as exp:
        error.reraise(exp, 'model:newAnalyzer')

def seeTime(timeDate1, timeDate2):
    hour1 = int(timeDate1[0:2])
    hour2 = int(timeDate2[0:2])
    minutes1 = int(timeDate1[3:6]) +hour1*60
    minutes2 = int(timeDate2[3:6])+hour2*60
    return minutes2-minutes1

def addTrip(citibike, trip):
    """
    """
    origin = trip['start station id']
    destination = trip['end station id']
    duration = int(trip['tripduration'])
    birth = int(trip["birth year"])
    userType = trip["usertype"]
    bikeId = trip["bikeid"]
    startTime = trip["starttime"]
    stopTime = trip["stoptime"]
    addBike(citibike, origin, destination, duration, bikeId, startTime,stopTime)
    addBirth(citibike, origin, destination, birth, userType)
    addStation(citibike, origin)
    addStation(citibike, destination)
    addConnection(citibike, origin, destination, duration)

def addBike(citibike, origin, destination, duration, bike, startTime,stopTime):
    bikes = m.get(citibike["bikes"], bike)
    initialDate = (datetime.datetime.strptime(startTime[0:19], '%Y-%m-%d %H:%M:%S')).date()
    finalTime = stopTime[11:16]
    initialTime = startTime[11:16]
    if bikes is None:
        datesHash = m.newMap(numelements=784,
                             maptype="PROBING",
                             loadfactor=0.5,
                             comparefunction=compareStopIds)
        m.put(citibike["bikes"], bike, datesHash)
    if m.get(me.getValue(m.get(citibike["bikes"], bike)), initialDate) is None:
        datesHash = me.getValue(m.get(citibike["bikes"], bike))
        bikes = {"routes":None,
                    "useTime":0,
                    "breakTime":0,
                    "times": None}
        bikes["routes"] = lt.newList(datastructure="ARRAY_LIST",
                               cmpfunction=compareroutes)
        bikes["times"]=st.newStack()
        m.put(datesHash,initialDate, bikes)
    datesHash = me.getValue(m.get(me.getValue(m.get(citibike["bikes"], bike)), initialDate))
    if lt.size(datesHash["routes"]) == 0:
        lt.addLast(datesHash["routes"], origin)
    else:
        lt.addLast(datesHash["routes"], destination)
        breakTime = seeTime(st.top(datesHash["times"]),initialTime)
        datesHash["breakTime"]+=breakTime
    datesHash["useTime"]+=duration/60
    st.push(datesHash["times"], finalTime)

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

def addBirth(citibike,origin,destination,birth, userType):
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
        miniHashCostumers = m.newMap(numelements=1536, 
                            maptype="PROBING", 
                            loadfactor=0.5, 
                            comparefunction=compareStopIds)
        m.put(miniHash, "Costumers", miniHashCostumers)
        m.put(miniHash, "Intro", miniHashIntro)
        m.put(miniHash, "Outro", miniHashOutro)
        m.put(miniHashIntro, "Max", [0, None])
        m.put(miniHashOutro, "Max", [0,None])
        m.put(miniHashCostumers, "Max", [0, None])
        m.put(citibike["births"], rango, miniHash)
    tabla_rango = me.getValue(m.get(citibike["births"], rango))
    intro = me.getValue(m.get(tabla_rango,"Intro"))
    outro = me.getValue(m.get(tabla_rango,"Outro"))
    if userType == "Customer":
        costumers = me.getValue(m.get(tabla_rango, "Costumers"))
        costumers_num = addRoute(costumers, origin+"-"+destination)
        addMax(costumers, costumers_num, origin+"-"+destination)
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
    try:
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
    except:
        return None
    
                    
def stationsForPublicity(citibike, ageRange):
    costumers = m.get(citibike["births"], ageRange)
    if costumers != None:
        costumers = m.get(me.getValue(costumers),"Costumers")
        costumers = m.get(me.getValue(costumers), "Max")
        costumers = me.getValue(costumers)
    return costumers

    
def bikesForMaintenance(citibike, bikeId, date):
    bikeInfo = m.get(citibike["bikes"], bikeId)
    if bikeInfo != None:
        bikeInfo = m.get(me.getValue(bikeInfo), date)
        if bikeInfo != None:
            bikeInfo = me.getValue(bikeInfo)
            numRoutes = lt.size(bikeInfo["routes"])
            breakTime = bikeInfo["breakTime"]
            useTime = bikeInfo["useTime"]
            bikeInfo = (numRoutes,breakTime,useTime)
    return bikeInfo
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
        return round((c * r),3)
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
        
        try: 
            if sal == ():
                sal = (element,distance1)
            elif distance1 < sal[1] or (distance1<=sal[1] and gr.outdegree(analyzer["connections"],element)>gr.outdegree(analyzer["connections"],sal[1])):
                sal = (element,distance1)   
        except:
            pass

        try:  
            if lleg == ():
                lleg = (element,distance2)
            elif distance2 < lleg[1] or (distance2<=lleg[1] and gr.indegree(analyzer["connections"],element)>gr.indegree(analyzer["connections"],lleg[1])):
                lleg = (element,distance2)   
        except:
            pass

    analyzer = minimumCostPaths(analyzer,sal[0])
    minpath = minimumCostPath(analyzer,lleg[0])
    time = djk.distTo(analyzer["paths"],lleg[0])

    return (sal[0],lleg[0],minpath,time)

def estaciones_por_rango(cont, rango):
    camino_mostrar=[]
    buscar_rango_hash=m.get(cont["births"],rango)
    if buscar_rango_hash == None:
        tupla = (0,0,0,0,0,0)
    else:
        variable1= me.getValue(buscar_rango_hash)
        variable2 =m.get(variable1, "Intro")
        variable3 = me.getValue(variable2)
        variable4 = m.get(variable3, "Max")
        variablesIntro = me.getValue(variable4)
        variable5 =m.get(variable1, "Outro")
        variable6 = me.getValue(variable5)
        variable7 = m.get(variable6, "Max")
        variablesOutro = me.getValue(variable7)
        if variablesIntro[1] != variablesOutro[1]:
            cont = minimumCostPaths(cont,variablesIntro[1])
            camino = minimumCostPath(cont,variablesOutro[1])
            tiempo = djk.distTo(cont["paths"],variablesOutro[1])
            iterator = it.newIterator(camino)
            while it.hasNext(iterator):
                element=it.next(iterator)
                camino_mostrar.append(element)
        else:
            camino="NINGUNO porque la estacion " +str(variablesIntro[1]) +" es la que mas viajes recibe y más arroja"
            tiempo=0

        tupla =(variablesIntro[1],variablesIntro[0],variablesOutro[1],variablesOutro[0],camino_mostrar,round(tiempo,2))
    return tupla

def hayarEstaciones(cont, initialStation):
    informacion = gr.adjacents(cont["connections"], initialStation)
    lista=[]
    if stack.isEmpty(informacion) == False:
        for i in range(0, stack.size(informacion)):
            sub_pila = stack.pop(informacion)
            lista.append(sub_pila)
    return lista

def comprobarCamino(cont, initialStation, salidas):
    lista=[]
    for a in range(0,len(salidas)):
        nuevo_scc= scc.KosarajuSCC(cont["connections"])
        verdad = scc.stronglyConnected(nuevo_scc, initialStation, salidas[a])
        if verdad:
            lista.append(salidas[a])
    if lista == []:
        lista = "NO EXISTEN"
    return lista   

def hayarMinCiclos(cont, initialStation, estaciones):
    listaCiclos=[]
    for a in range(0,len(estaciones)):
        lista=[]
        cont = minimumCostPaths(cont, initialStation)
        tiempo1 = djk.distTo(cont["paths"],estaciones[a]) #tiempo de Inicio a V1
        lista=["Hay un camino que empieza en "+str(initialStation)+" y va a " +str(estaciones[a]) +" en un tiempo de "+str(round(tiempo1))+" segundos que se conecta asi:"]
        cont = minimumCostPaths(cont, estaciones[a])
        tiempo2 = djk.distTo(cont["paths"],initialStation)
        minimumCostPaths(cont, estaciones[a])
        path2 = minimumCostPath(cont, initialStation)
        iterator = it.newIterator(path2)
        tiempo_visita=0
        while it.hasNext(iterator):
            element=it.next(iterator)
            lista.append(element)
            tiempo_visita+=20
        tiempo_total= tiempo1/60+tiempo2/60+tiempo_visita
        tupla=(lista,round(tiempo_total))
        listaCiclos.append(tupla) 
    return listaCiclos

def ciclosEnRango(listaCiclos, tiempo1, tiempo2):
    lista=[]
    for a in range(0,len(listaCiclos)):
        unCiclo = listaCiclos[a]
        if (tiempo1 < int(unCiclo[1]) and ( int(unCiclo[1]) < tiempo2)):
            crear= str(unCiclo[0]) +" Es un ciclo que tarda " +str(round(unCiclo[1],2)) +" MINUTOS, contando que puedas disfrutar de cada estacion 20 minutos!"
            lista.append(crear)
    return lista


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
        

