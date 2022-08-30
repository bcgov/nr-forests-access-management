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
import logging
import os
import re

LOGGER = None

class CreateFlywayMigraions():
    def __init__(self):
        self.flywayDir = os.path.realpath(os.path.join(
            os.path.dirname(__file__),
            '..',
            '..',
            '..',
            'flyway',
            'sql'
        ))
        LOGGER.debug(self.flywayDir)

    def createFlywayMigrations(self):
        '''
        iterates through the list of migrations in the alembic directory
        if a corresponding migration for flyway doesn't exist it gets
        created
        '''
        alembicMigrations = self.getAlembicMigrationFile()
        for alembicMigration in alembicMigrations:
            if self.flywayMigrationExists(alembicMigration):
                self.createFlywayMigration(alembicMigration)

    def createFlywayMigration(self, alembicMigrationFilePath):
        # TODO: finish here
        LOGGER.debug(f"alembicMigrationFilePath: {alembicMigrationFilePath}")
        # extract the previous and the current version from the migration
        # can get migrations either from the names of the files or by
        # running `alembic show <version>` example: `alembic show V1`
        #
        # run the alembic migration
        # alembic upgrade <prev ver>:<cur ver> --sql > <flyway migration file>
        #



    def flywayMigrationExists(self, alembicMigrationFilePath):
        """returns a boolean indicating if a flyway migration exists that
        corresponds with the supplied alembic migration file

        :param alembicMigrationFilePath: _description_
        :type alembicMigrationFilePath: _type_
        """
        flywayFile = self.getFlywayFilePath(alembicMigrationFilePath)
        return os.path.exists(flywayFile)


    def getFlywayFilePath(self, alembicMigrationFilePath):
        """remove the .py extension
        add and extra _ character after the versions string
        add a .sql suffix
        append the flyway directory to the path

        :param alembicMigrationFilePath: _description_
        :type alembicMigrationFilePath: _type_
        """
        flywayFile = os.path.splitext(alembicMigrationFilePath)[0]
        loc = flywayFile.find('_')
        flywayFile = flywayFile[0:loc] + '_' + flywayFile[loc:] + '.sql'
        LOGGER.debug(f"flyway file: {flywayFile}")
        flywayFileWithPath = os.path.join(
            self.flywayDir,
            flywayFile
        )
        LOGGER.debug(f'flywayFileWithPath: {flywayFileWithPath}')
        return flywayFileWithPath

    def getAlembicMigrationFile(self):
        versionDir = self.getAlembicVersionDir()
        filesInVersionDir = os.listdir(versionDir)
        versionRegex = re.compile('^V\d+_.*')
        versionFiles = []
        for versionFile in filesInVersionDir:
            if versionRegex.match(versionFile):
                versionFiles.append(versionFile)
        print(f'versionFiles: {versionFiles}')
        return versionFiles


    def getAlembicVersionDir(self):
        return os.path.realpath(
            os.path.join(os.path.dirname(__file__), 'versions'))


if __name__ == '__main__':
    # simple logging config
    LOGGER = logging.getLogger()
    LOGGER.setLevel(logging.DEBUG)
    hndlr = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(lineno)d - %(message)s')
    hndlr.setFormatter(formatter)
    LOGGER.addHandler(hndlr)
    LOGGER.debug("test")



    makeMigrate = CreateFlywayMigraions()
    makeMigrate.createFlywayMigrations()
