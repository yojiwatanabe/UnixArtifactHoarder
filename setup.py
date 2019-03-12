from setuptools import setup

setup(
   name='Unix Artifact Weasel',
   version='1.0',
   description='An artifact collection tool for forensics of Unix systems',
   license="MIT",
   long_description='The purpose of Unix Artifact Weasel is to perform artifact collection on Unix systems, allowing'
                    'forensic security analysts to review the artifacts and determine the integrity of the system. The '
                    'tool is designed to be used in the intrusion detection/response process, where beyond assessing'
                    ' the integrity of a system, it can give insight into the scope or method of exploitation.',
   author='Yoji Watanabe',
   author_email='yoji.watanabe@tufts.edu',
   url="https://github.com/yojiwatanabe/UnixArtifactWeasel",
   packages=['UnixArtifactWeasel'],
   install_requires=[],
)
