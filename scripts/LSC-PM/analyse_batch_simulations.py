from pvtrace import *

scenes_to_analyze = []

luminophore_name = 'Red305'
solvent = 'MB'
for mainloop_i in range(0, 2):
    luminophore_conc = mainloop_i * 10
    name = luminophore_name + '_' + str(luminophore_conc) + '_' + solvent
    scenes_to_analyze.append(name)

print("The following simulations will be analyzed")
print(scenes_to_analyze)

top_reflections_query = "SELECT MAX(uid) FROM photon GROUP BY pid HAVING uid IN" \
                    "(SELECT uid FROM state WHERE " \
                    "ray_direction_bound='Out' AND surface_id='top' AND intersection_counter=1 GROUP BY uid)"
text = ""
for scene in scenes_to_analyze:
    study = Scene(uuid=scene, force=True, level=logging.DEBUG)
    query_result = itemise(study.stats.db.cursor.execute(top_reflections_query).fetchall())
    top_relfected = len(query_result)
    text = text + (scene + ": " + str(top_relfected)+"\n")

print(text)
sys.exit(0)
