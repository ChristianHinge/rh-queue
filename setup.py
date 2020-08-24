from setuptools import setup, find_packages
setup(name="rh-queue",
        version="0.4",
        description="rh queue system for queueing scripts",
        author="Peter McDaniel",
        author_email="peter.nicolas.castenschiold.mcdaniel@regionh.dk",
       scripts=["bin/rhqueue", "bin/rhqemail"],
       packages=find_packages(),
       package_data={"emails": ["emails/templates/*.tmp"]},
       include_package_data=True
       )
