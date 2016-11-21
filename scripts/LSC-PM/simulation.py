from pvtrace import *

study = Scene(uuid="86jfhfQogE9gE9J6e8MupF", force=True)
# study.stats.print_detailed()
a=study.stats.history_from_uid(uid=(6))

study.stats.describe_trajectory(uid_list=a)

sys.exit(0)
