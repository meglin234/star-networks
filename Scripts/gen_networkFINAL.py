import os #import necessary modules 
import json
import networkx as nx
import argparse



#TO PUT IN COMMAND LINE:
'''python gen_networkFINAL.py -er "Additional Crew, Animation Department, Art Department, Art Direction by, Camera and Electrical Department, Cast, Casting By, Casting Department, Costume and Wardrobe Department, Editorial Department, Location Management, Music Department, Produced by, Production Department, Production Management, Visual Effects by, Script and Continuity Department, Second Unit Director or Assistant Director, Set Decoration by, Stunts, Thanks, Transportation Department" -n'''

def set_dir_attr(G, dir_id, dir_credits): # sets attributes for the director
    
    with open(dir_credits, 'r') as f:
        dir_credits_json = json.load(f) # load json file
        name = dir_credits_json['First Name'] + ' ' + dir_credits_json['Last Name'] 
        del dir_credits_json['First Name'] # remove first and last name keys
        del dir_credits_json['Last Name']
        dir_credits_json['name'] = name # add new name key that combines first and last nam
           
        # Set the node type to 'director' only if it is not already set or if it is currently set to 'crew'
        dir_credits_json['type'] = 'director'

        nx.set_node_attributes(G, {dir_id: dir_credits_json}) # set director attribute

def assign_weights_to_crew(role_frequency_for_crew, role_frequency_among_movies, dir_id, G):
    for role, crew_dist in role_frequency_for_crew.items(): # iterates over frequency of roles
        for crew_id, co_feat_count in crew_dist.items(): # iterate over crewmembers
            #if crew member is credited for more than one role
            if ('role' in G.get_edge_data(dir_id,crew_id).keys()) and (G.edges[dir_id, crew_id]['role'] != role):
                if co_feat_count<=G[dir_id][crew_id]['weight']:
                    continue
            # xs
            G[dir_id][crew_id]['weight'] = co_feat_count/role_frequency_among_movies[role] # update weights between director and crewmembers
            weight_numerator=co_feat_count
            weight_denominator=role_frequency_among_movies[role]
            edge_attributes={'role':role, 'weight_numerator': weight_numerator, 'weight_denominator': weight_denominator} # creates attributes
            nx.set_edge_attributes(G, {(dir_id, crew_id): edge_attributes}) # set attributes


def update_networkx(G, dir_id, movie_cred, excluded_roles, normalize, role_frequency_for_crew):

    # iterate through each dictionary (either a movie dictionary or role dictionary) in movie_cred
    for role in movie_cred:       
        
        # skip if dictionary has no key 'role' 
        if( 'role' not in role ):
            continue
       
        if normalize: # check whether we want to normalize roles
            role=make_normalized_dict(role)
       
        if( role['role'] == 'Directed by') or (role['role'] in excluded_roles):
            continue # checks if the role is either 'Directed by' or if it is in the list of excluded roles
        
        crew_members_for_role=[] #list of (unique) crewmembers for a given role

        for c in role['crew']: # iterates through each crewmember with 'crew'
            crew_id = c['id'] # extract ID
            crew_name = c['name'] # extract name
            rl = role['role'] # extract role

            if crew_id==dir_id: # check if crewmember ID is the same as director ID
                continue

            #if there are duplicate crew members for a given role, skip
            if crew_id in crew_members_for_role:  
                continue

            crew_members_for_role.append(crew_id) # adds crew member's ID to list of crewmembers for the role
           
            G.add_edge(dir_id, crew_id) # add edge

            #update role_frequency_for_crew
            role_frequency_for_crew.setdefault(rl, {}) # if rl doesnt exist, set to empty
            role_frequency_for_crew[rl].setdefault( crew_id, 0 ) # if crew_id doesnt exist, set to empty
            role_frequency_for_crew[rl][crew_id] += 1 # increments count of crew_id for given role

            #set node attributes (name, type)
            typ = 'director' if G.nodes[crew_id].get('type', '') == 'director' else 'crew' # check if node has 'type' == director
            node_attributes = {'name': crew_name, 'type': typ} # create dictionary containing names and type
            nx.set_node_attributes(G, {crew_id: node_attributes}) # set attributes



def get_mov_credit_frm_file(movie_cred_file):

    movie_credits = [] # empty list to store credits
    with open(movie_cred_file, 'r') as infile: # open file
        for cred in infile: # iterate over files
            cred = json.loads(cred) # parse through json files
            movie_credits.append(cred) # appends parsed object to list

    return movie_credits # return list containing parsed movie credits

def get_role_frequency_among_movies(dir_id, excluded_roles, normalize):
    dataset = './director_crew_info' # path to dataset
    role_frequency={}    # initialize empty dictionary to store role frequency
    credits_file = f'{dataset}/{dir_id}/feature_films/' # path to directory containing 'dir_id'
    movie_credits = os.listdir(credits_file) # obtain list of fiilenames
    for movie_cred in movie_credits: # iterates over each movie
        movie_cred = f'{credits_file}{movie_cred}' # creates full path to movie file
        movie_cred = get_mov_credit_frm_file(movie_cred) # retrieve movie credits 
        for role in movie_cred: # iterate over each role
            if( 'role' not in role): # check to see if 'role' exists
                continue
            if normalize: # check to see if normalize is True
                role=make_normalized_dict(role)
            if( role['role'] == 'Directed by') or (role['role'] in excluded_roles):
                continue # checks if the role is either equal to 'Directed by' or if it is in the excluded_roles list.
            if role['role'] in role_frequency.keys():
                role_frequency[role['role']]+=1 # This line updates the role_frequency dictionary by incrementing the frequency count for the current role.
            else: # If the role is not already a key in role_frequency, it is added to the dictionary with a frequency count of 1.
                role_frequency[role['role']]=1
    return role_frequency # return frequency counts of roles among movies

