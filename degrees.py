import csv
import sys

from util import Node, StackFrontier, QueueFrontier

# Maps names to a set of corresponding person_ids
names = {}

# Maps person_ids to a dictionary of: name, birth, movies (a set of movie_ids)
people = {}

# Maps movie_ids to a dictionary of: title, year, stars (a set of person_ids)
movies = {}


def load_data(directory):
    """
    Load data from CSV files into memory.
    """
    # Load people
    with open(f"{directory}/people.csv", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            people[row["id"]] = {
                "name": row["name"],
                "birth": row["birth"],
                "movies": set()
            }
            if row["name"].lower() not in names:
                names[row["name"].lower()] = {row["id"]}
            else:
                names[row["name"].lower()].add(row["id"])

    # Load movies
    with open(f"{directory}/movies.csv", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            movies[row["id"]] = {
                "title": row["title"],
                "year": row["year"],
                "stars": set()
            }

    # Load stars
    with open(f"{directory}/stars.csv", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                people[row["person_id"]]["movies"].add(row["movie_id"])
                movies[row["movie_id"]]["stars"].add(row["person_id"])
            except KeyError:
                pass


def main():
    if len(sys.argv) > 2:
        sys.exit("Usage: python degrees.py [directory]")
    directory = sys.argv[1] if len(sys.argv) == 2 else "large"

    # Load data from files into memory
    print("Loading data...")
    load_data(directory)
    print("Data loaded.")

    source = person_id_for_name(input("Name: "))
    if source is None:
        sys.exit("Person not found.")
    target = person_id_for_name(input("Name: "))
    if target is None:
        sys.exit("Person not found.")

    path = shortest_path(source, target)

    if path is None:
        print("Not connected.")
    else:
        degrees = len(path)
        print(f"{degrees} degrees of separation.")
        path = [(None, source)] + path
        for i in range(degrees):
            person1 = people[path[i][1]]["name"]
            person2 = people[path[i + 1][1]]["name"]
            movie = movies[path[i + 1][0]]["title"]
            print(f"{i + 1}: {person1} and {person2} starred in {movie}")


def shortest_path(source, target):
    """
    Returns the shortest list of (movie_id, person_id) pairs
    that connect the source to the target.

    If no possible path, returns None.
    """
    frontier = QueueFrontier()
    number_explored = 0
    exploredSet = set()

    neighbors = neighbors_for_person(source)

    for neighbor in neighbors:
        #print(neighbor)
        node = Node(state=(neighbor[0], neighbor[1]), parent=None, action=None)
        frontier.add(node)

    while True:
        if frontier.empty():
            break

        node = frontier.remove()
        if node not in exploredSet:
            exploredSet.add(node)

            if node.state[1] == target:
                solution_list = []
                for index in node:
                    solution_list.append(index.parent[0], index.parent[2])
                    return solution_list
            else:
                new_neighbors = neighbors_for_person(node.state[1])
                for new_neighbor in new_neighbors:
                    new_node = Node(state=(new_neighbor[0], new_neighbor[1]), parent=(node.state[0], node.state[1]), action=None)
                    frontier.add(new_node)

    #node = frontier.remove()

    # while True:
    #     if frontier.empty():
    #         raise Exception("no solution")
    #     if node.state == target:
    #         actions = []
    #         cells = []

    #         while node.parent is not None:
    #             cells.append(node.state)
    #             node = node.parent
    #         solution = cells.reverse()
    #         return solution
    #     exploredSet.add(node.state)
    #     for movie_id, person_id in neighbors:
    #         if not frontier.contains_state(person_id) and movie_id not in exploredSet:
    #             child = Node(state=(movie_id, person_id), parent=node,action=None)
    #             frontier.add(child)


    # for element in neighbors:
    #     node = Node(element, source, None)
    #     print(node)
    #     frontier.add(QueueFrontier, node)
    #     print(frontier)

    # currentNode = frontier.remove()
    # #if currentNode.state

    

    # solution = [] # this list will contain a touple like this: [(1, 2), (3, 4)]
    
    # first = (1,1)
    # second = (2,2)
    # solution.append(first)
    # solution.append(second)

    # #create for loop that looks at all of the elements in solution. (in reverse I think)
    # # Create touple of 2 strings. 
    # # (source in movieId, with actorId), (neighbor in movieId, with actorId)

    # if len(solution) == 0:
    #     return 'None'
    # print(solution)
    # # TODO
    # raise NotImplementedError


def person_id_for_name(name):
    """
    Returns the IMDB id for a person's name,
    resolving ambiguities as needed.
    """
    person_ids = list(names.get(name.lower(), set()))
    if len(person_ids) == 0:
        return None
    elif len(person_ids) > 1:
        print(f"Which '{name}'?")
        for person_id in person_ids:
            person = people[person_id]
            name = person["name"]
            birth = person["birth"]
            print(f"ID: {person_id}, Name: {name}, Birth: {birth}")
        try:
            person_id = input("Intended Person ID: ")
            if person_id in person_ids:
                return person_id
        except ValueError:
            pass
        return None
    else:
        return person_ids[0]


def neighbors_for_person(person_id):
    """
    Returns (movie_id, person_id) pairs for people
    who starred with a given person.
    """
    movie_ids = people[person_id]["movies"]
    neighbors = set()
    for movie_id in movie_ids:
        for person_id in movies[movie_id]["stars"]:
            neighbors.add((movie_id, person_id))
    return neighbors


if __name__ == "__main__":
    main()
