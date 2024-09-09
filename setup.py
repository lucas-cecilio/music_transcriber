from setuptools import find_packages
from setuptools import setup

with open("requirements.txt") as f:
    content = f.readlines()
requirements = [x.strip() for x in content if "git+" not in x]

setup(name='inference_model',
      version="1.7.8",
      description="Inference Model from Music Transcriber",
      install_requires=requirements,
      packages= ["music_transcriber"],
      include_package_data=True,
      zip_safe=False)