def generate_dir_crew_network(excluded_roles, normalize):
    counter = 0
    dataset = './director_crew_info' # set path
    dir_folders = os.listdir(dataset) #obtain list of directory names 
    G=nx.DiGraph() # create graph 

    for dir_id in dir_folders: 
        if( dir_id.startswith('.') ): # if hidden file, continue
            continue
        director_file = f'{dataset}/{dir_id}/{dir_id}.json' # path to director file
        credits_file = f'{dataset}/{dir_id}/feature_films/' # path to movie credits directory
        movie_credits = os.listdir(credits_file)
        #print(len(movie_credits))
        role_frequency_among_movies=get_role_frequency_among_movies(dir_id, excluded_roles, normalize) # obtain frequency of roles
        role_frequency_for_crew={} # initialize to store frequencies of roles
        for movie_cred in movie_credits:
            
            movie_cred = f'{credits_file}{movie_cred}'  # appended to the credits_file path to create the full path to the movie credits file.
            movie_cred = get_mov_credit_frm_file(movie_cred) # retrieve the movie credits from the file.
            
            update_networkx(G, dir_id, movie_cred, excluded_roles, normalize, role_frequency_for_crew) # update graph with all the information

        assign_weights_to_crew(role_frequency_for_crew, role_frequency_among_movies, dir_id, G) # assign weights 
        set_dir_attr(G, dir_id, director_file) # set attributes for director
        counter += 1
        print(counter)
        print(dir_id)

 
    print('writing graph to file - start')
    #nx.write_gexf(G, "EDGES_FINAL.gexf") #uncomment this code to write a gephi file
    print('writing graph to file - end')           
            

def normalize_role(role):
    if role=="Casting By" or role=="Casting Department": # checks if the role parameter is equal to either "Casting By" or "Casting Department"
        return role # return them
    elif role.startswith("Cast"): # checks if 'role' parameter starts with 'Cast'
        return "Cast" # return cast
    elif role.startswith("Writing Credits"): # checks if 'role' parameter starts with 'Writing Credits'
        return "Writing Credits" # return writing credits
    else:
        return role # nonnormaliized role

def make_normalized_dict(role_dict):
    role=role_dict["role"] #  retrieves the value associated with the key "role" from the role_dict dictionary and assigns it to the role variable
    if (role != "Cast" and role.startswith('Cast')) or (role != "Writing Credits" and role.startswith('Writing Credits')): # if not these roles, need to be normalized
        normalized_role=normalize_role(role) # normalize role
        role_dict["role"]=normalized_role # assign back to role
    return role_dict

def get_roles_from_movie_list(movie_cred):
    roles=set() # initialize empty set to store unique roles
    for x in movie_cred: # iterate over each element
        if "role" not in x.keys(): # if doesn't have 'role' key, continue
            continue
        roles.add(x["role"]) # add value associated 'role' keey
    return roles


def get_all_possible_roles():
    roles_all_movies=set() # set empty set to store all possible roles
    dataset = './director_crew_info' # specify dataset directory
    dir_folders = os.listdir(dataset) # obtain all director folders
    for dir_id in dir_folders: # iterates over director folders
        credits_file = f'{dataset}/{dir_id}/feature_films/' # construct path
        movie_credits = os.listdir(credits_file)
        #iterate through each movie for a director
        for movie_cred in movie_credits:
            movie_cred = f'{credits_file}{movie_cred}'
            movie_cred =  get_mov_credit_frm_file(movie_cred)
            roles_one_movie=get_roles_from_movie_list(movie_cred) # obtain roles for current movie
            roles_all_movies.update(roles_one_movie) # adds roles for current movie
    return sorted(roles_all_movies)

def calculate(G, min_num_times):
    times_worked=0
    for node, data in G.nodes(data=True):
        if data['type'] == 'director':
            #print(node)
            out_degree=G.out_degree(node) 
            for neighbor, edge_data in G[node].items():
                weight_numerator=edge_data['weight_numerator']
                if weight_numerator>=min_num_times: # if number of times worked > num times we want (2)
                    times_worked+=1
            percentage = times_worked/out_degree # calculate weights
            print('Director', node,'worked with',min_num_times,'or more crewmembers for', percentage,'% of the time')
            #print(percentage)

def main(excluded_roles, normalize):
    generate_dir_crew_network(excluded_roles, normalize)

if __name__ == '__main__':
    # define command line arguments
    parser=argparse.ArgumentParser()
    parser.add_argument("-er", "--excluded_roles", help="list of roles to exclude from the graph", type=str) # list of roles to exclued
    parser.add_argument("-n", "--normalize", help="normalize the roles that are variants of Cast and Writing Credits", action="store_true") # indicate whether to normalize or not

    args=parser.parse_args() # parses command line argumnet
    excluded_roles=[] # list of excluded roles
    if args.excluded_roles: # check if 'excluded_roles' argument was provided
        excluded_roles=args.excluded_roles.split(', ') # splits CSV values assigning them to excluded_roles
    main(excluded_roles, args.normalize) # calls main function 
    G=nx.read_gexf("EDGES_FINAL.gexf")
    calculate(G, 2)
    



