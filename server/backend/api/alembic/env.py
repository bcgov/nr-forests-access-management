import logging
from logging.config import fileConfig
import logging

from sqlalchemy import engine_from_config, create_engine
from sqlalchemy import pool

from alembic import context
from alembic.script import ScriptDirectory
from sqlalchemy import create_engine

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# override logging setup for debugging
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)
LOGGER.debug("test test test")


#from app.db.base import Base  # noqa

# add your model's MetaData object here
# for 'autogenerate' support
# from myapp import mymodel
# target_metadata = mymodel.Base.metadata
# target_metadata = None
target_metadata = app.models.model.metadata

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


def process_revision_directives(context, revision, directives):
    # extract Migration
    migration_script = directives[0]
    # extract current head revision
    head_revision = ScriptDirectory.from_config(context.config).get_current_head()

    if head_revision is None:
        # edge case with first migration
        new_rev_id = 1
    else:
        # default branch with incrementation
        last_rev_id = int(head_revision.lstrip("V"))
        new_rev_id = last_rev_id + 1
    # fill zeros up to 4 digits: 1 -> 0001
    # migration_script.rev_id = '{0:04}'.format(new_rev_id)
    migration_script.rev_id = f"V{new_rev_id}"


def get_url():
    # user = os.getenv("POSTGRES_USER", "postgres")
    # password = os.getenv("POSTGRES_PASSWORD", "")
    # server = os.getenv("POSTGRES_SERVER", "db")
    # db = os.getenv("POSTGRES_DB", "app")
    # url = f"postgresql://{user}:{password}@{server}/{db}"
    url = None
    x_param_url = context.get_x_argument(as_dictionary=True).get('url')
    LOGGER.debug(f"x_param_url: {x_param_url}")
    if x_param_url:
        url = x_param_url
        LOGGER.debug(f"url from -x: {url}")

    if not url:
        url = app.config.getDBString()
        LOGGER.debug(f"url from app config: {url}")
    LOGGER.debug(f"captured the url string: {url}")
    return url


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    #  process_revision_directives=process_revision_directives,

    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        process_revision_directives=process_revision_directives,
        include_schemas=True,
        compare_type=True,
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    #connectable = create_engine(get_url())
    #    with connectable.connect() as connection:
    # connectable = engine_from_config(
    #     config.get_section(config.config_ini_section),
    #     prefix="sqlalchemy.",
    #     poolclass=pool.NullPool,
    # )
    url = get_url()
    print(f"url: {url}")
    connectable = create_engine(get_url())

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            process_revision_directives=process_revision_directives,
            include_schemas=True,
            compare_type=True,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
