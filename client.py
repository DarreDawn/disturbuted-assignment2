import xmlrpc.client
from datetime import datetime

# Connect to the server
server_url = 'http://localhost:8000'
s = xmlrpc.client.ServerProxy(server_url, allow_none=True, use_builtin_types=True)

while True:
    topic = input("Enter topic: ")
    note_name = input("Enter note name: ")
    text = input("Enter text: ")

    try:
        response = s.add_entry(topic, note_name, text)
        print("Server response:", response)
    except Exception as e:
        print(f"An error occurred: {e}")
        for i in range(3):
            try:
                response = s.add_entry(topic, note_name, text)
                print(response)
                break
            except Exception as retry_e:
                print(f"Retry {i + 1} failed: {retry_e}")
    try:
        print(s.get_entry(topic))
    except Exception as e:
        print(f"An error occurred while retrieving entries: {e}")

    wiki_topic = input("Enter Wikipedia topic to search: ")
    try:
        print(s.query_wikipedia(wiki_topic))
    except Exception as e:
        print(f"An error occurred while querying Wikipedia: {e}")

    again = input("Do you want to perform another operation? (yes/no): ")
    if again.lower() != 'yes':
        break
