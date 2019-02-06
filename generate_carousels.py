import os
import lxml.etree as et
import configparser
import requests
import time

config = configparser.ConfigParser()
config.read("config.ini")

# NAMESPACE MAPPING
ns_map = {
    'atom': 'http://www.w3.org/2005/Atom',
    'dc': 'http://purl.org/dc/elements/1.1/',
    'holdings': 'http://open-ils.org/spec/holdings/v1'
}

def get_statuses(library):
    if library == 'None':
        library = 'lib-consortium'
    x = config[library]['status_codes']
    status_list = x.split(',')
    y = []
    for status in status_list:
        y.append('&status=' + status)
    status_parameters = '?' + ''.join(y)
    return status_parameters

def get_copy_locations(library):
    if library == 'None':
        library = 'lib-consortium'
    x = config[library]['copy_locations_to_return']
    copy_location_list = x.split(',')
    y = []
    for location in copy_location_list:
        y.append('&copyLocation=' + location)
    location_parameters = ''.join(y)
    return location_parameters

def item_return_count(library_subdomain):
    if library_subdomain == 'None':
        count = config['lib-consortium']['shortname']
    else:
        count = config[library_subdomain]['num_items_to_return']
    return count

def return_lib_shortname(library_subdomain):
    if library_subdomain == 'None':
        shortname = config['lib-consortium']['shortname']
    else:
        shortname = config[library_subdomain]['shortname']
    return shortname

def return_lib_subdomain(library):
    subdomain = config[library]['subdomain']
    return subdomain

def get_host():
    host = config['global']['host']
    return host

def get_output_path():
    outfile_path = config['global']['output_file_path']
    return outfile_path

def get_output_filename():
    outfile_filename = config['global']['output_filename']
    return outfile_filename

def make_query_urls(config):
    urls = {}
    for library in config:
        if library.startswith('lib-'):
            if library != 'lib-consortium':
                url = 'http://' + return_lib_subdomain( \
                    library) + '.' + get_host() + '/opac/extras/browse/atom/item-age/' \
                      + return_lib_shortname(library) + '/1/' + item_return_count(library) \
                      + get_statuses(library) + get_copy_locations(library)
            else:
                url = 'http://' + get_host() + '/opac/extras/browse/atom/item-age/' \
                      + return_lib_shortname(library) + '/1/' + item_return_count(library) \
                      + get_statuses(library) + get_copy_locations(library)
            urls.update( {return_lib_subdomain(library) : url} )
    return urls

def get_tcns(query_url_dict):
    tcns = {}
    for library, query_url in query_url_dict.items():
        marcxml = et.parse(query_url) # Parse Returned MARCXML
        books = marcxml.findall('atom:entry', namespaces=ns_map)
        tcn_list = []
        for book in books:
            urn = book.find('atom:id', namespaces=ns_map)
            tcn = urn.text.split(':')[2]
            tcn_list.append(tcn)
        tcns.update( { library : tcn_list } )
    return tcns

def check_cover_art(tcns_dict):
    good_covers = {}
    for library, tcn_list in tcns_dict.items():
        good_tcns = []
        if library != "None":
            for tcn in tcn_list:
                image_url = 'http://' + library + '.cool-cat.org/opac/extras/ac/jacket/medium/r/' + tcn
                response_status = requests.head(image_url, timeout=5).status_code
                response_length = requests.head(image_url).headers['content-length']
                time.sleep(0.2)
                if response_status == 200 and int(response_length) > 200:
                    good_tcns.append(tcn)
        else:
            for tcn in tcn_list:
                image_url = 'http://cool-cat.org/opac/extras/ac/jacket/medium/r/' + tcn
                response_status = requests.head(image_url, timeout=5).status_code
                response_length = requests.head(image_url).headers['content-length']
                time.sleep(0.2)
                if response_status == 200 and int(response_length) > 200:
                    good_tcns.append(tcn)
        good_covers.update( { library : good_tcns } )
    return good_covers

def write_files(good_covers_dict):
    for library, good_tcns in good_covers_dict.items():
        if library == 'None':
            filename = get_output_path() + get_output_filename()
        else:
            filename = get_output_path() + library + '/' + get_output_filename()
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        with open(filename, 'w') as file:
            file.write('<html><head> \
                    <link rel="stylesheet" type="text/css" href="https://cdnjs.cloudflare.com/ajax/libs/slick-carousel/1.5.9/slick.min.css"/> \
                    <link rel="stylesheet" type="text/css" href="https://cdnjs.cloudflare.com/ajax/libs/slick-carousel/1.5.9/slick-theme.min.css"/> \
                    <style> \
                    .slick-slide{ margin: 0px 7px 0px 7px; } \
                    .slick-slide img { box-shadow: 4px 8px 6px 0px rgba(0, 0, 0, 0.50); } \
                    .slick-list { overflow: visible; } \
                    .slick-slide > a > img { height: 200px; width: 133px; } \
                    #carousel-wrapper { height: 200px; background-color: transparent; } \
                    </style> \
                    <script type="text/javascript" src="https://cdnjs.cloudflare.com/ajax/libs/jquery/2.2.1/jquery.min.js"></script> \
                    <script type="text/javascript" src="https://cdnjs.cloudflare.com/ajax/libs/slick-carousel/1.5.9/slick.min.js"></script> \
                    </head></body> \
                    <div id="carousel-wrapper"> \
                    <div id="carousel">')
            if library == 'None':
                for tcn in good_tcns:
                    file.write('<div><a href="https://cool-cat.org/eg/opac/record/' + tcn + '" target="_blank"><img src="https://cool-cat.org/opac/extras/ac/jacket/medium/r/' + tcn + '"></a></div>')
            else:
                for tcn in good_tcns:
                    file.write('<div><a href="https://' + library + '.cool-cat.org/eg/opac/record/' + tcn + '" target="_blank"><img src="https://' + library + '.cool-cat.org/opac/extras/ac/jacket/medium/r/' + tcn + '"></a></div>')
            file.write('</div> \
                        </div> \
                        <script>$(document).ready(function(){ $("#carousel").slick({ dots: false, arrows: false, infinite: true, cssEase: "linear", centerMode:true, slidesToShow: 3, slidesToScroll: 1, autoplay: true, autoplaySpeed: 2000, variableWidth: true }); });</script> \
                        </body></html>')

# ---------------------------
sections = config.sections()
query_urls = make_query_urls(sections)
tcns = get_tcns(query_urls)
good_covers = check_cover_art(tcns)
write_files(good_covers)