from setuptools import setup, find_packages

setup(
    name='json_schema_generator',
    version='0.0.4',
    packages=find_packages(exclude=['tests']),
    url='https://github.com/OndraTom/JsonSchemaGenerator',
    license='https://opensource.org/licenses/MIT',
    author='Ondrej Tom',
    author_email='odis@meiro.io',
    description='JSON schema generator'
)
