import imdb_scraper as imdb_scr
import util as util
import argparse
import json
import os

# get the director/crew id or movie id 
# uri: the imdb uri
def get_id(uri):
    return uri.split("/")[4]


# return a list of films (and their relevant information)
# exclude_non_feature_films: True will exclude the non-feature-films (non-films or films that are less than 70 min long) from the list of films. False will
                            # will keep all the works of the director
def get_list_of_films_for_director(director_id, exclude_non_feature_films):
    # dir_dict structure:
    # {director_name: str, credits:[{title:str, uri:str, year:str, note:str}, ... ]}

    '''dir_dict example with director id nm2125482:
    {'director_name': 'ChloΘ Zhao', 'imdb_uri': 'https://www.imdb.com/name/nm2125482/fullcredits/', 
    'credits': [{'title': 'Hamnet', 'uri': 'https://www.imdb.com/title/tt14905854/?ref_=nm_flmg_dr_1', 'year': '', 'note': '(pre-production)'}, 
                {'title': "A Clydesdale's Journey", 'uri': 'https://www.imdb.com/title/tt24349856/?ref_=nm_flmg_dr_2', 'year': '2022', 'note': '(Short)'}, 
                {'title': 'Eternals', 'uri': 'https://www.imdb.com/title/tt9032400/?ref_=nm_flmg_dr_3', 'year': '2021', 'note': ''}, 
                {'title': 'Nomadland', 'uri': 'https://www.imdb.com/title/tt9770150/?ref_=nm_flmg_dr_4', 'year': '2020', 'note': '(directed by)'}, 
                {'title': 'The Rider', 'uri': 'https://www.imdb.com/title/tt6217608/?ref_=nm_flmg_dr_5', 'year': '2017', 'note': ''}, 
                {'title': 'Songs My Brothers Taught Me', 'uri': 'https://www.imdb.com/title/tt3566788/?ref_=nm_flmg_dr_6', 'year': '2015', 'note': ''}, 
                {'title': 'Benachin', 'uri': 'https://www.imdb.com/title/tt1630305/?ref_=nm_flmg_dr_7', 'year': '2011', 'note': '(Short)'}, 
                {'title': 'Daughters', 'uri': 'https://www.imdb.com/title/tt1517671/?ref_=nm_flmg_dr_8', 'year': '2010', 'note': '(Short)'}, 
                {'title': 'The Atlas Mountains', 'uri': 'https://www.imdb.com/title/tt1362356/?ref_=nm_flmg_dr_9', 'year': '2009', 'note': '(Short)'}, 
                {'title': 'Post', 'uri': 'https://www.imdb.com/title/tt1522245/?ref_=nm_flmg_dr_10', 'year': '2008', 'note': '(Short)'}]}'''

    dir_dict=imdb_scr.get_full_credits_for_director(director_id)
    movie_info_from_scrape=dir_dict["credits"]
    movie_info_list=[] #list of movie_info dictionaries

    # iterate through the movies and create a movie info dictionary for each movie
    for movie in movie_info_from_scrape:
        movie_info={} # {title: str, year: str, movie id: str}
        movie_id=get_id(movie["uri"])
        if exclude_non_feature_films:
            if not imdb_scr.is_feature_film(movie_id):
                continue
        movie_info["title"]=movie["title"]
        movie_info["year"]=movie["year"]
        movie_info["movie id"]=movie_id
        movie_info_list.append(movie_info)
    return movie_info_list


