﻿"""
 * Copyright 2020, Departamento de sistemas y Computación,
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
 * along withthis program.  If not, see <http://www.gnu.org/licenses/>.
 *
 * Contribuciones:
 *
 * Dario Correal - Version inicial
 """


import config as cf
from DISClib.ADT import list as lt
from DISClib.ADT import map as mp
from DISClib.DataStructures import mapentry as me
from DISClib.Algorithms.Sorting import shellsort as sa
from DISClib.ADT.graph import gr
from DISClib.Algorithms.Graphs import scc
from DISClib.Algorithms.Graphs import dijsktra as djk
from DISClib.Utils import error as error
from DISClib.Algorithms.Sorting import mergesort as Merge
import haversine as hs
assert cf

"""
Se define la estructura de un catálogo de videos. El catálogo tendrá dos listas, una para los videos, otra para las categorias de
los mismos.
"""

# Construccion de modelos

def newAnalyzer():
    try:
        analyzer = {'LandingPoint': None,'connectionsDistance': None,'connectionsCapacity': None,'countrysInfo':None}

        analyzer['LandingPoint'] = mp.newMap(numelements=1290,maptype='PROBING',comparefunction=compareCountryNames)

        analyzer['connectionsDistance'] = gr.newGraph(datastructure='ADJ_LIST',directed=False,size=3500,comparefunction=compareLanCableIds)

        analyzer['connectionsCapacity'] = gr.newGraph(datastructure='ADJ_LIST',directed=False,size=3500,comparefunction=compareLanCableIds)

        analyzer['countriesInfo'] = mp.newMap(numelements=240, maptype='PROBING', comparefunction=compareCountryNames)

        return analyzer
    except Exception as exp:
        error.reraise(exp, 'model:newAnalyzer')

# Funciones para agregar informacion al catalogo

def AddLandingPointsData(analyzer, Entry):
    entry = mp.get(analyzer['LandingPoint'], Entry['landing_point_id'])
    if entry is None:
        CaracEntry = CreateLandingInfo()
    else:
        CaracEntry = me.getValue(entry)
    lt.addLast(CaracEntry['lstData'], Entry)
    mp.put(analyzer['LandingPoint'],Entry['landing_point_id'],CaracEntry)
    return analyzer

def addLandingConnection(analyzer, Entry):
    try:
        origin = formatVertexOring(Entry)
        destination = formatVertexDestination(Entry)
        distance = CalculateDistance(analyzer,Entry)
        addLandingVertexDistance(analyzer, origin)
        addLandingVertexDistance(analyzer, destination)
        addLandingVertexCapacity(analyzer, destination)
        addLandingVertexCapacity(analyzer, destination)
        addConnectionDistance(analyzer, origin, destination, distance)
        capacity = Entry['capacityTBPS']
        addConnectionCapacity(analyzer, origin, destination,capacity)
        addLandingsRoutes(analyzer, Entry)
        return analyzer
    except Exception as exp:
        error.reraise(exp, 'model:addLandingConnection')

def AddCountry(Analyzer,country):
    Name = country['CountryName']
    existName = mp.contains(Analyzer['countriesInfo'], Name)
    if existName:
        entry = mp.get(Analyzer['countriesInfo'], Name)
        NameCountry = me.getValue(entry)
    else:
        NameCountry = newCountryValues()
        mp.put(Analyzer['countriesInfo'], Name, NameCountry)
    lt.addLast(NameCountry['countriesInfo'], country)
    return Analyzer

def addLandingVertexDistance(analyzer, LandingId):
    try:
        if not gr.containsVertex(analyzer['connectionsDistance'], LandingId):
            gr.insertVertex(analyzer['connectionsDistance'], LandingId)
        return analyzer
    except Exception as exp:
        error.reraise(exp, 'model:addLandingVertex')

def addLandingVertexCapacity(analyzer, LandingId):
    try:
        if not gr.containsVertex(analyzer['connectionsCapacity'], LandingId):
            gr.insertVertex(analyzer['connectionsCapacity'], LandingId)
        return analyzer
    except Exception as exp:
        error.reraise(exp, 'model:addLandingVertex')

def addLandingsRoutes(analyzer, Entry):
    entry = mp.get(analyzer['LandingPoint'], Entry['origin'])
    try:
        entry = me.getValue(entry)
        CableName = Entry['cable_name']
        CapacityValue = Entry['capacityTBPS']
        if not lt.isPresent(entry['lstCables'], CableName):
            lt.addLast(entry['lstCables'], CableName)
        if not lt.isPresent(entry['lstCapacity'], CapacityValue):
            lt.addLast(entry['lstCapacity'], CapacityValue)
        mp.put(analyzer['LandingPoint'], Entry['origin'], entry)
        return analyzer
    except Exception as exp:
        error.reraise(exp, 'model:InexistenciaLanding')

