"""
when deploying to AWS the FAM api will use flyway to run the migrations to
a RDS database

This script can be run at any time.  It will ensure that any alembic migration
files have corresponding flyway migration files.

How it works:

1. alembic configuration has been modified to name migrations using the flyway
    migration naming syntax, ie V1_<migration_name>... V2_<migration_name> etc

2. Script will iterate through the alembic migration files, for each migration
    file will look for a corresponding file in the flyway directory

3. If an alembic migration file exists without a corresponding flyway migration
    a flyway migration will be generated.

Assumptions:
    * flyway migrations will always move forward, a rollback actually will
        be a new migration that does an undo.
    * will not use alembic branches

Future considerations
    * current flow only allows for migrations to flow from alembic.
    * Could potentially implement a way of supporting migrations from either
        flyway OR alembic, but creating a script that autogenerates a
        model-autogen.py file using sqlacodegen, then having a model.py that
        subclasses the model-autogen.py and implements alembic changes from
        that class: Needs research spike to confirm it would work.

"""
import contextlib
import logging
import os
import re

import alembic.config
from alembic import command

LOGGER = None


class MigrationFilePaths:
    """utility methods for working with paths to flyway and alembic migration
    files.
    """

    def __init__(self):
        self.migration_file_prefix = "V"

    def get_alembic_ini_file_path(self):
        alembic_path = os.path.realpath(
            os.path.join(os.path.dirname(__file__), "..", "alembic.ini")
        )
        return alembic_path

    def get_alembic_dir(self):
        """gets the directory taht contains the alembic.ini... the directory
        from which alembic commands need to be run.

        :return: _description_
        :rtype: _type_
        """
        alembic_dir = os.path.realpath(os.path.join(os.path.dirname(__file__), ".."))
        return alembic_dir

    def get_alembic_version_from_migration(self, alembic_migration_file_path):
        file_name = os.path.basename(alembic_migration_file_path)

        alembic_version = file_name[: file_name.find("_")]
        LOGGER.debug(f"alembic_version: {alembic_version}")
        return alembic_version

    def get_flyway_file_path(self, alembic_migration_file_path):
        """remove the .py extension
        add and extra _ character after the versions string
        add a .sql suffix
        append the flyway directory to the path

        :param alembic_migration_file_path: _description_
        :type alembic_migration_file_path: _type_
        """
        flyway_file = os.path.splitext(alembic_migration_file_path)[0]
        loc = flyway_file.find("_")
        flyway_file = flyway_file[0:loc] + "_" + flyway_file[loc:] + ".sql"
        flyway_dir = self.get_flyway_migration_directory()
        LOGGER.debug(f"flyway file: {flyway_file}")
        flyway_file_with_path = os.path.join(flyway_dir, flyway_file)
        LOGGER.debug(f"flyway_file_with_path: {flyway_file_with_path}")
        return flyway_file_with_path

    def get_alembic_migration_file(self):
        """iterates through the files in the alembic version directory and
        returns a list of files that match the expected naming convension.

        :return: list of alembic version files
        :rtype: list
        """
        version_dir = self.get_alembic_version_dir()
        files_in_version_dir = os.listdir(version_dir)
        version_regex = re.compile(f"^{self.migration_file_prefix}\d+_.*")  # noqa
        version_files = []
        for version_file in files_in_version_dir:
            if version_regex.match(version_file):
                version_files.append(version_file)
        LOGGER.debug(f"version_files: {version_files}")
        return version_files

    def get_previous_alembic_version_from_migration(self, alembic_migration_file_path):
        cur_ver = self.get_alembic_version_from_migration(alembic_migration_file_path)
        if cur_ver == f"{self.migration_file_prefix}1":
            return None
        prev_ver_num = int(cur_ver.replace(self.migration_file_prefix, ""))
        prev_ver_num -= 1
        prev_ver = f"{self.migration_file_prefix}{prev_ver_num}"
        return prev_ver

    def get_alembic_version_dir(self):
        """calculates the expected path to where the alembic migration version
        files should be located relative to the location of this file

        :return: path to the alembic version directory
        :rtype: str / path
        """
        return os.path.realpath(os.path.join(os.path.dirname(__file__), "versions"))

    def get_flyway_migration_directory(self):
        flyway_dir = os.path.realpath(
            os.path.join(os.path.dirname(__file__), "..", "..", "..", "flyway", "sql")
        )
        return flyway_dir

    def flyway_migration_exists(self, alembic_migration_file_path):
        """returns a boolean indicating if a flyway migration exists that
        corresponds with the supplied alembic migration file

        :param alembic_migration_file_path: _description_
        :type alembic_migration_file_path: _type_
        """
        flyway_file = self.get_flyway_file_path(alembic_migration_file_path)
        LOGGER.debug(f"flyway_file: {flyway_file}")
        return os.path.exists(flyway_file)

    def flyway_migration_version_exists(self, version: str) -> bool:
        # get the 12 from V12 (version)
        alembic_version_int = version[1:]
        LOGGER.debug(f"alembic version int: {alembic_version_int}")
        flyway_dir = self.get_flyway_migration_directory()
        # get all the migration files
        flyway_migration_files = [
            f
            for f in os.listdir(flyway_dir)
            if os.path.isfile(os.path.join(flyway_dir, f))
        ]
        flyway_version_ints = []
        # get the version numbers found in the flyway directory
        for migration_file in flyway_migration_files:
            migration_version = migration_file.split("__")[0][1:]
            LOGGER.debug(f"migration_version: {migration_version}")
            flyway_version_ints.append(migration_version)
        # check to see if the version number for alembic exists in the versions
        # just extracted from flyway migration files
        flyway_version_exists = False
        if alembic_version_int in flyway_version_ints:
            flyway_version_exists = True
        return flyway_version_exists


