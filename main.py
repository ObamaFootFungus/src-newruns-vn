import requests
import pickle


# Get recently verified runs
def get_runs():
    runs = requests.get("https://www.speedrun.com/api/v1/runs?game=pd0qj2w1&status=verified&orderby=verify-date&direction=desc&max=25")
    return (runs.json())["data"]

# Get name of category by id
def get_category_name(id):
    category = requests.get("https://www.speedrun.com/api/v1/categories/" + id)
    return (category.json())["data"]["name"]

# Get names of players from array of player objects
def get_player_names(playerArray):
    names = []
    for player in playerArray:
        name = requests.get(player["uri"])
        names.append((name.json())["data"]["names"]["international"])
    return ' - '.join(names)

# Get the names of variable values
def get_value_labels(valueArray):
    labels = []
    for value in valueArray:
        variable = requests.get("https://www.speedrun.com/api/v1/variables/" + value)
        variable = (variable.json())["data"]["values"]["values"]
        labels.append(variable[(valueArray[value])]["label"])
    return ' - '.join(labels)

# Sort out previously used runs
def check_for_old_runs(runArray):
    filtered = []
    oldRuns = pickle.load(open('runs.data', 'rb'))
    for run in runArray:
        if (run["id"] not in oldRuns):
            filtered.append(run)
            oldRuns.append(run["id"])
    fw = open('runs.data', 'wb')
    pickle.dump(oldRuns, fw)
    fw.close()
    return filtered

# Formats values into api acceptable options
def format_values_for_request(values):
    formatted = []
    for key in values:
        formatted.append("var-" + key + "=" + values[key])
    return '&'.join(formatted)

# Get place of run of leaderboard
def get_place_on_leaderboard(run):
    formattedValues = format_values_for_request(run["values"])
    leaderboard = requests.get("https://www.speedrun.com/api/v1/leaderboards/" + run["game"] + "/category/" + run["category"] + "?" + formattedValues)
    leaderboard = leaderboard.json()
    rank = None
    for r in leaderboard["data"]["runs"]:
        if r["run"]["id"] == run["id"]:
            rank = r["place"]
    return rank

# Converts times in the format XXX.xxx into h m s ms
def format_time(time):
    ms = int(time * 1000)
    s, ms = divmod(ms, 1000)
    m, s = divmod(s, 60)
    h, m = divmod(m, 60)
    ms = "{:03d}".format(ms)
    s = "{:02d}".format(s)
    if h > 0:
        m = "{:02d}".format(m)
    return (
        ((h > 0) * (str(h) + "h "))
        + str(m)
        + "m "
        + str(s)
        + "s "
        + ((str(ms) + "ms") * (ms != "000"))
    )

# Formats runs for use
def format_data(run):
    return {
        "header": "Voxyl Network - " +  get_category_name(run["category"]) + " - " + get_value_labels(run["values"]),
        "link": run["weblink"],
        "time": format_time(run["times"]["realtime_t"]),
        "players": get_player_names(run["players"]),
        "rank": get_place_on_leaderboard(run),
        "verify-date": run["status"]["verify-date"]

    }

# Returns array of runs for use
def main():
    final = []
    runs = check_for_old_runs(get_runs())
    for r in runs:
        final.append(format_data(r))
    return final or "No new runs"

print(main())