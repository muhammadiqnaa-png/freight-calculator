preset_params = {
    "270 ft": {
        "speed_laden": 3, "speed_ballast": 4,
        "consumption": 85, "price_fuel": 25000,
        "consumption_fw": 2, "price_fw": 120000,
        "charter": 0, "crew": 60000000, "insurance": 40000000,
        "docking": 40000000, "maintenance": 40000000,
        "certificate": 40000000, "premi_nm": 50000, "other_cost": 10000000,
        "port_cost_pol": 35000000, "port_cost_pod": 35000000, "asist_tug": 0,
        "port_stay_pol": 4, "port_stay_pod": 4
    },
    "300 ft": {
        "speed_laden": 3, "speed_ballast": 4,
        "consumption": 115, "price_fuel": 25000,
        "consumption_fw": 2, "price_fw": 120000,
        "charter": 0, "crew": 60000000, "insurance": 50000000,
        "docking": 50000000, "maintenance": 50000000,
        "certificate": 45000000, "premi_nm": 50000, "other_cost": 15000000,
        "port_cost_pol": 35000000, "port_cost_pod": 35000000, "asist_tug": 0,
        "port_stay_pol": 5, "port_stay_pod": 5
    },
    "330 ft": {
        "speed_laden": 3, "speed_ballast": 4,
        "consumption": 130, "price_fuel": 25000,
        "consumption_fw": 2, "price_fw": 120000,
        "charter": 0, "crew": 60000000, "insurance": 60000000,
        "docking": 60000000, "maintenance": 60000000,
        "certificate": 50000000, "premi_nm": 50000, "other_cost": 20000000,
        "port_cost_pol": 35000000, "port_cost_pod": 35000000, "asist_tug": 0,
        "port_stay_pol": 5, "port_stay_pod": 5
    },
    "Custom": {
        "speed_laden": 0, "speed_ballast": 0,
        "consumption": 0, "price_fuel": 0,
        "consumption_fw": 0, "price_fw": 0,
        "charter": 0, "crew": 0, "insurance": 0,
        "docking": 000, "maintenance": 0,
        "certificate": 0, "premi_nm": 0, "other_cost": 0,
        "port_cost_pol": 0, "port_cost_pod": 0, "asist_tug": 0,
        "port_stay_pol": 0, "port_stay_pod": 0
    }
}


cargo_qty_default = {
    "270 ft": {
        "Coal (MT)": 5500,
        "Nickel (MT)": 5500,
        "Bauxite (MT)": 5500,
        "Sand (M3)": 3500,
        "Split (M3)": 3500
    },
    "300 ft": {
        "Coal (MT)": 7500,
        "Nickel (MT)": 7500,
        "Bauxite (MT)": 7500,
        "Sand (M3)": 4700,
        "Split (M3)": 5000
    },
    "330 ft": {
        "Coal (MT)": 10500,
        "Nickel (MT)": 10500,
        "Bauxite (MT)": 10500,
        "Sand (M3)": 5500,
        "Split (M3)": 6300
    }
}

def get_default_cargo(barge, cargo_type):
    return float(cargo_qty_default.get(barge, {}).get(cargo_type, 0))