class CreateFlywayMigraions:
    def __init__(self):
        self.path_utile = MigrationFilePaths()

    def create_flyway_migrations(self):
        """
        iterates through the list of migrations in the alembic directory
        if a corresponding migration for flyway doesn't exist calls methods to
        create it
        """
        alembic_migrations = self.path_utile.get_alembic_migration_file()
        for alembic_migration in alembic_migrations:
            alembic_version = self.path_utile.get_alembic_version_from_migration(
                alembic_migration
            )
            if not self.path_utile.flyway_migration_exists(alembic_migration):
                if self.path_utile.flyway_migration_version_exists(alembic_version):
                    msg = (
                        f"A migration file for version {alembic_version}  " +
                        "already exists in the flyway migration file directory"
                    )
                    raise ExistingFlywayMigrationError(msg)
                LOGGER.info(
                    f"creating a flyway migraiton for {alembic_migration}")
                self.create_flyway_migration(alembic_migration)

    def create_flyway_migration(self, alembic_migration_file_path):
        """recieves an input alembic file and creates a corresponding flyway
        migration.

        :param alembic_migration_file_path: _description_
        :type alembic_migration_file_path: _type_
        """
        LOGGER.debug(f"alembic_migration_file_path: {alembic_migration_file_path}")
        # extract the previous and the current version from the migration
        # can get migrations either from the names of the files or by
        # running `alembic show <version>` example: `alembic show V1`
        #
        # run the alembic migration
        # alembic upgrade <prev ver>:<cur ver> --sql > <flyway migration file>
        alembic_version = self.path_utile.get_alembic_version_from_migration(
            alembic_migration_file_path
        )
        prev_alembic_version = \
            self.path_utile.get_previous_alembic_version_from_migration(
                alembic_migration_file_path
            )
        flyway_migration_file = self.path_utile.get_flyway_file_path(
            alembic_migration_file_path
        )
        # line =
        LOGGER.debug(f"{'-'*40}")
        LOGGER.debug(f"current alembic version: {alembic_version}")
        LOGGER.debug(f"previous alembic version: {prev_alembic_version}")
        LOGGER.debug(f"flyway_migration_file: {flyway_migration_file}")

        if not prev_alembic_version:
            # cli alembic migration command:
            # alembic upgrade <version> --sql > <flywayfile>
            alembic_args = alembic_version
        else:
            #  alembic upgrade <prevver>:<curver> --sql <flywayfile>
            alembic_args = prev_alembic_version + ":" + alembic_version
        self.alembic_to_flyway(alembic_args, flyway_migration_file)

    def alembic_to_flyway(self, input_alembic_args, output_flyway):
        """could call this through the alembic api, but not sure how to capture
        the stream

        :param inputAlembic: _description_
        :type inputAlembic: _type_
        :param output_flyway: _description_
        :type output_flyway: _type_
        """
        LOGGER.debug(f"output_flyway: {output_flyway}")
        if os.path.exists(output_flyway):
            # don't want to EVER overwrite a flyway script, if need to
            # overwrite one it should be deleted manually assuming that it
            # hasn't been run through the pipeline yet
            msg = (
                f"The input alembic file: {input_alembic_args} aligns " +
                "with the corresponding flyway migration file: " +
                f"{output_flyway}  which already exists!"
            )
            raise FileExistsError(msg)

        # first arg should be to the alembic config
        ini_file = self.path_utile.get_alembic_ini_file_path()
        config = alembic.config.Config(ini_file)
        LOGGER.debug(f"ini_file: {ini_file}")
        LOGGER.debug(f"input_alembic_args: {input_alembic_args}")
        entry_dir = os.getcwd()
        alembic_dir = self.path_utile.get_alembic_dir()
        os.chdir(alembic_dir)
        with open(output_flyway, "w") as write_stream:
            with contextlib.redirect_stdout(write_stream):
                command.upgrade(config=config, revision=input_alembic_args, sql=True)

        os.chdir(entry_dir)


class ExistingFlywayMigrationError(Exception):
    pass


if __name__ == "__main__":
    # simple logging config
    LOGGER = logging.getLogger()
    logLevel = logging.INFO
    LOGGER.setLevel(logLevel)
    hndlr = logging.StreamHandler()
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(lineno)d - %(message)s"
    )
    hndlr.setFormatter(formatter)
    LOGGER.addHandler(hndlr)
    LOGGER.debug("test")

    makeMigrate = CreateFlywayMigraions()
    makeMigrate.create_flyway_migrations()