# get the crewmembers for a movie
# movie_id: the movie_id (from the imdb uri) of the movie 
def get_movie_crew(movie_id):
    ret_arr=[]
    #full_dict_from_scrape structure:
    # {title_uri: str, title: str, full_credits: [{role: str, crew: [{name: str, link: str, credit: str}]}, ]}
    ''' full_dict_from_scrape example with movie id tt9032400:
    {'title_uri': 'https://www.imdb.com/title/tt9032400/fullcredits/', 'title': 'Eternals (2021)', 
     'full_credits': [{'role': 'Directed by', 'crew': [{'name': 'ChloΘ Zhao', 'link': 'https://www.imdb.com/name/nm2125482/?ref_=ttfc_fc_dr1'}]}, 
                      {'role': 'Writing Credits', 'crew': [{'name': 'ChloΘ Zhao', 'link': 'https://www.imdb.com/name/nm2125482/?ref_=ttfc_fc_wr1', 'credit': '(screenplay by) and'}, 
                                                           {'name': 'Patrick Burleigh', 'link': 'https://www.imdb.com/name/nm1522597/?ref_=ttfc_fc_wr2', 'credit': '(screenplay by) and'}, 
                                                           {'name': 'Ryan Firpo', 'link': 'https://www.imdb.com/name/nm2535716/?ref_=ttfc_fc_wr3', 'credit': '(screenplay by) &'}, 
                                                           {'name': 'Kaz Firpo', 'link': 'https://www.imdb.com/name/nm3303922/?ref_=ttfc_fc_wr4', 'credit': '(screenplay by)'}, 
                                                           {'name': 'Ryan Firpo', 'link': 'https://www.imdb.com/name/nm2535716/?ref_=ttfc_fc_wr5', 'credit': '(screen story by) &'}, 
                                                           {'name': 'Kaz Firpo', 'link': 'https://www.imdb.com/name/nm3303922/?ref_=ttfc_fc_wr6', 'credit': '(screen story by)'}, 
                                                           {'name': 'Jack Kirby', 'link': 'https://www.imdb.com/name/nm0456158/?ref_=ttfc_fc_wr7', 'credit': '(based on the Marvel comics by)'}]}, 
                    {'role': 'Cast (in credits order) verified as complete', 'crew': []}, 
                    {'role': 'Produced by', 'crew': [{'name': 'Victoria Alonso', 'link': 'https://www.imdb.com/name/nm0022285/?ref_=ttfc_fc_cr2', 'credit': 'executive producer'}, 
                                                     {'name': 'Mitchell Bell', 'link': 'https://www.imdb.com/name/nm0068416/?ref_=ttfc_fc_cr3', 'credit': 'co-producer (as Mitch Bell)'}, 
                                                     {'name': "Louis D'Esposito", 'link': 'https://www.imdb.com/name/nm0195669/?ref_=ttfc_fc_cr4', 'credit': 'executive producer'}, 
                                                     {'name': 'Kevin de la Noy', 'link': 'https://www.imdb.com/name/nm0209326/?ref_=ttfc_fc_cr5', 'credit': 'executive producer'}, 
                                                     {'name': 'Kevin Feige', 'link': 'https://www.imdb.com/name/nm0270559/?ref_=ttfc_fc_cr6', 'credit': 'producer (produced by) (p.g.a.)'}, 
                                                     {'name': 'Nate Moore', 'link': 'https://www.imdb.com/name/nm5478123/?ref_=ttfc_fc_cr7', 'credit': 'producer (produced by) (p.g.a.)'}, 
                                                     {'name': 'Juan Cano Nono', 'link': 'https://www.imdb.com/name/nm6001744/?ref_=ttfc_fc_cr8', 'credit': 'producer: Sur Film, Canary Islands (as Juan Antonio Cano)'}, 
                                                     {'name': 'Helen Pollak', 'link': 'https://www.imdb.com/name/nm0689426/?ref_=ttfc_fc_cr9', 'credit': 'line producer: additional photography unit'}, ...'''
                                                     
    full_dict_from_scrape=imdb_scr.get_full_crew_for_movie(movie_id)
    for role_category in full_dict_from_scrape["full_credits"]:
        role_crew_dict={} # {role: str, crew: {name: str, id: str}}
        role_crew_dict["role"]=role_category["role"]
        role_crew_dict["crew"]=[]
        for crew_member in role_category["crew"]:
            crew_info={} # {name: str, id: str}
            crew_info["name"]=crew_member["name"]
            crew_info["id"]=get_id(crew_member["link"])
            role_crew_dict["crew"].append(crew_info)
        ret_arr.append(role_crew_dict)
    return ret_arr


# write the crew data of one movie to a jsonl file
# movie info: dictionary that includes information about a movie's title, year, and movie id
# movie_crew_arr: array of dictionaries that each correspond to a specific role {role: str, crew: [{name: str, id: str}, {name: str, id: str}, ... ]}
def write_crew_data_to_movie_file(movie_info, movie_crew_arr, filename):
    with open(filename, "w") as outfile:
        movie_info_str=json.dumps(movie_info)
        outfile.write(movie_info_str + "\n")

        for i in range(len(movie_crew_arr)):
            dictionary=json.dumps(movie_crew_arr[i])
            outfile.write(dictionary +"\n")
    return


# put the direction information from the csv into a dictionary
def make_director_info_dict(info, categories):
    director_info={}
    director_info_list=info.split(",")
    director_info["Last Name"]=director_info_list[0]
    director_info["First Name"]=director_info_list[1]
    director_info["Sex"]=director_info_list[2]
    director_info["Ethnicity"]=director_info_list[3]
    director_info["Labels"]=director_info_list[4]
    director_id=get_id(director_info_list[5])
    director_info["Director Id"]=director_id
    if len(categories)>6:
        for i in range(6, len(categories)):
            director_info[categories[i]]=director_info_list[i]
    return director_info


# creates the director_crew relationship dataset for ONE director
# filename: name of the file that includes information about the directors
# exclude_non_feature_film: True will exclude the non-feature-films (non-films or films that are less than 70 min long) from the list of films. False will
                            # will keep all the works of the director
