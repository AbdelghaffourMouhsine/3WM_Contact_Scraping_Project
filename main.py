################################################ main ###########################################################
#################################################################################################################
import threading
import time
import os
from LoadLinksData import SharedListURLs
from ContactStorage import ContactStorage
from WorkerThread import WorkerThread

os.makedirs("results", exist_ok=True)

# Créer une liste partagée, une file de résultats et un verrou CSV
shared_list = SharedListURLs()
shared_list.load_data()

# Créer et démarrer les threads
num_threads = 10

start = 0
end = min(shared_list.nb_URLs,shared_list.nb_URLs)
step = 100

for i in range(start, end, step):
    
    shared_list.select_data(i,i+step)
    
    contact_storage = ContactStorage('results/contacts_3')
    
    threads = []
    for j in range(num_threads):
        thread = WorkerThread(j+1, shared_list, contact_storage)
        thread.start()
        threads.append(thread)

    # Attendre que tous les threads se terminent
    for thread in threads:
        thread.join()

    # Fermer les fichiers
    contact_storage.close_file()
    contact_storage.close_file_errors()
    
    print(f"%"*100)
    print("saved URLs : ",i+step)
    print(f"%"*100)