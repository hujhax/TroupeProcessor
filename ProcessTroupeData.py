"""Process Troupe Data

This takes in an ODS file of troupe applications to the Hideout Theatre,
collates them into a single dictionary of troupes->troupe data, and then
converts that to a set of files for the AIC Wiki.

Command line usage:
$ python ProcessTroupeData.py filename
"""


def load_troupe_info(filename):
    from ODSReader import ODSReader
    doc = ODSReader(filename)
    troupeDatabase = doc.getSheet("avail")
    return troupeDatabase


def is_url(string):
    return 'www' in string or 'http' in string


def set_first_valid_url(data, field_name, new_string):
    if not field_name in data and is_url(new_string):
        data[field_name] = new_string


def set_longest_string(data, field_name, new_string):
    if not new_string:
        return
    if field_name in data and len(data[field_name]) > len(new_string):
        return
    data[field_name] = new_string


def process_row(troupe_dict, row):
    if row[1] in troupe_dict:
        data = troupe_dict[row[1]]
    else:
        data = {}

    set_first_valid_url(data, 'site', row[2])
    set_first_valid_url(data, 'photo', row[19])
    set_first_valid_url(data, 'video', row[20])

    set_longest_string(data, 'blurb', row[7])
    set_longest_string(data, 'deal', row[13])

    if not 'cast' in data:
        data['cast'] = row[4]

    return data


def process_troupe_data(filename):
    table = load_troupe_info(filename)[1:]  # remove headers
    troupe_dict = {}
    for row in table:
        if row[1]:
            troupe_dict[row[1]] = process_row(troupe_dict, row)
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
