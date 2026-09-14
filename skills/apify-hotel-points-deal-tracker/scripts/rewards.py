#!/usr/bin/env python3
"""Map a loyalty or rewards program to concrete search filters.

Neither the Google Hotels nor the Google Flights Actor filters by loyalty
program directly, so this helper turns a program name into filters the Actors
DO understand:

  Flights: a list of airline codes for the program's own airline plus its
           alliance partners, ready for the Actor's `airlines` input (CSV).
  Hotels:  a list of brand-name substrings for the program's chain family,
           used to keep or flag matching rows from a normal search (the Actor
           has no loyalty filter, so match on each property's `name`).

Honest limit: these Actors read public cash prices, not your loyalty account.
They surface which chain or alliance properties exist at what cash rate; they
do not show points or award pricing. Book award stays through your own program.

Usage:
  python3 rewards.py "Marriott Bonvoy"        # -> JSON with hotel brands
  python3 rewards.py "United MileagePlus"      # -> JSON with airline codes
  python3 rewards.py --list                    # list known programs
"""

import json
import sys

# Airline alliance member codes (IATA). Not exhaustive; the common carriers.
STAR_ALLIANCE = ["UA", "AC", "LH", "NH", "SQ", "TK", "LX", "OS", "SN", "TP",
                 "SK", "OZ", "TG", "CA", "ZH", "SA", "ET", "AV", "CM", "NZ",
                 "MS", "BR", "AI", "LO", "A3", "JP"]
ONEWORLD = ["AA", "BA", "QF", "CX", "JL", "IB", "AY", "QR", "MH", "RJ",
            "UL", "AT", "AS", "WY", "S7", "FJ"]
SKYTEAM = ["DL", "AF", "KL", "KE", "AZ", "SU", "MU", "CZ", "CI", "GA",
           "SV", "ME", "KQ", "AR", "AM", "RO", "VN", "OK", "UX", "VS"]

