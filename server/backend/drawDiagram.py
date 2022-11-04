""" Simple test script to generate and ERD from the ORM model

Other option, lighter and possibly easier to install as its just a binary
originally written in go - tbls (https://github.com/k1LoW/tbls#quick-start)

"""

import api.app.models.model as model


from sqlalchemy_schemadisplay import create_schema_graph
from sqlalchemy import MetaData


graph = create_schema_graph(metadata=model.metadata)
graph.write_png('fam_erd.png')
