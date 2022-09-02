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
        self.migrationFilePrefix = "V"

    def getAlembicIniFilePath(self):
        alembicPath = os.path.realpath(
            os.path.join(os.path.dirname(__file__), "..", "alembic.ini")
        )
        return alembicPath

    def getAlembicDir(self):
        """gets the directory taht contains the alembic.ini... the directory
        from which alembic commands need to be run.

        :return: _description_
        :rtype: _type_
        """
        alembicDir = os.path.realpath(
            os.path.join(
                os.path.dirname(__file__), ".."))
        return alembicDir

    def getAlembicVersionFromMigration(self, alembicMigrationFilePath):
        fileName = os.path.basename(alembicMigrationFilePath)

        alembicVersion = fileName[: fileName.find("_")]
        LOGGER.debug(f"alembicVersion: {alembicVersion}")
        return alembicVersion

    def getFlywayFilePath(self, alembicMigrationFilePath):
        """remove the .py extension
        add and extra _ character after the versions string
        add a .sql suffix
        append the flyway directory to the path

        :param alembicMigrationFilePath: _description_
        :type alembicMigrationFilePath: _type_
        """
        flywayFile = os.path.splitext(alembicMigrationFilePath)[0]
        loc = flywayFile.find("_")
        flywayFile = flywayFile[0:loc] + "_" + flywayFile[loc:] + ".sql"
        flywayDir = self.getFlywayMigrationDirectory()
        LOGGER.debug(f"flyway file: {flywayFile}")
        flywayFileWithPath = os.path.join(flywayDir, flywayFile)
        LOGGER.debug(f"flywayFileWithPath: {flywayFileWithPath}")
        return flywayFileWithPath

    def getAlembicMigrationFile(self):
        """iterates through the files in the alembic version directory and
        returns a list of files that match the expected naming convension.

        :return: list of alembic version files
        :rtype: list
        """
        versionDir = self.getAlembicVersionDir()
        filesInVersionDir = os.listdir(versionDir)
        versionRegex = re.compile(f"^{self.migrationFilePrefix}\d+_.*") # noqa
        versionFiles = []
        for versionFile in filesInVersionDir:
            if versionRegex.match(versionFile):
                versionFiles.append(versionFile)
        print(f"versionFiles: {versionFiles}")
        return versionFiles

    def getPreviousAlembicVersionFromMigration(self, alembicMigrationFilePath):
        curVer = self.getAlembicVersionFromMigration(alembicMigrationFilePath)
        if curVer == f"{self.migrationFilePrefix}1":
            return None
        prevVerNum = int(curVer.replace(self.migrationFilePrefix, ""))
        prevVerNum -= 1
        prevVer = f"{self.migrationFilePrefix}{prevVerNum}"
        return prevVer

    def getAlembicVersionDir(self):
        """calculates the expected path to where the alembic migration version
        files should be located relative to the location of this file

        :return: path to the alembic version directory
        :rtype: str / path
        """
        return os.path.realpath(
            os.path.join(
                os.path.dirname(__file__), "versions"))

    def getFlywayMigrationDirectory(self):
        flywayDir = os.path.realpath(
            os.path.join(
                os.path.dirname(__file__),
                "..",
                "..",
                "..",
                "flyway",
                "sql")
        )
        return flywayDir

    def flywayMigrationExists(self, alembicMigrationFilePath):
        """returns a boolean indicating if a flyway migration exists that
        corresponds with the supplied alembic migration file

        :param alembicMigrationFilePath: _description_
        :type alembicMigrationFilePath: _type_
        """
        flywayFile = self.getFlywayFilePath(alembicMigrationFilePath)
        LOGGER.debug(f"flywayFile: {flywayFile}")
        return os.path.exists(flywayFile)


