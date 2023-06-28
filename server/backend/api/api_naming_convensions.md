
fixtures:

data fixtures that return data used to construct a database state:
named by what kind of data they contain, followed by _data (optional,
started not including this) followed
by the type they return

* application_dict - returns dict
* application_data_model - return orm model data
* application_data_pydantic - returns as pydantic model
* user_dict - returns user data as a dict... (_data not included.)



fixtures that return database sessions

* dbsession_<description of whats in the db>
* dbsession_fam_roles_concrete

<!-- trigger/junk commit -->
