from SQLManager import DatabaseManager
from cfg import DB_URL
import json


manager = DatabaseManager(db_url=DB_URL)
# #manager.add_constants(
#     coneHeight=10.2,
#     cylinderHeight=20.5,
#     Quefeed=100,
#     Qunderfl=50,
#     Flfeed=5.5,
#     psolid=1,
#     pfluid=2,
#     muliqour=3.3
# )

constants = manager.get_constants()
for const in constants:
    print(json.loads(const))