# =================================  GEOMETRY FUNCTIONS ========================================================


# Returns new geometry string in format POINTZ (49.3308 69.5647 1176) i.e. POINTZ (longitude, latitude, altitude)
# Or returns new string in format POINT (49.3308 69.5647) i.e. POINT (longitude, latitude)
# Input strings must starts with 'latlon' and have two or three values in between parentheses.
# Acceptable input formats:
# latlon (69.5647, 49.3308, 1176)
# latlon (69.5647, 49.3308)
def get_gcnet_geometry(position_string):
    latlon_string = get_string_in_parentheses(position_string)
    latlon_list = convert_string_to_list(latlon_string)

    # Switch latitude and longitude from source data
    longlat_list = switch_two_elements(latlon_list, 0, 1)
    longlat_string = convert_list_to_string(longlat_list)
    position_longlat = replace_substring(position_string, latlon_string, longlat_string)

    if len(latlon_list) == 3:
        point_geometry = replace_substring(position_longlat, "latlon", "POINTZ")
        geometry_no_commas = replace_substring(point_geometry, ",", "")
        return geometry_no_commas
    elif len(latlon_list) == 2:
        point_geometry = replace_substring(position_longlat, "latlon", "POINT")
        geometry_no_commas = replace_substring(point_geometry, ",", "")
        return geometry_no_commas
    else:
        print(
            f'WARNING (geometry.py): "{position_string}" must have two or three items in between parentheses'
        )
        return


# Returns list of strings to string with space
def convert_list_to_string(input_list, separator=" "):
    return separator.join(input_list)


# Switch two elements of list by index
def switch_two_elements(input_list, a, b):
    input_list[a], input_list[b] = input_list[b], input_list[a]
    return input_list


# Returns string in between parentheses
# Example inputting 'latlon (69.5647, 49.3308, 1176)' outputs '69.5647, 49.3308, 1176'
def get_string_in_parentheses(input_string):
    start = input_string.find("(") + len("(")
    end = input_string.find(")")
    substring = input_string[start:end]
    return substring


# Returns comma delimited string as list
def convert_string_to_list(string):
    new_list = [item.strip() for item in string.split(",")]
    return new_list


# Replace substring in a string and return modified string, 'old' is substring to replace with 'new'
def replace_substring(string, old, new):
    return string.replace(old, new)
