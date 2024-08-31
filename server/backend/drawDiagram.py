""" Simple test script to generate and ERD from the ORM model

Other option, lighter and possibly easier to install as its just a binary
originally written in go - tbls (https://github.com/k1LoW/tbls#quick-start)

"""

from api.app.models import metadata

from sqlalchemy_schemadisplay import create_schema_graph

graph = create_schema_graph(metadata=metadata)
graph.write_png("fam_erd.png")
