import xml.dom.minidom
from xmlrpc.server import SimpleXMLRPCServer
from xmlrpc.server import SimpleXMLRPCRequestHandler
from requests.exceptions import RequestException
import requests
import os
import xml.etree.ElementTree as ET
from datetime import datetime
import threading
import logging

logging.basicConfig(level=logging.INFO)

class RequestHandler(SimpleXMLRPCRequestHandler):
    rpc_paths = ('/RPC2',)

def prettify_xml_element(element):
    rough_string = ET.tostring(element, 'utf-8')
    reparsed = xml.dom.minidom.parseString(rough_string)
    return reparsed.toprettyxml(indent="  ")

def get_or_create_tree(topic):
    filename = f"{topic}.xml"
    if os.path.exists(filename):
        tree = ET.parse(filename)
        root = tree.getroot()
    else:
        root = ET.Element("data")
        tree = ET.ElementTree(root)
    return tree, root


def add_entry(topic, note_name, text):
    try:
        tree, root = get_or_create_tree(topic)
        # The server generates the current timestamp
        current_timestamp = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")

        # Check for the existing topic element or create a new one
        topic_element = None
        for t in root.findall('topic'):
            if t.attrib.get('name') == topic:
                topic_element = t
                break
        if topic_element is None:
            topic_element = ET.SubElement(root, 'topic', name=topic)

        # Create a new note element with the note name and text
        note_element = ET.SubElement(topic_element, 'note', name=note_name)
        text_element = ET.SubElement(note_element, 'text')
        text_element.text = text  # Ensure this is the note content

        # Add the generated timestamp to the note
        timestamp_element = ET.SubElement(note_element, 'timestamp')
        timestamp_element.text = current_timestamp  # Ensure this is the timestamp

        # Write the XML to file using pretty printing
        with open(f"{topic}.xml", "w") as file:
            file.write(prettify_xml_element(root))

        return "New note added."
        logging.info(f"Entry added to {topic}")
    except Exception as e:
        logging.error("Error adding entry", exc_info=True)
        return f"An error occurred: {e}"


def get_entry(topic):
    tree, root = get_or_create_tree(topic)
    notes = []
    for topic_element in root.findall('topic'):
        if topic_element.attrib.get('name') == topic:
            for note in topic_element.findall('note'):
                note_text_element = note.find('text')
                if note_text_element is not None:
                    notes.append(note_text_element.text)
    if notes:
        return f"Notes for {topic}: {notes}"
    else:
        return "Topic not found."


def query_wikipedia(topic):
    url = f"https://en.wikipedia.org/w/api.php?action=opensearch&search={topic}&limit=1&namespace=0&format=json"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            result = response.json()
            if result[1]:
                link = result[3][0]
                return f"More info on {topic}: {link}"
            else:
                return "No Wikipedia article found."
        else:
            return "Failed to fetch data from Wikipedia."
    except RequestException as e:
        return f"Error during Wikipedia query: {str(e)}"

class ThreadedXMLRPCServer(SimpleXMLRPCServer):
    def __init__(self, *args, **kwargs):
        SimpleXMLRPCServer.__init__(self, *args, **kwargs)
        self.allow_reuse_address = True

    def process_request(self, request, client_address):
        """Start a new thread to process the request."""
        thread = threading.Thread(target=self._process_request, args=(request, client_address))
        thread.daemon = True
        thread.start()

    def _process_request(self, request, client_address):
        """Handle requests in a new thread."""
        SimpleXMLRPCServer.process_request(self, request, client_address)

with ThreadedXMLRPCServer(('0.0.0.0', 8000), requestHandler=RequestHandler) as server:
    server.register_introspection_functions()

    server.register_function(add_entry, 'add_entry')
    server.register_function(get_entry, 'get_entry')
    server.register_function(query_wikipedia, 'query_wikipedia')

    print("Serving XML-RPC on localhost port 8000...")
    server.serve_forever()
