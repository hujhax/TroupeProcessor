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
    return troupeDatabase[1:]  # remove headers


def is_url(string):
    return 'www' in string or 'http' in string


def set_first_valid_url(data, field_name, new_string):
    if not field_name in data and is_url(new_string):
        data[field_name] = new_string


def collect_valid_urls(data, field_name, new_string):
    if is_url(new_string):
        new_item_set = set([new_string])
        if field_name in data:
            data[field_name] = data[field_name] | new_item_set
        else:
            data[field_name] = new_item_set


def set_longest_string(data, field_name, new_string):
    if not new_string:
        return False
    if field_name in data and len(data[field_name]) > len(new_string):
        return False
    data[field_name] = new_string
    return True


def collate_cast(data, field_name, new_string):
    import re
    if not new_string:
        return
    # Handle AND
    new_string = re.sub(r'\sAND\s', ' & ', new_string, flags=re.IGNORECASE)
    new_cast_set = set(re.split('[&,\n]', new_string))  # set of split-up names
    new_cast_set = {name.strip() for name in new_cast_set}  # strip whitespace
    new_cast_set = {name for name in new_cast_set if name}  # kill empty

    if field_name in data:
        data[field_name] = data[field_name] | new_cast_set
    else:
        data[field_name] = new_cast_set


def set_start_year(data, field_name, new_string):
    if not new_string:
        return

    if not field_name in data or int(data[field_name]) > int(new_string):
        data[field_name] = new_string


def set_end_year(data, field_name, new_string):
    if not new_string:
        return

    if not field_name in data or int(data[field_name]) < int(new_string):
        data[field_name] = new_string


def set_yes_no_field(data, field_name, new_string):
    if not new_string:
        return
    if new_string.find('n') != -1:  # "no"
        return
    if new_string.find('m') != -1:  # "maybe"
        return
    if new_string.find('y') == -1:  # no "yes"
        return
    data[field_name] = 'y'


def process_row(troupe_dict, row):
    if row[1] in troupe_dict:
        data = troupe_dict[row[1]]
    else:
        data = {}

    set_first_valid_url(data, 'site', row[2])
    set_first_valid_url(data, 'photo', row[19])
    collect_valid_urls(data, 'video', row[20])

    if set_longest_string(data, 'blurb', row[7]):
        data['blurb_year'] = row[22]
    if set_longest_string(data, 'deal', row[13]):
        data['deal_year'] = row[22]

    collate_cast(data, 'cast', row[4])

    set_start_year(data, 'start_year', row[22])
    set_end_year(data, 'end_year', row[22])

    set_yes_no_field(data, 'performed_before', row[11])

    return data


def process_troupe_data(filename):
    table = load_troupe_info(filename)
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
