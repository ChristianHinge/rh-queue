from distutils.core import setup

setup(name="rh-queue",
        version="0.1",
        description="rh queue system for queueing scripts",
        author="Peter McDaniel",
        author_email="peter.nicolas.castenschiold.mcdaniel@regionh.dk",
       scripts=["bin/rhqueue"],
       packages=["rhqueue"]
       )
