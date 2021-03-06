# This file contains the code necessary for fetching various stats.
# IE: General stats, ff-stats, map stats, etc.
import json
import requests
import urllib.request

import d_maps
from d_weapons import dh_weps


# This function displays general stats to the user (kills, deaths, kdr, etc.)
def userStats(user_dict, user_id):
    user_roid = user_dict[user_id]

    stats_url = "http://api.darklightgames.com/players/" + user_roid + "/?format=json"

    # Opens a user's page on the stats website and grabs their stats (kills, deaths, etc)
    stats_data = urllib.request.urlopen(stats_url)
    stats_contents = stats_data.read()
    load_stats = json.loads(stats_contents)

    weapon_url =  "http://46.101.44.19/players/damage_type_kills/?format=json&killer_id=" + user_roid + \
                    "&limit=10&offset=0"
    
    # Opens a user's weapon data file and loads it's contents
    weapon_data = urllib.request.urlopen(weapon_url)
    weapon_contents = weapon_data.read()
    weapon_list = str(weapon_contents).split("{")

    # Getting a user's favorite weapon and kill count with said weapon
    top_weapon = weapon_list[2]
    split_list = top_weapon.split(",")
    trimmed_list = [element.strip("}") for element in split_list]
    del trimmed_list[-1]

    stat_dict = {}

    for element in trimmed_list:
        (key, val) = element.split(":")
        stat_dict[key] = val

    # Reads a user's top damage type and associates it with a weapon name
    dam_type = stat_dict['"damage_type_id"']
    ref_weapon = dh_weps[dam_type]

    fav_weapon = "**Favorite Weapon:** " + ref_weapon + " at " + \
                stat_dict['"kills"'] + " kills"
    
    # Constructing the user's stats for display in Discord
    s_kills =  str(load_stats["kills"])
    deaths =  str(load_stats["deaths"])
    raw_kdr = str(load_stats["kills"] / load_stats["deaths"])
    kdr =  str(raw_kdr[0:4])

    # Move decimal-points over 2 places for TK-ratio.
    raw_tk_ratio = int(load_stats["ff_kills"]) / int(load_stats["kills"])
    tk_ratio = raw_tk_ratio * 10 * 10

    ff_kills =  str(load_stats["ff_kills"])
    ff_deaths =  str(load_stats["ff_deaths"])
    formatted_tk_ratio = "{:.2f}".format(tk_ratio) + "%"

    components = [s_kills, deaths, kdr, fav_weapon, ff_kills, ff_deaths, formatted_tk_ratio]

    return components


# This function fetches the stats for the map and gamemode the user has selected.
def mapStats(mode_selection):
    # Open the selected map's data and parse it.
    map_url = "http://46.101.44.19/maps/" + mode_selection + "/summary/"
    map_data = urllib.request.urlopen(map_url)
    map_data_contents = map_data.read()
    load_map_data = json.loads(map_data_contents)

    # Define json objects for easier use.
    axis_w = int(load_map_data["axis_wins"])
    axis_d = int(load_map_data["axis_deaths"])
    allied_w = int(load_map_data["allied_wins"])
    allied_d = int(load_map_data["allied_deaths"])

    axis_deaths = "**Axis Deaths:** " + str(axis_d) + " "
    allied_deaths = "| **Allied Deaths:** " + str(allied_d)
    axis_wins = "| **Axis Wins:** " + str(axis_w) + "  "
    allied_wins = "  **Allied Wins:** " + str(allied_w) + " "

    number_line = ["«", "-", "-", "-", "-",
                "-", "-", "-", "-", "-",
                "-", "-", "-", "-", "-",
                "-", "-", "-", "-", "-",
                "»"]

    total_games = axis_w + allied_w

    # Compare the map's axis vs allied wins.
    # Draw a small line-infographic weighted towards the larger winrate.
    if axis_w > allied_w:
        rough_percentage = axis_w / total_games
        win_percentage = round(rough_percentage, 2)

        marker_shift = 20 * win_percentage

        marker_position = 20 - marker_shift

        number_line.insert(int(marker_position), "o")
    elif axis_w < allied_w:
        rough_percentage = allied_w / total_games
        win_percentage = round(rough_percentage, 2)

        marker_shift = 20 * win_percentage

        number_line.insert(int(marker_shift), "o")
    elif axis_w == allied_w:
        number_line.insert(10, "o")
    
    win_infographic = ''.join(number_line)

    composed_map_message = axis_deaths + axis_wins + win_infographic + allied_wins + allied_deaths

    return composed_map_message


# This function checks if a user's searched map is in the bot's database.
# They are prompted to select which game mode and map stats are then fetched.
def mapSearch(user_string):
    split_string = user_string.split()
    del split_string[0:2]
    seperator = " "
    split_string = seperator.join(split_string)
    split_string = split_string.title()

    selected_map = split_string

    map_dict_1 = d_maps.adv_dict
    map_dict_2 = d_maps.push_dict
    map_dict_3 = d_maps.clash_dict
    map_dict_4 = d_maps.arm_dict
    map_dict_5 = d_maps.def_dict
    map_dict_6 = d_maps.stalemate_dict

    if any(selected_map in item for item in [map_dict_1, map_dict_2, map_dict_3, map_dict_4, map_dict_5, map_dict_6]):
        adv_string = None
        push_string = None
        clash_string = None
        arm_string = None
        def_string = None
        stalemate_string = None

        adv_flag = 0
        push_flag = 0
        clash_flag = 0
        arm_flag = 0
        def_flag = 0
        stalemate_flag = 0

        # Check each dict for the map name, set it's flag to 1 if it is found.
        if selected_map in map_dict_1:
            adv_string = map_dict_1[selected_map]
            adv_flag += 1
        if selected_map in map_dict_2:
            push_string = map_dict_2[selected_map]
            push_flag += 1
        if selected_map in map_dict_3:
            clash_string = map_dict_3[selected_map]
            clash_flag += 1
        if selected_map in map_dict_4:
            arm_string = map_dict_4[selected_map]
            arm_flag += 1
        if selected_map in map_dict_5:
            def_string = map_dict_5[selected_map]
            def_flag += 1
        if selected_map in map_dict_6:
            stalemate_string = map_dict_6[selected_map]
            stalemate_flag += 1
        
        choice_list = []
        options_msg = ""
        map_list = []
        response_flag = 0

        if adv_flag == 1:
            choice_list.append("Advance | ")
            map_list.append(adv_string)
        if push_flag == 1:
            choice_list.append("Push | ")
            map_list.append(push_string)
        if clash_flag == 1:
            choice_list.append("Clash | ")
            map_list.append(clash_string)
        if arm_flag == 1:
            choice_list.append("Armored | ")
            map_list.append(arm_string)
        if def_flag == 1:
            choice_list.append("Defense | ")
            map_list.append(def_string)
        if stalemate_flag == 1:
            choice_list.append("Stalemate | ")
            map_list.append(stalemate_string)

        idx = 0

        for idx, element in enumerate(choice_list):
            previous_element = element

            element = str(idx + 1) + " " + previous_element

            options_msg = options_msg + element

            idx += 1
        
        options_msg = options_msg[:-2]
        
        return options_msg, selected_map, map_list, response_flag
  
    else:
        msg = " That map does not exist or you may have typed it wrong, try again!"
        map_list = None
        response_flag = 1

        return msg, selected_map, map_list, response_flag