# Program -> filter definition. `aliases` are lowercase substrings for matching.
PROGRAMS = {
    # Airline programs (kind: air)
    "United MileagePlus": {"kind": "air", "airlines": STAR_ALLIANCE,
                           "aliases": ["united", "mileageplus", "mileage plus"]},
    "Air Canada Aeroplan": {"kind": "air", "airlines": STAR_ALLIANCE,
                            "aliases": ["aeroplan", "air canada"]},
    "Lufthansa Miles & More": {"kind": "air", "airlines": STAR_ALLIANCE,
                               "aliases": ["miles & more", "miles and more", "lufthansa"]},
    "American AAdvantage": {"kind": "air", "airlines": ONEWORLD,
                            "aliases": ["american", "aadvantage", "aa "]},
    "British Airways Executive Club": {"kind": "air", "airlines": ONEWORLD,
                                       "aliases": ["british airways", "executive club", "avios"]},
    "Alaska Mileage Plan": {"kind": "air", "airlines": ONEWORLD,
                            "aliases": ["alaska", "mileage plan"]},
    "Delta SkyMiles": {"kind": "air", "airlines": SKYTEAM,
                       "aliases": ["delta", "skymiles"]},
    "Air France-KLM Flying Blue": {"kind": "air", "airlines": SKYTEAM,
                                   "aliases": ["flying blue", "air france", "klm"]},
    "Southwest Rapid Rewards": {"kind": "air", "airlines": ["WN"],
                                "aliases": ["southwest", "rapid rewards"]},
    "JetBlue TrueBlue": {"kind": "air", "airlines": ["B6"],
                         "aliases": ["jetblue", "trueblue"]},

    # Hotel programs (kind: hotel). Brand substrings match against property name.
    "Marriott Bonvoy": {"kind": "hotel", "aliases": ["marriott", "bonvoy"],
                        "hotel_brands": ["Marriott", "Courtyard", "Fairfield", "SpringHill",
                                         "Residence Inn", "TownePlace", "Ritz-Carlton", "Westin",
                                         "Sheraton", "W Hotels", "Aloft", "Element", "Four Points",
                                         "Le Meridien", "St. Regis", "Autograph", "Moxy", "AC Hotels",
                                         "Delta Hotels", "Gaylord", "Renaissance", "Tribute",
                                         "JW Marriott"]},
    "Hilton Honors": {"kind": "hotel", "aliases": ["hilton", "honors"],
                      "hotel_brands": ["Hilton", "Hampton", "Home2", "Homewood", "Garden Inn",
                                       "Embassy Suites", "DoubleTree", "Waldorf Astoria", "Conrad",
                                       "Canopy", "Curio", "Tapestry", "Tru", "Motto", "LXR",
                                       "Signia", "Tempo", "Spark"]},
    "IHG One Rewards": {"kind": "hotel", "aliases": ["ihg", "one rewards"],
                        "hotel_brands": ["Holiday Inn", "avid", "Garner", "Candlewood", "Staybridge",
                                         "Crowne Plaza", "InterContinental", "Kimpton", "Hotel Indigo",
                                         "EVEN", "Regent", "Six Senses", "voco", "Atwell", "Iberostar"]},
    "World of Hyatt": {"kind": "hotel", "aliases": ["hyatt"],
                       "hotel_brands": ["Hyatt", "Andaz", "Thompson", "Caption", "Alila", "Miraval",
                                        "Grand Hyatt", "Park Hyatt", "Hyatt Regency", "Hyatt Place",
                                        "Hyatt House", "Destination", "Dream", "The Unbound"]},
    "Wyndham Rewards": {"kind": "hotel", "aliases": ["wyndham"],
                        "hotel_brands": ["Wyndham", "Days Inn", "Super 8", "La Quinta", "Baymont",
                                         "Ramada", "Howard Johnson", "Microtel", "Travelodge",
                                         "Wingate", "AmericInn", "Dolce", "Dazzler", "Esplendor"]},
    "Choice Privileges": {"kind": "hotel", "aliases": ["choice", "privileges"],
                          "hotel_brands": ["Comfort", "Quality Inn", "Sleep Inn", "Clarion", "Cambria",
                                           "Ascend", "Econo Lodge", "Rodeway", "MainStay", "WoodSpring",
                                           "Suburban", "Everhome"]},
    "Best Western Rewards": {"kind": "hotel", "aliases": ["best western"],
                             "hotel_brands": ["Best Western", "SureStay", "Aiden", "Sadie", "Glo",
                                              "Vib", "Executive Residency"]},
    "Accor Live Limitless": {"kind": "hotel", "aliases": ["accor", "all ", "live limitless"],
                             "hotel_brands": ["Sofitel", "Novotel", "Mercure", "ibis", "Pullman",
                                              "Fairmont", "Raffles", "Swissotel", "Movenpick",
                                              "MGallery", "Grand Mercure", "Adagio"]},
}


def lookup(name):
    """Return the program definition best matching a free-text name, or None."""
    if not name:
        return None
    q = name.strip().lower()
    # Exact key match first.
    for key, val in PROGRAMS.items():
        if key.lower() == q:
            return dict(val, program=key)
    # Alias substring match.
    for key, val in PROGRAMS.items():
        for alias in val.get("aliases", []):
            if alias in q:
                return dict(val, program=key)
    return None


def main():
    args = sys.argv[1:]
    if not args or args[0] in ("-h", "--help"):
        print(__doc__)
        return
    if args[0] == "--list":
        for key, val in sorted(PROGRAMS.items()):
            print("%-32s %s" % (key, val["kind"]))
        return
    name = " ".join(args)
    result = lookup(name)
    if result is None:
        print(json.dumps({"query": name, "match": None,
                          "note": "No known program matched. Run with --list to see known programs, "
                                  "or brand-bias the search query by hand."}, indent=2))
        return
    print(json.dumps({"query": name, **result}, indent=2))


if __name__ == "__main__":
    main()
