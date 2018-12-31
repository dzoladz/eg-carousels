import os
import lxml.etree as et
import configparser

config = configparser.ConfigParser()
config.read("config.ini")

# NAMESPACE MAPPING
ns_map = {
    'atom': 'http://www.w3.org/2005/Atom',
    'dc': 'http://purl.org/dc/elements/1.1/',
    'holdings': 'http://open-ils.org/spec/holdings/v1'
}

def get_statuses(library):
    """ (str) -> str

    Returns the copy status values that are set in config.ini as a string of query parameters

    >>> get_statuses('lib-arcanum')
    '?&status=0'

    """
    x = config[library]['status_codes']
    status_list = x.split(',')
    y = []
    for status in status_list:
        y.append('&status=' + status)
    status_parameters = '?' + ''.join(y)
    return status_parameters

def get_copy_locations(library):
    x = config[library]['copy_locations_to_return']
    copy_location_list = x.split(',')
    y = []
    for location in copy_location_list:
        y.append('&copyLocation=' + location)
    location_parameters = ''.join(y)
    return location_parameters

def get_cover_art(marcxml_entries):
    img_url = []
    for id in marcxml_entries:
        tcn_urn = id.find('atom:id', namespaces=ns_map)
        if len(tcn_urn) is not None:
            tcn = tcn_urn.text.split(':')[2]
            image_url = 'http://' + get_host() + '/opac/extras/ac/jacket/medium/r/' + tcn
            img_url.append(image_url)
    return img_url

def make_url_base(marcxml_entries, library):
    items_url = []
    for id in marcxml_entries:
        tcn_urn = id.find('atom:id', namespaces=ns_map)
        if len(tcn_urn) is not None:
            tcn = tcn_urn.text.split(':')[2]
            item_url = 'http://' + return_lib_subdomain(library) + '.' + get_host() + '/eg/opac/record/' + tcn
            items_url.append(item_url)
    return items_url

def item_return_count(library):
    count = config[library]['num_items_to_return']
    return count

def return_lib_shortname(library):
    shortname = config[library]['shortname']
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

def make_query_url(library):
    url = 'http://' + return_lib_subdomain(library) + '.' + get_host() + '/opac/extras/browse/atom/item-age/' \
         + return_lib_shortname(library) + '/1/' + item_return_count(library) \
         + get_statuses(library) + get_copy_locations(library)
    return url

# ---------------------------
sections = config.sections()
for library in sections:
    if library.startswith('lib-'):
        url = make_query_url(library)
        print(url)
        marcxml = et.parse(url) # Parse Returned MARCXML
        books = marcxml.findall('atom:entry', namespaces=ns_map)
        filename = get_output_path() + return_lib_subdomain(library) + '/' + get_output_filename()
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        with open(filename, 'w') as file:
            file.write('<html><head> \
                    <link rel="stylesheet" type="text/css" href="https://cdnjs.cloudflare.com/ajax/libs/slick-carousel/1.5.9/slick.min.css"/> \
                    <link rel="stylesheet" type="text/css" href="https://cdnjs.cloudflare.com/ajax/libs/slick-carousel/1.5.9/slick-theme.min.css"/> \
                    <script type="text/javascript" src="https://cdnjs.cloudflare.com/ajax/libs/jquery/2.2.1/jquery.min.js"></script> \
                    <script type="text/javascript" src="https://cdnjs.cloudflare.com/ajax/libs/slick-carousel/1.5.9/slick.min.js"></script> \
                    </head><body> \
                    <div style="width: 50%; height: 200px; background-color: grey;"> \
                    <div id="test">')
            for i in range(len(make_url_base(books, library))):
                file.write('<div><a href="' + make_url_base(books, library)[i] + '" target="_blank"><img src="' + get_cover_art(books)[i] + '"></a></div>')
            file.write('</div> \
                        </div> \
                        <script>$(document).ready(function(){ $("#test").slick({ dots: true, slidesToShow: 3, slidesToScroll: 1, autoplay: true, autoplaySpeed: 2000, arrows: true, variableWidth: true }); });</script> \
                        </body></html>')
