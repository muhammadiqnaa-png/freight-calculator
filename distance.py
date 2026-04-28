import os
import json


DATA_FILE = "distance_data.json"

def find_distance(pol, pod):
    data = load_distances()

    pol = (pol or "").strip().upper()
    pod = (pod or "").strip().upper()

    for route, distance in data.items():
        try:
            p, d = route.split(" - ")

            p = p.strip().upper()
            d = d.strip().upper()

            # ✅ normal match
            if p == pol and d == pod:
                return distance

            # 🔥 reverse match (INI KUNCI FIX LU)
            if p == pod and d == pol:
                return distance

        except:
            continue

    return 0

def load_distances():
    if not os.path.exists(DATA_FILE):
        return {}

    with open(DATA_FILE, "r") as f:
        return json.load(f)


def save_distances(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)

def get_all_ports():
    data = load_distances()
    ports = set()

    for route in data.keys():
        try:
            pol, pod = route.split(" - ")
            ports.add(pol.upper())
            ports.add(pod.upper())
        except:
            continue

    return sorted(list(ports))
