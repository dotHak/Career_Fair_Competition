""" Airline Routes Writer

This script allows the user to write the possible routes between two countries 
to a file. The output file can be found in the 'Output' directory with the name
filename_output.txt

This programs accepts '.csv' and '.txt' files

The depends on the 'anytree' package and thus, requires user to install the anytree 
module in the user python environments 

The program can only be executed in command line. The program can be executed as follows:
To write only the only the optimal route
    $ python airlineRoutes.py filename.txt
To write all possible routes and optimal routes add the '--all' flag
    $ python airlineRoutes.py --all filename.txt
For help use 
    $ python airlinesRoutes.py -h
File path can be used instead of the filename. The program uses the python3 interpretor 
and the interpretor can specified. For instance, $ python3 airlineRoutes.py filename

"""


# Dependencies
import csv, sys, argparse, math, ntpath
from anytree import Node
from random import randint

def read_file(file_name):

    """ Read and returns the context from the file containing the start city and destination city

    Parameters
    ----------
    file_name: str
        The path or file name of the file containing the routes
    
    Returns
    -------
    dictionary
        a dictionary containing the filename, start city and destination city

    """

    filename = extract_filename(file_name)
    file_data = []
    if ".csv" not in file_name and ".txt" not in file_name:
        print("Error: File must be a .csv or .txt file")
        sys.exit()
    with open(file_name) as routes_csv:
        locations = csv.reader(routes_csv, delimiter=',')
        for location in locations:
            file_data.append((location[0].strip(), location[1].strip()))
            
    return {"filename" : filename.strip(), "start" : file_data[0], "destination" : file_data[1] }
    
    
def extract_filename(path):

    """ Extracts the filename from file path

    Parameters
    ----------
    path: str
        file path eg: directory/somedirectory/yourfile.txt or directory\directory\yourfile.txt

    Returns
    -------
    str
        the name of the file

    """

    head, tail = ntpath.split(path)
    return tail[:-4] 

    
def execute_argument():

    """ Processes the command line arguments

    Returns
    -------
    tuple
        a containing the file data and the optional arguments
        
    """    

    parser = argparse.ArgumentParser(description='Finds the optimal airline route.')
    parser.add_argument('file_data', metavar='filename.txt', type=read_file, nargs="+" ,
                        help='File or path containing the start city and the destination city')
    parser.add_argument('--all', dest = "show", action='store_const', const= "ALL",help='Print all possible routes and an optimal route')
               
    return  (parser.parse_args().file_data[0], parser.parse_args().show)


def find_location_code(location, country, file_name):

    """ Finds and check if the country IATA code exits in airpots.csv

    Parameters
    ----------
    location: str
        the city to search
    country: str
        the country the city is located 
    file_name: str
        the file name of the file containing the route details

    Returns
    -------
    str
        the IATA code of the city

    """

    all_codes = []
    file = open("OutputFiles/" + file_name + "_output.txt", "a")
    with open('CSVFiles/airports.csv') as airports_csv:
        airports = csv.reader(airports_csv, delimiter=',')
        for airport in airports:
            if airport[2] == location and airport[3] == country:
                 all_codes.append(airport[4])
                                    
    for city_code in all_codes:
        if city_code != "\\N":
            return city_code
    else:
        file.write("Unsupported request!\n")
        file.close()
        sys.exit(2)


def find_possible_destinations(iata_code):
    """ Finds all possible destinations(cities) from the routes.csv file

    Parameters
    ----------
    iata_code: str
        the IATA code of the city to start from.

    Returns
    -------
    set
        set of the IATA code of all the possibles cities.
    """
    all_possible_destination = []
    with open('CSVFiles/routes.csv') as routes_csv:
        routes = csv.reader(routes_csv, delimiter=',')
        for route in routes:
            if route[2] == iata_code:
                all_possible_destination.append(route[4])

    return set(all_possible_destination)


def find_possible_starts(iata_code):
    """ Find all the possible cites to move from to a destination from the routes.csv file

    Parameters
    ----------
    iata_code: str
        the IATA code of the destination city

    Returns
    -------
    set
        the set of the IATA code of all the possible start cities
    """

    all_possible_start = []
    with open('CSVFiles/routes.csv') as routes_csv:
        routes = csv.reader(routes_csv, delimiter=',')
        for route in routes:
            if route[4] == iata_code:
                all_possible_start.append(route[2])

    return set(all_possible_start)


