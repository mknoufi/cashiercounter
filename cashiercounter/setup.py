from setuptools import setup, find_packages

setup(
    name='cashiercounter',
    version='0.0.1',
    description='Custom cashier module for ERPNext',
    author='Lavanya Emart',
    author_email='your@email.com',
    packages=find_packages(),
    zip_safe=False,
    include_package_data=True,
    install_requires=['frappe'],
)