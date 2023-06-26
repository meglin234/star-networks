import os
import sys
import json
import networkx as nx
import matplotlib.pyplot as plt
import argparse

#TO PUT IN COMMAND LINE (remember to take out the #s):
'''python gen_networkv3.py -er "Additional Crew, Animation Department, Art Department, Art Direction by, Camera and Electrical Department, Cast,
Casting By, Casting Department, Costume and Wardrobe Department, Editorial Department, Location Management, Music Department, Produced by, Production Department,
Production Management, Visual Effects by, Script and Continuity Department, Second Unit Director or Assistant Director, Set Decoration by, Stunts, Thanks, Transportation Department" -n'''

def set_dir_attr(G, dir_id, dir_credits):
    
    with open(dir_credits, 'r') as f:
        dir_credits_json = json.load(f)
        name = dir_credits_json['First Name'] + ' ' + dir_credits_json['Last Name']
        del dir_credits_json['First Name']
        del dir_credits_json['Last Name']
        dir_credits_json['name'] = name
           
        # Set the node type to 'director' only if it is not already set or if it is currently set to 'crew'
        dir_credits_json['type'] = 'director'

        nx.set_node_attributes(G, {dir_id: dir_credits_json})

def update_networkx(G, dir_id, crewmembers, excluded_roles, normalize):
    
    # Check if the current node is a director

    for crew in crewmembers:        
        if( 'role' not in crew ):
            continue
        if normalize:
            crew=make_normalized_dict(crew)

        if( crew['role'] == 'Directed by') or (crew['role'] in excluded_roles):
            continue

        for c in crew['crew']:
            crew_id = c['id']
            crew_name = c['name']
            roles = crew['role']
            
            if G.has_edge(dir_id, crew_id):
                G.edges[dir_id, crew_id]['weight'] += 1
            else:
                G.add_edge(dir_id, crew_id, weight=1)
            
            typ = 'director' if G.nodes[crew_id].get('type', '') == 'director' else 'crew'

            attributes = {'name': crew_name,'roles':roles, 'type': typ}
            nx.set_node_attributes(G, {crew_id: attributes})

def get_mov_credit_frm_file(movie_cred_file):

    movie_credits = []
    with open(movie_cred_file, 'r') as infile:
        for cred in infile:
            cred = json.loads(cred)
            movie_credits.append(cred)

    return movie_credits

def generate_dir_crew_network(excluded_roles, normalize):
    counter = 0
    dataset = './director_crew_info'
    dir_folders = os.listdir(dataset)
    G=nx.DiGraph()

    for dir_id in dir_folders:

        if( dir_id.startswith('.') ):
            continue

        #print(dir_id)
        director_file = f'{dataset}/{dir_id}/{dir_id}.json'
        credits_file = f'{dataset}/{dir_id}/feature_films/'
        movie_credits = os.listdir(credits_file)
        #print(dir_id)
        for movie_cred in movie_credits:
            if( movie_cred.startswith('.') ):
                continue
            
            #print(movie_cred)
            movie_cred = f'{credits_file}{movie_cred}'
            movie_cred = get_mov_credit_frm_file(movie_cred)
            #print(movie_cred)
            #update_network(movie_cred)
            #print(movie_cred)
            update_networkx(G, dir_id, movie_cred, excluded_roles, normalize)
        
        set_dir_attr(G, dir_id, director_file)
        counter += 1
        print(counter)
    
    print('writing graph to file - start')
    nx.write_gexf(G, "z5.gexf")
    print('writing graph to file - end')

        #print(dir_id)
       # print(dir_id)
        #if counter == 10:
            #break
    #print(counter)
        #break
            #print(movie_cred)
            #print(len(movie_cred))
            
    #nx.write_gexf(G, "movies.gexf")
            #nx.draw(G)
            #plt.savefig('directors.png', dpi=300)
            
            

def normalize_role(role):
    if role=="Casting By" or role=="Casting Department":
        return role
    elif role.startswith("Cast"):
        return "Cast"
    elif role.startswith("Writing Credits"):
        return "Writing Credits"
    else:
        return role

def make_normalized_dict(role_dict):
    role=role_dict["role"]
    if (role != "Cast" and role.startswith('Cast')) or (role != "Writing Credits" and role.startswith('Writing Credits')):
        normalized_role=normalize_role(role)
        role_dict["role"]=normalized_role
    return role_dict

def get_roles_from_movie_list(movie_cred):
    roles=set()
    for x in movie_cred:
        if "role" not in x.keys():
            continue
        roles.add(x["role"])
    return roles


def get_all_possible_roles():
    roles_all_movies=set()
    dataset = './director_crew_info'
    dir_folders = os.listdir(dataset)
    for dir_id in dir_folders:
        credits_file = f'{dataset}/{dir_id}/feature_films/'
        movie_credits = os.listdir(credits_file)
        #iterate through each movie for a director
        for movie_cred in movie_credits:
            movie_cred = f'{credits_file}{movie_cred}'
            movie_cred =  get_mov_credit_frm_file(movie_cred)
            roles_one_movie=get_roles_from_movie_list(movie_cred)
            #print(len(roles_one_movie))
            roles_all_movies.update(roles_one_movie)
    return sorted(roles_all_movies)

#Possible Roles for a Feature Film (not normalized)
# 1) Additional Crew
# 2) Animation Department
# 3) Art Department
# 4) Art Direction by
# 5) Camera and Electrical Department
# 6) Cast
# 7) Cast (in credits order)
# 8) Cast (in credits order) complete, awaiting verification
# 9) Cast (in credits order) verified as complete
#10) Cast complete, awaiting verification
#11) Casting By
#12) Casting Department
#13) Cinematography by
#14) Costume Design by
#15) Costume and Wardrobe Department
#16) Directed by
#17) Editorial Deparment
#18) Film Editing by 
#19) Location Management
#20) Makeup Department
#21) Music Department
#22) Music by
#23) Produced by
#24) Production Department
#25) Production Design by
#26) Production Management
#27) Script and Continuity Department
#28) Second Unit Director or Assistant Director
#29) Set Decoration by
#30) Sound Department
#31) Special Effects by
#32) Stunts
#33) Thanks
#34) Transportation Department
#35) Visual Effects by
#36) Writing Credits
#37) Writing Credits (WGA)
#38) Writing Credits (WGA) (in alphabetical order)
#39) Writing Credits (in alphabetical order)


def main(excluded_roles, normalize):
    generate_dir_crew_network(excluded_roles, normalize)

if __name__ == '__main__':
    
    parser=argparse.ArgumentParser()
    parser.add_argument("-er", "--excluded_roles", help="list of roles to exclude from the graph", type=str)
    parser.add_argument("-n", "--normalize", help="normalize the roles that are variants of Cast and Writing Credits", action="store_true")

    args=parser.parse_args()
    #print(args.normalize)
    excluded_roles=[]
    if args.excluded_roles:
        excluded_roles=args.excluded_roles.split(', ')
    #print(excluded_roles)
    main(excluded_roles, args.normalize)




