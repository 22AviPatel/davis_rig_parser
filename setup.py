from setuptools import setup, find_packages

setup(
    name='davis_rig_parser',
    version='0.1.8',
    url='https://github.com/<your-github-username>/my_module',
    author='Avi Patel, Bradly Stone, Daniel Svedberg',
    author_email='avpnea@gmail.com, dan.ake.svedberg@gmail.com',
    description='Data parser for the Davis Rig',
    packages=find_packages(),    
    install_requires=[
    'numpy >= 1.18.5',
    'pandas >= 1.3.5',
    'easygui >= 0.98.1',
],
)
