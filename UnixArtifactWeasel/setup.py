from setuptools import setup

setup(
   name='Unix Forensic Weasel',
   version='1.0.alpha',
   description='An artifact collection tool for forensics of Unix systems',
   license="MIT",
   long_description='The purpose of Unix Artifact Hoarder is to perform artifact collection on Unix systems, allowing'
                    'forensic security analysts to review the artifacts and determine the integrity of the system. The '
                    'tool is designed to be used in the intrusion detection/response process, where beyond assessing'
                    ' the integrity of a system, it can give insight into the scope or method of exploitation.',
   author='Yoji Watanabe',
   author_email='yoji.watanabe@tufts.edu',
   url="https://github.com/yojiwatanabe/UnixArtifactHoarder",
   packages=['Unix Forensic Weasel'],
   install_requires=[],
)
