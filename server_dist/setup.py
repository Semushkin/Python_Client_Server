from setuptools import setup, find_packages

setup(name="messenger_123_server",
      version="0.0.2",
      description="messenger_123_server",
      author="Semushkin Anton",
      author_email="rkzton@yandex.ru",
      packages=find_packages(),
      install_requires=['PyQt5', 'sqlalchemy', 'pycryptodome', 'pycryptodomex']
)