def get_director_crew_relationship_for_one(director_id, filename, exclude_non_feature_films):
        director_categories=[] 
        with open(filename,"r", encoding = "utf-8") as data:  
            # create a folder named "director_crew_info" in the directory you're currently in
            util.create_folder(os.getcwd(), "director_crew_info")
            # go inside the newly created folder, "director_crew_info"
            path=os.getcwd()+"\\director_crew_info"
            os.chdir(path)

            # flag is True if the current director's id matches that of the passed in parameter
            flag=False
            counter=-1
            # iterate through all the directors
            for line in data:
                # split the column names and put them into an array
                if counter==-1:
                    director_categories = line.split(',')
                    counter += 1
                    continue

                # make a dictionary containing information about the director {Last Name: val, First Name: val, Sex: val, Ethnicity: val, Labels: val, Director Id: val, ...}
                director_info=make_director_info_dict(line, director_categories)
                if (director_id==director_info["Director Id"]):
                    print(line.replace("\n", ""))
                    # create a folder named with the director id
                    util.create_folder(path, director_id)
                    # go inside the director folder
                    os.chdir(path+"\\"+director_id)
                    # write the json file for the director information
                    util.write_json(director_id+".json", director_info)
                    # create a folder named "movies"
                    util.create_folder(os.getcwd(), "movies")
                    # go inside the folder, "movies"
                    os.chdir(os.getcwd()+"\\movies")
                    try:
                        # get a list of feature films or works that the director has directed
                        movie_info_list=get_list_of_films_for_director(director_id, exclude_non_feature_films)
                        print(len(movie_info_list),"films\n")
                        # iterate through each movie or work and create a jsonl file that contains information about the movie's crew
                        for movie in movie_info_list:
                            movie_id=movie["movie id"]
                            movie_crew_info=get_movie_crew(movie_id)
                            write_crew_data_to_movie_file(movie, movie_crew_info, movie_id+".jsonl")
                    except KeyError:
                        print("failed to get director-crew relationship for "+director_id)
                        return
                    flag=True
                # once the for loop has reached the desired director, there is no need to go through the rest of the directors, so return
                if flag:
                    return


# create the director crew dataset for multiple directors
# filename: name of the file that includes information about the directors
# exclude_non_feature_film: True will exclude the non-feature-films (non-films or films that are less than 70 min long) from the list of films. False will
                            # will keep all the works of the director
# increment: how many directors to get the dataset for at a time; pass in 0 if you would like to get the dataset for all the directors at once
def main(filename, exclude_non_feature_films, increment=0):
    director_categories=[]
    with open(filename,"r", encoding = "utf-8") as data:  
        # create a folder named "director_crew_info" in the directory you're currently in
        util.create_folder(os.getcwd(), "director_crew_info")
        # go inside the folder, "director_crew_info"
        path=os.getcwd()+"\\director_crew_info"
        os.chdir(path)

        counter=-1
        # iterate through all the directors
        for line in data:
            if counter==-1:
                director_categories = line.split(',')
                counter += 1
                continue

            print(line.replace("\n", ""))

            # make a dictionary containing information about the director {Last Name: val, First Name: val, Sex: val, Ethnicity: val, Labels: val, Director Id: val, ...}
            director_info=make_director_info_dict(line, director_categories)
            director_id=director_info["Director Id"]
            # create a folder named with the director id; if a folder for a director already exists, move on to the next director
            if util.create_folder(path, director_id):
                continue
            # go inside the director folder
            os.chdir(path+"\\"+director_id)
            # write the json file for the director information
            util.write_json(director_id+".json", director_info)
            # create a folder named "movies
            util.create_folder(os.getcwd(), "movies")
            # go inside the folder, "movies"
            os.chdir(os.getcwd()+"\\movies")
            try:
                # get a list of feature films or works that the director has directed
                movie_info_list=get_list_of_films_for_director(director_id, exclude_non_feature_films)
                print(len(movie_info_list),"films\n")
                # iterate through each movie or work and create a jsonl file that contains information about the movie's crew
                for movie in movie_info_list:
                    movie_id=movie["movie id"]
                    movie_crew_info=get_movie_crew(movie_id)
                    write_crew_data_to_movie_file(movie, movie_crew_info, movie_id+".jsonl")
            except KeyError:
                print("failed to get director-crew relationship for "+director_id+"\n")
                continue
            counter+=1
            if counter==increment:
                break
        # the final value assigned to counter should indicate for how many directors the data extraction successful for
        print(counter)


if __name__ == "__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("filename", help="the filename that contains information about all the directors", type=str)
    parser.add_argument("-enff", "--exclude_non_feature_films", help="exclude works that are not feature films (movies over 70 minutes long)", action="store_true")
    parser.add_argument("-d", "--director", help="pass in the director id (from imdb) to get the director-crew relationship data (for only ONE director)", type=str)
    parser.add_argument("-i", "--increment", help="the number of directors at a time you want to run the data extraction for", type=int)
    args=parser.parse_args()
    if args.director is None:
        if (args.increment is None):
            main(args.filename, args.exclude_non_feature_films)
        else:
            main(args.filename, args.exclude_non_feature_films, args.increment)
    else:
        get_director_crew_relationship_for_one(args.director, args.filename, args.exclude_non_feature_films)


  
