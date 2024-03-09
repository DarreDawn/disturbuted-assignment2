import xmlrpc.client
import threading

def client_thread(topic, note_name, text):
    s = xmlrpc.client.ServerProxy('http://localhost:8000')
    response = s.add_entry(topic, note_name, text)
    print(response)

threads = []
for i in range(5):
    t = threading.Thread(target=client_thread, args=(f"Topic {i}", f"Note {i}", "This is a test."))
    threads.append(t)
    t.start()

for t in threads:
    t.join()
