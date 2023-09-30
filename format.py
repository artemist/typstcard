#!/usr/bin/env python3
import argparse
import base64
import csv
import json
import os
import string
import typing
import xml.etree.ElementTree as ET
import requests
import imb


def iso_code(s: str) -> str:
    if len(s) != 2:
        raise ValueError("must be 2 characters long")
    s = s.lower()
    if not (s[0] in string.ascii_lowercase and s[1] in string.ascii_lowercase):
        raise ValueError("must be ascii letters")
    return s


def get_orig_avatar(url: str, name: str) -> typing.Optional[bytes]:
    if not os.path.exists("cache"):
        os.mkdir("cache")
    if os.path.exists("cache/" + name):
        with open("cache/" + name, "rb") as infile:
            return infile.read()
    result = requests.get(url)
    if result.ok:
        with open("cache/" + name, "wb") as outfile:
            outfile.write(result.content)
        return result.content
    return None


def get_avatar(url: str) -> str:
    name = url.split("?")[0].split("/")[-1]
    if os.path.exists(f"cache/{name}.svg"):
        return f"cache/{name}.svg"
    avatar_raster = get_orig_avatar(url, name)
    if avatar_raster is None:
        return ""

    svg_text = f"""<svg viewBox="0 0 480 480" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink">
        <clipPath id="circle">
            <circle cx="240" cy="240" r="240" />
        </clipPath>
        <image width="480" height="480" clip-path="url(#circle)"
            xlink:href="data:;base64,{base64.b64encode(avatar_raster).decode("utf-8")}" />
    </svg>"""

    with open(f"cache/{name}.svg", "w") as svgfile:
        svgfile.write(svg_text)
    return f"cache/{name}.svg"


def get_country_name(
    root: ET.ElementTree, destination: str, alt=None
) -> typing.Optional[str]:
    elements = root.findall(
        f"./localeDisplayNames/territories/territory[@type='{destination.upper()}']"
    )
    normal = None
    for element in elements:
        if element.attrib.get("alt") == alt:
            return element.text
        elif element.attrib.get("alt") is None:
            normal = element.text
    return normal


parser = argparse.ArgumentParser(
    prog="format", description="format postcards with latex"
)
parser.add_argument("template", help="template to use", nargs="?", default="2card")
parser.add_argument(
    "-o", "--origin", help="origin country code", default="us", type=iso_code
)
parser.add_argument(
    "-l",
    "--language",
    help="language to use for countries ",
    default="en",
    type=iso_code,
)
parser.add_argument(
    "-c",
    "--count",
    default=1,
    type=int,
    help="Number of sets of labels to print, default 1 (labels only)",
)
parser.add_argument(
    "-s",
    "--skip",
    default=0,
    type=int,
    help="Number of labels to skip (label sheets only)",
)

parser.add_argument(
    "-a",
    "--address-file",
    default="addresses.csv",
    type=str,
    help="CSV file containing addresses",
)

parser.add_argument(
    "-n",
    "--no-content",
    action="store_true",
    help="Skip content, e.g. to make postcard back labels"
)

args = parser.parse_args()

root = ET.parse(
    f"{os.getenv('CLDR_ROOT')}/share/unicode/cldr/common/main/{args.language}.xml"
)

csvfile = open(args.address_file)
rows = csv.DictReader(csvfile)

current_serial = imb.get_first_serial()
mid = int(open("mailer_id.txt").read().strip())


cards = []
for row in rows:
    if row["Address"] == "":
        continue

    country = (
        []
        if row["Country"].lower() == args.origin
        else [get_country_name(root, row["Country"]).upper()]
    )

    address = row["Address"].split("\n") + country

    if row.get("Avatar", "") != "":
        avatar = get_avatar(row["Avatar"])
    else:
        avatar = None

    cards += [
        {
            "address": "\n".join(address),
            "avatar": avatar,
            "row": row,
            "imb": "",
        }
    ]

cards = cards * args.count

serial = imb.get_first_serial()
if args.origin == "us":
    for card in cards:
        dpc = card["row"].get("DPC", "")
        if dpc != "":
            card["imb"] = imb.generate(
                0, 310, mid, serial, dpc.replace(" ", "").replace("-", "")
            )
            serial += 1
imb.write_current_serial(serial)

with open("options.json", "w") as options:
    json.dump(
        fp=options,
        obj={
            "args": args.__dict__,
            "cards": cards,
        },
    )
