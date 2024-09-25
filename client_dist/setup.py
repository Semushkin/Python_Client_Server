from setuptools import setup, find_packages

setup(name="messenger_123_clients",
      version="0.0.4",
      description="messenger_123_clients",
      author="Semushkin Anton",
      author_email="rkzton@yandex.ru",
      packages=find_packages(),
      install_requires=['PyQt5', 'sqlalchemy', 'pycryptodome', 'pycryptodomex']
      )