def find_routes(start,stop,start_list, destination_list, start_node, stop_node, file_name):

    """ Find all the shortest possible routes from a location to a destination base on the number of flight

    Parameters
    ----------
    start: str 
        the IATA code of the start city
    stop: str 
        the IATA code of the destination city
    start_list: list
        all the possible destinations from the start city
    destination_list: list
        all the possible starts to the stop/destination city
    start_node: Node
        the node/tree of the start city
    stop_node: Node
        the node/tree of the destination city
    file_name: str
        the file name of the file containing the route details

    Returns
    -------
    list
        list of all the possible routes with minimum number of flights

    """

    matched_path = []
    temp_route = []
    file = open("OutputFiles/" + file_name + "_output.txt", "a")
    if stop in start_list:
        temp_route.append([start,stop])
        return temp_route
    else:
        if start_node.height < 2: 
            matched = compare(destination_list,start_list)
            for city in matched:
                reverse_path = get_path(city,stop_node)
                matched_path.append((get_path(city,start_node),reverse_path[::-1]))
            
            if len(matched_path) != 0:
                return clean_path(matched_path)
        else:
            matched = compare_node(start_list,destination_list) 

        if start_node.height == 5 and start_node == 5: 
            file.write('Unsupported request!\n')
            file.close()
            sys.exit(2)
        elif len(matched) != 0:
            for city in matched:
                reverse_path = get_path_from_tree(city[1][0],city[1][1],stop_node)
                matched_path.append((get_path_from_tree(city[0][0],city[0][1],start_node),reverse_path[::-1]))
            return clean_path(matched_path)

        elif start_node.height == stop_node.height:
            start_l = retrieve_leaves(start_node)
            start_n = build_search_tree(start_node, start_l, find_possible_destinations)
            return find_routes(start, stop, start_n.leaves,stop_node.leaves, start_n, stop_node, file_name)
        else:
            stop_l = retrieve_leaves(stop_node)
            stop_n = build_search_tree(stop_node,stop_l, find_possible_starts)
            return find_routes(start, stop, start_node.leaves, stop_n.leaves, start_node,stop_n, file_name)
    

def build_search_tree(node, possible_list, list_function):
    """ Build the search tree of a route

    Parameters
    ----------
    node: Node
        the node/tree of the start/destination city
    possible_list: list
        the list of all possible cities to/from the a node
    list_function: function
        the function that returns the list all the possible starts/destination to/from a node

    Returns
    -------
    Node
        the new built tree/node
    """
    tree = node
    if tree.is_leaf:
        for city in possible_list:
            Node(city,parent=tree)
    else:
        for city in tree.leaves:
            for location in list_function(city.name):
                Node(location, parent=city)
    return tree


def compare(start_lists, destination_lists):
    """ Compares if any city in the start lists is in the destination lists

    Parameters
    ----------
    start_lists: list
        list of all possible destinations from the start city
    destination_lists:
        list of all the possible starts to the destination city

    Returns
    -------
    list
        all the cities found in both lists 
    """
    possible_matches = []
    for city in start_lists:
        if city in destination_lists:
            possible_matches.append(city)
    return possible_matches


def compare_node(start_lists, destination_lists):
    """ Compare if any city node in the start lists is in the destinations lists

    Parameters
    ----------
    start_lists: list
        list of nodes of all possible destinations from the start city
    destination_lists:
        list of nodes of all the possible starts to the destination city

    Returns
    -------
    list
        all the city nodes found in both lists 

    """
    possible_matches = []
    for city in start_lists:
        for city2 in destination_lists:
            if city2.name == city.name:
                possible_matches.append(((city, city.parent),(city2, city2.parent)))

    return possible_matches


def retrieve_leaves(node):

    """ Retrieves list of the names of leaves the search tree
    
    Parameters
    ----------
    node: Node
        the search tree/node
    
    Returns
    -------
    list
        the list of all the names of the leaves in the search tree/node
    """

    leaves_list = []
    for city_node in node.leaves:
        leaves_list.append(city_node.name)
    
    return leaves_list


def get_path_from_tree(node, parent, tree):

    """ Finds the path of a node
    
    Parameters
    ----------
    node: Node
        the node to find the path
    parent: Node
        the parent of node
    tree: tree
        the tree of the node

    Returns
    -------
    lists
        a list of  path from the root to the node
    """

    for some_node in tree.leaves:
        if some_node.name == node.name and some_node.path[:-1] == parent.path:
            return some_node.path  


def get_path(node, tree):

    """ Finds the path of a node

    Parameters
    ----------
    node: str 
        the name of the node to find the path
    tree: Node
        the Node/tree of the node

    Returns
    -------
    list
        a list of  path from the root to the node
    
    """

    for some_node in tree.leaves:
        if some_node.name == node:
            return some_node.path  