class CreateFlywayMigraions:
    def __init__(self):
        self.pathUtil = MigrationFilePaths()

    def createFlywayMigrations(self):
        """
        iterates through the list of migrations in the alembic directory
        if a corresponding migration for flyway doesn't exist calls methods to
        create it
        """
        alembicMigrations = self.pathUtil.getAlembicMigrationFile()
        for alembicMigration in alembicMigrations:
            if not self.pathUtil.flywayMigrationExists(alembicMigration):
                self.createFlywayMigration(alembicMigration)

    def createFlywayMigration(self, alembicMigrationFilePath):
        """recieves an input alembic file and creates a corresponding flyway
        migration.

        :param alembicMigrationFilePath: _description_
        :type alembicMigrationFilePath: _type_
        """
        LOGGER.debug(f"alembicMigrationFilePath: {alembicMigrationFilePath}")
        # extract the previous and the current version from the migration
        # can get migrations either from the names of the files or by
        # running `alembic show <version>` example: `alembic show V1`
        #
        # run the alembic migration
        # alembic upgrade <prev ver>:<cur ver> --sql > <flyway migration file>
        alembicVersion = self.pathUtil.getAlembicVersionFromMigration(
            alembicMigrationFilePath
        )
        prevAlembicVersion = \
            self.pathUtil.getPreviousAlembicVersionFromMigration(
                alembicMigrationFilePath
            )
        flywayMigrationFile = \
            self.pathUtil.getFlywayFilePath(alembicMigrationFilePath)
        # line =
        LOGGER.debug(f"{'-'*40}")
        LOGGER.debug(f"current alembic version: {alembicVersion}")
        LOGGER.debug(f"previous alembic version: {prevAlembicVersion}")
        LOGGER.debug(f"flywayMigrationFile: {flywayMigrationFile}")

        if not prevAlembicVersion:
            # cli alembic migration command:
            # alembic upgrade <version> --sql > <flywayfile>
            alembicArgs = alembicVersion
        else:
            #  alembic upgrade <prevver>:<curver> --sql <flywayfile>
            alembicArgs = prevAlembicVersion + ":" + alembicVersion
        self.alembic2Flyway(alembicArgs, flywayMigrationFile)

    def alembic2Flyway(self, inputAlembicArgs, outputFlyway):
        """could call this through the alembic api, but not sure how to capture
        the stream

        :param inputAlembic: _description_
        :type inputAlembic: _type_
        :param outputFlyway: _description_
        :type outputFlyway: _type_
        """
        LOGGER.debug(f"outputFlyway: {outputFlyway}")
        if os.path.exists(outputFlyway):
            # don't want to EVER overwrite a flyway script, if need to
            # overwrite one it should be deleted manually assuming that it
            # hasn't been run through the pipeline yet
            msg = f"The input alembic file: {inputAlembicArgs} aligns " + \
                  "with the corresponding flyway migration file: " + \
                  f"{outputFlyway}  which already exists!"
            raise FileExistsError(msg)

        # first arg should be to the alembic config
        iniFile = self.pathUtil.getAlembicIniFilePath()
        config = alembic.config.Config(iniFile)
        LOGGER.debug(f"iniFile: {iniFile}")
        LOGGER.debug(f"inputAlembicArgs: {inputAlembicArgs}")
        # alembic.config.main(argv=alembicArgs)
        # config.main(argv=alembicArgs)
        entryDir = os.getcwd()
        alembicDir = self.pathUtil.getAlembicDir()
        os.chdir(alembicDir)
        with open(outputFlyway, "w") as write_stream:
            with contextlib.redirect_stdout(write_stream):
                command.upgrade(
                    config=config,
                    revision=inputAlembicArgs,
                    sql=True)

        os.chdir(entryDir)


if __name__ == "__main__":
    # simple logging config
    LOGGER = logging.getLogger()
    LOGGER.setLevel(logging.DEBUG)
    hndlr = logging.StreamHandler()
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(lineno)d - %(message)s"
    )
    hndlr.setFormatter(formatter)
    LOGGER.addHandler(hndlr)
    LOGGER.debug("test")

    makeMigrate = CreateFlywayMigraions()
    makeMigrate.createFlywayMigrations()
