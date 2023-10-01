#!/usr/bin/env python3
import argparse
import base64
import csv
import hashlib
import json
import os
import string
import typing
import urllib.parse
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


def get_discord_avatar(
    url: urllib.parse.ParseResult, secrets: dict
) -> (typing.Optional[str], str):
    try:
        token = secrets["discord_token"]
        user_info = requests.get(
            f"https://discord.com/api/users/{url.path}",
            headers={"Authorization": f"Bot {token}"},
        ).json()
        avatar_hash = user_info["avatar"]
        return (
            f"https://cdn.discordapp.com/avatars/{url.path}/{avatar_hash}.png?size=4096",
            "png",
        )
    except KeyError:
        return None, ""


def get_fedi_avatar(
    url: urllib.parse.ParseResult, secrets: dict
) -> (typing.Optional[str], str):
    try:
        mastodon_api = secrets["mastodon_api"]
        user_info = requests.get(
            f"{mastodon_api}/api/v1/accounts/lookup", params={"acct": url.path}
        ).json()
        avatar_url = user_info["avatar_static"]
        extension = avatar_url.split(".")[-1]
        return avatar_url, extension
    except KeyError:
        return None, ""


def get_orig_avatar(url: str, basename: str, secrets: dict) -> typing.Optional[bytes]:
    if not os.path.exists("cache"):
        os.mkdir("cache")

    url_parts = urllib.parse.urlparse(url)
    if url_parts.scheme == "fedi":
        real_url, extension = get_fedi_avatar(url_parts, secrets)
    elif url_parts.scheme == "discord":
        real_url, extension = get_discord_avatar(url_parts, secrets)
    else:
        real_url = url
        extension = url_parts.path.rsplit(".", 1)[1]

    if real_url is None:
        return None

    img_name = f"cache/{basename}.{extension}"

    if os.path.exists(img_name):
        with open(img_name, "rb") as infile:
            return infile.read()
    result = requests.get(real_url)
    if result.ok:
        with open(img_name, "wb") as outfile:
            outfile.write(result.content)
        return result.content
    return None


def get_avatar(url: str, secrets: dict) -> str:
    basename = hashlib.sha256(url.encode("utf-8")).hexdigest()
    if os.path.exists(f"cache/{basename}.svg"):
        return f"cache/{basename}.svg"
    avatar_raster = get_orig_avatar(url, basename, secrets)
    if avatar_raster is None:
        return ""

    svg_text = f"""<svg viewBox="0 0 480 480" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink">
        <clipPath id="circle">
            <circle cx="240" cy="240" r="240" />
        </clipPath>
        <image width="480" height="480" clip-path="url(#circle)"
            xlink:href="data:;base64,{base64.b64encode(avatar_raster).decode("utf-8")}" />
    </svg>"""

    with open(f"cache/{basename}.svg", "w") as svgfile:
        svgfile.write(svg_text)
    return f"cache/{basename}.svg"


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
    help="Skip content, e.g. to make postcard back labels",
)

args = parser.parse_args()

root = ET.parse(
    f"{os.getenv('CLDR_ROOT')}/share/unicode/cldr/common/main/{args.language}.xml"
)

csvfile = open(args.address_file)
rows = csv.DictReader(csvfile)

with open("secrets.json") as secrets_file:
    secrets = json.load(secrets_file)

current_serial = imb.get_first_serial()
mid = secrets.get("mailer_id")


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
        avatar = get_avatar(row["Avatar"], secrets)
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
        if dpc != "" and mid is not None:
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
