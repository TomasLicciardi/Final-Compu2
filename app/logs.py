from datetime import datetime

def log_writer(queue):
    with open("logs.txt", "a") as log_file:
        while True:
            message = queue.get()
            log_file.write(f"{datetime.now()} - {message}\n")
            log_file.flush() 
