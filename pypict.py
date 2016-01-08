#!/usr/bin/python3.5
"""Download picture on website.

Search in a webpage all links and download them according to some
caracteristics.
"""

# import sysconfig
# print(sysconfig.get_python_version())
import re
import os
import sys

from concurrent.futures import ThreadPoolExecutor
from requests_futures.sessions import FuturesSession

from utils import get, wget, cd, pwd


def filename_check(filename):
    """Rename the file.

    If file exist, it return a i+1 nd version of the name of the
    file.
    """
    # TODO case where the file doesn't have extension
    while os.path.isfile(filename):
        regex = " (\([0-9]+\))(\.?[a-zA-Z0-9]*)$"
        token = re.search(regex, filename)
        if not token:
            extension = "." + filename.split(".")[-1]
            filename = "{} (2){}".format(filename[:-len(extension)], extension)
        else:
            version, extension = token.groups()
            version = int(version.strip("()")) + 1
            filename = "{} ({}){}".format(filename[:-len(token.group())],
                                          version, extension)
    return filename


def get_all_http(url):
    """Search url for all http(s) links."""
    start = 'http'
    text = get(url.strip()).text
    i_start = text.find(start)
    while i_start != -1:
        next = text.find('"', i_start + 1)
        i_end = next if next != -1 else text.find("'", i_start + 1)
        yield text[i_start:i_end]
        i_start = text.find(start, i_end + 1)


def get_all_http_func(url):
    """Almost same as get_all_http but in a fontional way.

    WARNING : the output are sometimes differents.
    """
    text = get(url.strip()).text
    return map((lambda text: "http" + text),
               map((lambda text: text.split("'")[0]),
               map((lambda text: text.replace('"', "'")),
                   text.split('http')[1:])))


def is_type(link, type_file="img"):
    """If link is a type of file <type_file>."""
    # TODO : how to know if a binary file is a picture ?
    if type_file == "all":
        return True

    switch = {"img": ['jpg', 'png', 'bmp', 'gif'],  # and upper
              "video": ['mp4', 'flv', 'flac']}
    if type_file not in switch:
        raise Exception('Actual recognise files are "img" and "video"')
    extension = switch[type_file]
    for ext in extension:
        if ext in link or ext.upper() in link:
            return True
    else:
        return False


def wget_future(future, subfolder="", filename=""):
    """Wget with a async way to download."""
    response = future.result()
    data = response.content
    url = response.url
    if filename == "":
        filename = os.path.split(url)[-1]
    filename = os.path.join(subfolder, filename)
    filename = filename_check(filename)
    if subfolder != "":
        os.makedirs(subfolder, exist_ok=True)
    try:
        with open(filename, "wb") as f_out:
            f_out.write(data)
    except:
        print("Error with file: " + filename)


def snif(url, locate="tmp", async=True, condition=is_type):
    """Main function to download files."""
    if type(async) == int and async > 2:
        session = FuturesSession(
            executor=ThreadPoolExecutor(max_workers=async))
    elif async:
        session = FuturesSession()
    links = filter(condition, get_all_http_func(url))
    number_links = 0
    for link in links:
        number_links += 1
        try:
            if async:
                session.get(link).add_done_callback(
                    lambda future:
                        wget_future(future, subfolder=locate))
                # wget_async(link, subfolder=locate, async=40)
            else:
                wget(link, subfolder=locate)
        except ConnectionError:
            print("Problème avec le lien:" + link)
            continue
    print(number_links, " éléments téléchargeables.")

if __name__ == "__main__":
    if len(sys.argv) > 2:
        cd(pwd())
        snif(sys.argv[1], sys.argv[2])