def clean_path(paths_list):

    """ Returns lists of the path using the names

    Parameters
    ----------
    paths_list: list
        the list of the path using Nodes

    Returns
    -------
    list
        a list of all the paths

    """

    cleaned_path = []
    for route_paths in paths_list:
        temp = []
        for route_path in route_paths[0]:
            if type(route_path) is str:
                temp.append(route_path)
            else:
                temp.append(route_path.name)
        if route_paths[1] is not None:
            for route_path1 in route_paths[1]:
                if type(route_path1) is str:
                    if temp[len(temp)-1] != route_path1:
                        temp.append(route_path1)
                else:
                    if temp[len(temp)-1] != route_path1.name:
                        temp.append(route_path1.name)
        cleaned_path.append(temp)
    return cleaned_path 


def write_routes(routes_lists,file_name):

    """Writes the all the routes to the output file

    Parameters
    ----------
    routes_lists: list
        the list of all the possible paths for the route
    file_name: str
        the name of the file containing the route details

    """

    file = open("OutputFiles/" + file_name + "_output.txt", "a")
    file.write("All Routes\n")
    file.write("------------------------------\n\n")
    for path in routes_lists:
        file.write(f'Route from {path[0]} to path {path[len(path) - 1]}\n')
        file.write("------------------------------\n")
        total_stops = 0
        for i in range(0, len(path)-1):
            all_flight_details = find_flight_details(path[i],path[i+1])
            airline,stop_number = randomize_airline_list(all_airlines(all_flight_details), all_flight_details)
            file.write(f'{i+1}. {airline} from {path[i]} to {path[i+1]} {stop_number} stops\n')
            total_stops += stop_number
        file.write(f'Total flights: {len(path) -1}\n')
        file.write(f'Total additional stops: {total_stops}\n\n\n')
    file.close()


def write_optimal_route(optimal_route, file_name):

    """Writes the all the routes to the output file

    Parameters
    ----------
    optimal_route: list
        the list of all the possible paths for the route
    file_name: str
        the name of the file containing the route details

    """
    
    file = open("OutputFiles/" + file_name + "_output.txt", "a")
    path = optimal_route[0]
    file.write(f'Optimal route from {path[0]} to {path[len(path)-1]}\n')
    file.write("------------------------------\n")
    total_stops = 0
    for i in range(0, len(path)-1):
        all_flight_details = find_flight_details(path[i],path[i+1])
        airline,stop_number = randomize_airline_list(all_airlines(all_flight_details), all_flight_details) 
        file.write(f'{i+1}. {airline} from {path[i]} to {path[i+1]} {stop_number} stops\n')
        total_stops += stop_number  
    file.write(f'Total flights: {len(path) -1}\n')
    file.write(f'Total additional stops: {total_stops}\n')
    file.write(f'Total distance: {round(optimal_route[1], 2)} km\n')
    file.write('Optimality criteria: flights and distance\n\n\n')
    file.close()


def calculate_distance(start_city,end_city):

    """Calculate the the distance between two cities

    Parameters
    ----------
    start_city: tuple
        a tuple of the latitude and the longitude of the start city
    end_city: tuple
        a tuple of the latitude and the longitude of the stop/destination city

    Returns
    -------
    float
        the distance between the two cities using the Haversine formula 

    """
    latitude1 = math.radians(float(start_city[0]))
    latitude2 = math.radians(float(end_city[0]))
    longitude1 = math.radians(float(start_city[1]))
    longitude2 = math.radians(float(end_city[1]))
    r = 6371
    value1 = (math.sin((latitude2 - latitude1)/2))**2
    value2 = math.cos(latitude1) * math.cos(latitude2) *(math.sin((longitude2 - longitude1)/2))**2
    d = math.sqrt(value1 + value2)
    return 2 * r * math.asin(d)


def calculate_total_distance(path_list):

    """ Calculate the total distance of a path

    Parameters
    ----------
    path_list: list
        the path of a route

    Returns
    ------- 
    float
        the total distance of the path
    """
    total_distance = 0
    for i in range(0, len(path_list)-1):
        total_distance += calculate_distance(path_list[i],path_list[i+1])
    return total_distance


def find_location(code):

    """ Finds the latitude and longitude of a city

    Parameter
    ---------
    code: str
        the IATA code of a city

    Returns
    -------
    tuple
        a tuple of the latitude and longitude of the city

    """
    with open('CSVFiles/airports.csv') as airports_csv:
        airports = csv.reader(airports_csv, delimiter=',')
        for airport in airports:
            if airport[4] == code:
                return (airport[6], airport[7])


