import multiprocessing
import threading
from numpy.lib.function_base import append
import typer
import sqlite3
import os
import time
from pathlib import Path
from typing import Optional
from queue import Empty
from pvtrace.cli.parse import parse
from pvtrace.light.event import Event
from pvtrace.scene.renderer import MeshcatRenderer

BASE_DIR = Path(__file__).resolve().parent.parent
SCHEMA = BASE_DIR / "data" / "schema.sql"
if not SCHEMA.exists():
    raise FileNotFoundError("Cannot find database schema")
SCHEMA = str(SCHEMA)

RENDERER = dict()

app = typer.Typer()


def prepare_database(dbfilepath):
    with open(SCHEMA) as fp:
        connection = sqlite3.connect(dbfilepath)
        cur = connection.cursor()
        cur.executescript(fp.read())
        connection.commit()
        connection.close()


def write_ray(cur, ray, global_throw_id):
    values = (
        global_throw_id,
        ray.position[0],
        ray.position[1],
        ray.position[2],
        ray.direction[0],
        ray.direction[1],
        ray.direction[2],
        ray.wavelength,
        ray.source,
        ray.travelled,
    )
    cur.execute("INSERT INTO ray VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", values)
    return cur.lastrowid


def write_event(cur, event, metadata, ray_db_id):

    component = None
    hit = None
    container = None
    adjacent = None
    facet = None

    if metadata:
        component = metadata.get("component", None)
        hit = metadata.get("hit", None)
        container = metadata.get("container", None)
        adjacent = metadata.get("adjacent", None)
        facet = metadata.get("facet", None)

    values = (ray_db_id, event.name, component, hit, container, adjacent, facet)
    cur.execute("INSERT INTO event VALUES (?, ?, ?, ?, ?, ?, ?)", values)


def write_to_database(dbfilepath, queue, stop, progress, evertything):

    print(f"Opening connection {dbfilepath}")
    connection = sqlite3.connect(dbfilepath)

    global_completed = 0
    counts = dict()
    global_ids = dict()

    while True:

        if stop.is_set():
            connection.close()
            return

        try:
            info = queue.get(True, 1.0)
            pid, throw_idx = info[:2]

            # Keep track of counts from this process
            if pid not in counts:
                counts[pid] = throw_idx + 1
            counts[pid] = throw_idx + 1

            if sum(counts.values()) > global_completed:
                global_completed += 1
                progress.update(1)

            # Assign unique ID for this process and throw
            if (pid, throw_idx) not in global_ids:
                global_ids[(pid, throw_idx)] = len(global_ids)

            if evertything:
                # Write all rays to database, not just the initial and final
                cur = connection.cursor()
                ray, event, metadata = info[2:]
                ray_db_id = write_ray(cur, ray, global_ids[(pid, throw_idx)])
                write_event(cur, event, metadata, ray_db_id)
                connection.commit()
            else:
                raise NotImplementedError("Database must store all events")

        except Empty:
            pass


@app.command(short_help="Run raytrace simulations")
def simulate(
    scene: Optional[str] = typer.Option(...),
    rays: Optional[int] = typer.Option(100),
    workers: Optional[int] = typer.Option(None),
):

    print("WARNING: pvtrace-cli is still in development.")
    print(f"Reading {os.path.relpath(scene)}")
    scene_yml_path = scene
    scene = parse(scene_yml_path)

    # Database file is in the same folder and has the same name as the yml file
    # but with the .sqlite3 extension
    dbfilepath = os.path.abspath(os.path.splitext(scene_yml_path)[0]) + ".sqlite3"
    if os.path.exists(dbfilepath):
        delete = typer.confirm("Delete existing database file?", abort=True)
        if delete:
            os.remove(dbfilepath)
    prepare_database(dbfilepath)

    # Prepare for multiprocessing
    manager = multiprocessing.Manager()
    queue = manager.Queue(maxsize=5000)
    stop = threading.Event()
    with typer.progressbar(length=rays) as progress:
        monitor_thread = threading.Thread(
            target=write_to_database,
            args=(dbfilepath, queue, stop, progress, True),
        )
        monitor_thread.start()

        try:
            scene.simulate(rays, workers=workers, queue=queue)
        finally:
            # Might need to wait for the queue to be empty!
            while queue.qsize() > 0:
                time.sleep(0.2)
            stop.set()
            monitor_thread.join()

    print("OK")


@app.command(short_help="View scene file in browser")
def show(
    scene: Path = typer.Option(
        ...,
        "--scene",
        "-s",
        exists=True,
        file_okay=True,
        dir_okay=False,
        writable=False,
        readable=True,
        resolve_path=True,
    ),
    zmq: str = typer.Option(..., "--zmq", "-z"),
    wireframe: Optional[bool] = typer.Option(True),
):
    scene_obj = parse(scene)
    if "renderer" not in RENDERER:
        renderer = MeshcatRenderer(zmq_url=zmq, open_browser=False, wireframe=wireframe)
        RENDERER.update(
            {
                "web_url": zmq,
                "renderer": renderer,
            }
        )
        RENDERER["scene"] = scene_obj
    renderer = RENDERER["renderer"]
    renderer.remove(RENDERER["scene"])
    renderer.render(RENDERER["scene"])
    renderer.vis.open()


def main():
    app()


if __name__ == "__main__":
    main()