import os, time, sys, sqlite3, hashlib
from rich.console import Console
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer

console=Console()

def get_paths():
    while True:
        tar_path=console.input("[bold italic white]PLEASE ENTER THE TARGATED DIRECTORY/FILE PATH:[/bold italic white]").strip().strip("'")
        if os.path.isdir(tar_path) or os.path.isfile(tar_path):
            break
        else:
            console.print("[bold red]ERROR:[/bold red] [bold italic red]Invalid Address.[/bold italic red]")
    while True:
        db_path=console.input("[bold italic white]PLEASE ENTER THE DIRECTORY ADDRESS YOU WANT DATABASE IN:[/bold italic white]").strip().strip("'")
        if os.path.isdir(db_path):
            path=os.path.join(db_path,"my_db")
            break
        else:
            console.print("[bold red]ERROR:[/bold red] [bold italic red]Invalid Address.[/bold italic red]")
    return tar_path, db_path, path 


def make_db(path):
    try:
        conn=sqlite3.connect(path)
        cursor=conn.cursor()
    except Exception as e:
        console.print("COULD NOT MAKE THE DATABASE.-->",e,style="bold italic red")
    else:
        cursor.execute('''CREATE TABLE IF NOT EXISTS file_recs(id INTEGER PRIMARY KEY, ADDRESS, ACTIVITY, STATUS, HASH)''')
        conn.commit()
        conn.close()
        console.print("TABLE CREATED SUCESSFULLY.",style="bold green")


def add_in_db(address, activity, status, hashed,path):
    try:
        conn=sqlite3.connect(path)
    except Exception as e:
        console.print(f"[bold red]ERROR:[bold red][bold italic red]COULD NOT CONNECT WITH DATABASE.[/bold italic red] ---> {e}")
    else:
        cursor=conn.cursor()
        cursor.execute("INSERT INTO file_recs (ADDRESS, ACTIVITY, STATUS, HASH)VALUES(?,?,?,?)",(address, activity, status, hashed))
        conn.commit()
        conn.close()
        console.print("RECORDS ADDED IN DB SUCCESSFULLY.",style="bold italic white")

def hasher(file_address):
    hsh=hashlib.sha256()
    try:
       with open (file_address,"rb") as f:
            while True:
                chunks=f.read(4096)
                if not chunks:
                    break
                hsh.update(chunks)
    except Exception as e:
        console.print("COULD NOT MAKE THE HASH.-->",e,style="bold italic red")
    else:
        hashed=hsh.hexdigest()
        console.print("NEW HASH:",style="bold italic yellow")
        console.print(hashed,style="bold yellow")
        return hashed
    
def old_files(tar_path):
    if os.path.isdir(tar_path):
        try:
            for root, dirs, files in os.walk(tar_path):
                for file in files:
                    if file=="my_db" or file=="my_db-journal":
                        continue
                    try:
                        file_address=os.path.join(root,file)
                        hashed=hasher(file_address)
                    except Exception as e:
                        console.print(f"[bold red]ERROR:[/bold red][bold italic red]Could not access the file {file_address} --> {e}[/bold italic red]")
                    else:
                        activity="GETTING OLD RECORDS"
                        status="OLD FILE"
                        add_in_db(file_address, activity, status, hashed,path)
        except Exception as e:
            console.print(f"[bold red]ERROR:[/bold red] [bold italic red]Could not access the targated Directory. --> {e}[/bold italic red]")

    if os.path.isfile(tar_path):
        try:
            hashed=hasher(tar_path)
        except Exception as e:
            console.print(f"[bold red]ERROR:[/bold red][bold italic red]Could not access the file {tar_path} --> {e}[/bold italic red]")
        else:
            activity="GETTING OLD RECORDS"
            status="OLD FILE"
            add_in_db(tar_path, activity, status, hashed,path)

def get_hash(file_address,path):
    try:
        conn=sqlite3.connect(path)
        cursor=conn.cursor()
        data=cursor.execute("SELECT HASH FROM file_recs WHERE ADDRESS=? ORDER BY id DESC LIMIT 1",(file_address,))
    except Exception as e:
        console.print(f"[bold red]ERROR:[/bold red][bold italic red] Could not get the old hash. --> {e}[/bold italic red]")
        row="-"
    else:
        row=data.fetchone()
        if row:
            row=row[0]
        else:
            row="-"
        conn.close()
    finally:
        console.print("OLD HASH:",style="bold italic green")
        console.print(row,style="bold italic green")
        return row

def comp(row,hashed):
    if row=="-":
        console.print("COULD NOT COMPARE BECAUSE NO PREVIOUS HASH.",style="bold red")
        status="COULD NOT FIND"
    elif row!=hashed:
        console.print("CONTEXT CHANGED.",style="bold italic white")
        status="CONTEXT CHANGED"
    elif row==hashed:
        console.print("CONTEXT NOT CHANGED.",style="bold italic white")
        status="CONTEXT NOT CHANGED"
    return status

class my_handler(FileSystemEventHandler):
    def on_created(self, event):
        if os.path.isdir(event.src_path):
            return
        file_name=os.path.basename(event.src_path)
        if file_name=="my_db" or file_name=="my_db-journal":
            return
        elif not os.path.exists(event.src_path):
            return

        file_address=event.src_path
        activity="CREATED"
        status="NEW"
        console.print(f"{event.src_path} --> CREATED.",style="bold italic green")
        hashed=hasher(file_address)
        add_in_db(file_address, activity, status, hashed,path)

    def on_modified(self, event):
        if os.path.isdir(event.src_path):
            return
        file_name=os.path.basename(event.src_path)
        if file_name=="my_db" or file_name=="my_db-journal":
            return
        elif not os.path.exists(event.src_path):
            return
        console.print(f"{event.src_path} --> MODIFIED.",style="bold italic cyan")
        file_address=event.src_path
        activity="MODIFIED"
        hashed=hasher(file_address)
        row=get_hash(file_address,path)
        status=comp(row,hashed)
        add_in_db(file_address, activity, status, hashed,path)

    def on_moved(self, event):
        if os.path.isdir(event.src_path):
            return
        path=event.src_path+" ---> "+event.dest_path
        console.print(f"{path} ---> MOVED.",style="bold italic blue")
        file_addr=event.dest_path
        hashed=hasher(file_addr)
        activity="MOVED"
        status="NO CHANGE."
        add_in_db(path, activity, status, hashed,path)

    def on_deleted(self, event):
        file_name=os.path.basename(event.src_path)
        if file_name=="my_db" or file_name=="my_db-journal":
            return
        file_path=event.src_path
        console.print(f"{file_path} ---> DELETED.",style="bold italic purple")
        activity="DELETED"
        status="GONE"
        hashed="-"
        add_in_db(file_path,activity,status,hashed,path)

observer=None
try:
    tar_path,db_path,path=get_paths()
    make_db(path)
    old_files(tar_path)
    observer=Observer()
    observer.schedule(my_handler(),path=tar_path,recursive=True)
    observer.start()
    while True:
        time.sleep(2)
except KeyboardInterrupt:
    if observer is not None:
        observer.stop()
        observer.join()
    print("")
    console.print("[bold italic yellow]<(*-*)>[/bold italic yellow][bold italic red] <( GOOD BYE )>  [/bold italic red][bold italic yellow]<(*-*)>[/bold italic yellow]")
    sys.exit()