def addRouteConnections(analyzer):
    lststops = mp.keySet(analyzer['LandingPoint'])
    for key in lt.iterator(lststops):
        lstCables = mp.get(analyzer['LandingPoint'], key)
        lstCables = me.getValue(lstCables)['lstCables']
        lstCables = CapacityOrder(lstCables)
        prevCableName = None
        for CableName in lt.iterator(lstCables):
            CableName = key + '-' + CableName
            capacity = lt.getElement(lstCables,1)
            if prevCableName is not None:
                addConnectionDistance(analyzer, prevCableName, CableName, 100)
                addConnectionCapacity(analyzer, prevCableName, CableName, capacity)
            prevCableName = CableName

def addConnectionDistance(analyzer, origin, destination, distance):
    edge = gr.getEdge(analyzer['connectionsDistance'], origin, destination)
    if edge is None:
        gr.addEdge(analyzer['connectionsDistance'], origin, destination, distance)
    return analyzer

def addConnectionCapacity(analyzer, origin, destination, Capacity):
    try:
        edge = gr.getEdge(analyzer['connectionsCapacity'], origin, destination)
        if edge is None:
            gr.addEdge(analyzer['connectionsCapacity'], origin, destination, Capacity)
        return analyzer
    except:
        pass
# Funciones para creacion de datos

def CreateLandingInfo():
    entry = {'lstData':None,'lstCables':None,'lstCapacity':None}
    entry['lstData'] = lt.newList('ARRAY_LIST')
    entry['lstCables'] = lt.newList('ARRAY_LIST',cmpfunction=compareCableName)
    entry['lstCapacity'] = lt.newList('ARRAY_LIST',cmpfunction=compareCableName)
    return entry

def newCountryValues():
    Values = {"countriesInfo": None}
    Values['countriesInfo'] = lt.newList('ARRAY_LIST')
    return Values

def formatVertexOring(Entry):
    name = Entry['origin'] + '-'
    name = name + Entry['cable_name']
    return name
    
def formatVertexDestination(Entry):
    name = Entry['destination'] + '-'
    name = name + Entry['cable_name']
    return name

# Funciones de consulta

def InfoCatalog(analyzer):
    sizeCountries = lt.size(mp.keySet(analyzer['countriesInfo']))
    totLandingPoints = lt.size(mp.keySet(analyzer['LandingPoint']))
    totConections = gr.numEdges(analyzer['connectionsDistance'])
    return sizeCountries,totLandingPoints,totConections

def CalculateDistance(analyzer,Entry):
    oring = Entry['origin']
    destination = Entry['destination']
    Info1 = mp.get(analyzer['LandingPoint'],oring)
    Info2 = mp.get(analyzer['LandingPoint'],destination)
    try:
        latitude1 = me.getValue(Info1)['lstData']
        latitude1 = float(lt.getElement(latitude1,1)['latitude'])
        latitude2 = me.getValue(Info2)['lstData']
        latitude2 = float(lt.getElement(latitude2,1)['latitude'])
    except:
        pass
    try:
        longitude1 = me.getValue(Info1)['lstData']
        longitude1 = float(lt.getElement(longitude1,1)['longitude'])
        longitude2 = me.getValue(Info2)['lstData']
        longitude2 = float(lt.getElement(longitude2,1)['longitude'])
    except:
        pass
    loc1=latitude1,longitude1
    loc2=latitude2,longitude2
    distance = hs.haversine(loc1,loc2)
    distance *= 1000
    return distance

#Funciones Comparacion

def compareLanCableIds(LanCable, keyvalueLanCable):
    LanCablecode = keyvalueLanCable['key']
    if (LanCable == LanCablecode):
        return 0
    elif (LanCable > LanCablecode):
        return 1
    else:
        return -1

def compareroutes(connection1, connection2):
    if (connection1 == connection2):
        return 0
    elif (connection1 > connection2):
        return 1
    else:
        return -1

def compareCountryNames(Name1, Name2):
    Name = me.getKey(Name2)
    if (Name1 == Name):
        return 0
    elif (Name1 > Name):
        return 1
    else:
        return -1

def compareCableName(Cable1, Cable2):
    if (Cable1 == Cable2):
        return 0
    elif (Cable1 > Cable2):
        return 1
    else:
        return -1

def CapacityOrder(listaOrdenada):
    sub_list = lt.subList(listaOrdenada, 1, lt.size(listaOrdenada))
    sub_list = sub_list.copy()
    sorted_list = Merge.sort(sub_list, cmpCapacitys)
    return sorted_list

def cmpCapacitys(video1, video2):
    return video1 < video2