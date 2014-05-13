"""Process Troupe Data

This takes in an ODS file of troupe applications to the Hideout Theatre,
collates them into a single dictionary of troupes->troupe data, and then
converts that to a set of files for the AIC Wiki.

Command line usage:
$ python ProcessTroupeData.py filename
"""

from ODSReader import *

# open the ods file


def load_troupe_info(filename):
    doc = ODSReader(filename)
    troupeDatabase = doc.getSheet("avail")
    return troupeDatabase


def is_url(string):
    return 'www' in string or 'http' in string


def process_row(troupe_dict, row):
    if row[1] in troupe_dict:
        data = troupe_dict[row[1]]
    else:
        data = {}

    if not 'site' in data and is_url(row[2]):
        data['site'] = row[2]

    if not 'cast' in data:
        data['cast'] = row[4]

    if not 'blurb' in data:
        data['blurb'] = row[7]

    if not 'deal' in data:
        data['deal'] = row[13]

    if not 'photo' in data and is_url(row[19]):
        data['photo'] = row[19]

    if not 'video' in data and is_url(row[20]):
        data['video'] = row[20]

    return data


def process_troupe_data(filename):
    table = load_troupe_info(filename)[1:]  # remove headers
    troupe_dict = {}
    troupe_dict = {row[1]: process_row(troupe_dict, row)
                   for row in table if row[1]}
    return troupe_dict

if __name__ == '__main__':
    import sys
    if sys.argv[1:]:
        print process_troupe_data(sys.argv[1])
    else:
        print __doc__

# for each row of data
    # add the data to troupe_dict[troupe_name]
        # (we'll be creating an array of rows for each name)
# for each name in troupe_dict
    # set URL to the first URL field with www or http in the text
    # set "photo" to be the first photo field with www or http in the text
    # set "deal" to the longest deal string
    # set "blurb" to the longest blurb string
    # iterate through years
        # if minyear is blank or > year, minyear = year
        # if maxyear is blank or < year, maxyear = year
    # set cast to a null set
    # for each cast list
        # convert string to an array
        # add items to the set
    # add all videos to a set
    # output all of these data as a csv row
