import requests
import pickle
import time
from datetime import datetime

# Information for the discord webhook
webookID = "" # Ex: 1028011492051800084
webhookToken = "" # Ex: MEpvTZE9WXkSFJP1PvhzhmMLWfo7jIqLpn6K0HWNXH88mxOhDT01Hcd4upZ0ttChpmsl

# How often the script should run in seconds
interval = 300

# Get recently verified runs
def get_runs():
    runs = requests.get("https://www.speedrun.com/api/v1/runs?game=pd0qj2w1&status=verified&orderby=verify-date&direction=desc&max=25&embed=category,players")
    return (runs.json())["data"]

# Get names of players from array of player objects
def get_player_names(playerArray):
    names = []
    for player in playerArray:
        names.append(player["names"]["international"])
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
    dataF = open('runs.data', 'rb')
    oldRuns = pickle.load(dataF)
    dataF.close()
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
    leaderboard = requests.get("https://www.speedrun.com/api/v1/leaderboards/" + run["game"] + "/category/" + run["category"]["data"]["id"] + "?" + formattedValues)
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
    place = get_place_on_leaderboard(run)
    if place is None:
        return None
    if place > 3:
        return None
    if place == 1:
        color = 16766720
    elif place == 2:
        color = 12632256
    else:
        color = 13467442
    return {
        "header": "Voxyl Network - " +  run["category"]["data"]["name"] + " - " + get_value_labels(run["values"]),
        "link": run["weblink"],
        "time": format_time(run["times"]["realtime_t"]),
        "players": get_player_names(run["players"]["data"]),
        "rank": place,
        "verify-date": run["status"]["verify-date"],
        "color": color

    }

# Sends run message to discord webhook
def send_to_webhook(run):
    if run is None:
        return
    webhookData = {
        "username": "Mr. Thomas",
        "avatar_url": "https://cdn.discordapp.com/avatars/819816951982981140/641e6e316c5b3c662a28ae049ecd754c.png?size=4096",
        "embeds": [{
            "title": run["time"] + " by " + run["players"],
            "type": "rich",
            "url": run["link"],
            "timestamp": datetime.now().isoformat(),
            "color": run["color"],
            "author": {
                "name": run["header"]
            },
            "fields": [{
                "name": "Leaderboard Rank",
                "value": run["rank"]
            },
            {
                "name": "Verified at",
                "value": "`" + run["verify-date"] + "`"
            }],
            "thumbnail": {
                "url": "https://www.speedrun.com/gameasset/pd0qj2w1/cover?v=7430ead"
            }
        }]
    }
    requests.post("https://discord.com/api/v10/webhooks/" + webookID + "/" + webhookToken, json = webhookData)


# Main func
def main():
    runs = check_for_old_runs(get_runs())
    for r in reversed(runs):
        time.sleep(2)
        send_to_webhook(format_data(r))
    time.sleep(interval)
    main()

main()