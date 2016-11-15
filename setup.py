from setuptools import setup

setup(name="Robotics",
    version="1.0",
    description="A Robotics Library",
    author="Lucas Fink, Quinn Parrott",
    url="github.com/lf-/robotics",
    packages=["robotics"],
    entry_points={
        'console_scripts': [
            'robotctl = robotics.cli:main',
            'robotd = robotics.jsonapi:main'
        ]
    }
)