def find_path_location(path_list):

    """ Finds the latitude and longitude of a path

    Parameter
    ---------
    path_list: list
        a list of IATA code of a path

    Returns
    -------
    list
        a list of the latitude and longitude of the path

    """
    path_code = []
    temp = []
    for path in path_list:
        for city in path:
            temp.append(find_location(city))
        path_code.append(temp)
        temp = []
    return path_code


def find_flight_details(start_code, end_code):

    """ Finds the airline id and stops of a path

    Parameter
    ---------
    start_code: str
        the IATA code of the start city
    stop_city: str
        the IATA code of the stop city
    Returns
    -------
    list 
        a list of the airline id and stops of the path
    """

    all_list = []
    with open('CSVFiles/routes.csv') as routes_csv:
        routes = csv.reader(routes_csv, delimiter=',')
        for route in routes:
            if route[2] == start_code and route[4] == end_code:
                all_list.append((int(route[1]), int(route[7])))

    return all_list   


def all_airlines(flight_details):

    """ Finds the airline id from the flight details

    Parameter
    ---------
    flight_details: list
        the list of the flight id and stops from a path

    Returns
    -------
    list
        a list of the IATA code and ICAO code of the path

    """

    airline_list = []
    for detail in flight_details:
        airline_list.append(find_airline(detail[0]))
    return airline_list


def find_airline(number):
    """ Finds the IATA coe and ICAO code of the airline id

    Parameter
    ---------
    number: int
        the airline id of the route

    Returns
    -------
    tuple
        a tuple of the IATA code and ICAO code of the airline

    """
    with open('CSVFiles/airlines.csv') as airlines_csv:
        airlines = csv.reader(airlines_csv, delimiter=',')
        for airline in airlines:
            if int(airline[0]) == number and airline[7] == "Y":
                return (airline[3],airline[4])


def randomize_airline_list(lists, flight_details):  

    """ Returns a random IATA code or ICAO code and the number of stops 
        of an airline from the airline list 

    Parameter
    ---------
    lists: list
        the list of all the airlines 
    flight_details: list
        the list of the airlines and the number of stops the route

    Returns
    -------
    tuple
        a tuple of the IATA code or ICAO code and the number stops

    """  

    random = randint(0, len(lists)-1)
    if len(lists[random][0]) != 0 and lists[random][0] != "\\N":
        return lists[random][0],flight_details[random][1]
    elif len(lists[random][1]) != 0 and lists[random][1] != "\\N":
        return lists[random][1],flight_details[random][1]
    else:
        return randomize_airline_list(lists,flight_details)


def find_optimal_route(path_locations, path_lists):
    """ Finds the optimal routes from all the paths

    Parameter
    ---------
    path_locations: list
        the list of the latitudes and longitudes of the path
    path_lists: list
        the list of all the path for the routes 

    Returns
    -------
    list
        the optimal path of the routes

    """

    optimal_route = []
    
    for i in range(0, len(path_locations)):
        isLocation = True
        for position in path_locations[i]:
            if type(position) is not tuple:
                isLocation = False

        if isLocation:
            distance = calculate_total_distance(path_locations[i])
            if len(optimal_route) == 0:
                optimal_route = [path_lists[i], distance]
            elif optimal_route[1] > distance:
                optimal_route = [path_lists[i],distance]
            
    return optimal_route


def main():
    """ Execute the program
    """
    route_info = execute_argument()[0]
    other_argument = execute_argument()[1]
    file_name = route_info['filename']
    start_code = find_location_code(route_info['start'][0],route_info['start'][1],file_name)
    destination_code = find_location_code(route_info['destination'][0],route_info['destination'][1],file_name)
    
    all_possible_starts = find_possible_starts(destination_code)
    all_possible_destinations = find_possible_destinations(start_code)
    start_node = build_search_tree(Node(start_code), all_possible_destinations, find_possible_destinations)
    destination_node = build_search_tree(Node(destination_code),all_possible_starts, find_possible_starts)

    all_possible_routes = find_routes(start_code, destination_code, all_possible_destinations, all_possible_starts, start_node, destination_node, file_name)
    
    path_locations = find_path_location(all_possible_routes)

    optimal_route = find_optimal_route(path_locations, all_possible_routes)
    
    if other_argument == "ALL":
        write_routes(all_possible_routes, file_name)
        write_optimal_route(optimal_route,file_name)
    else:
        write_optimal_route(optimal_route,file_name)


if __name__ == "__main__":
    # Code execution
    main()
