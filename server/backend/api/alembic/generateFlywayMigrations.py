"""
when deploying to AWS the FAM api will use flyway to run the migrations to
a RDS database
"""
import sys
import os


import logging
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