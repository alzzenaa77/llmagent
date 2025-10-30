from setuptools import setup, find_packages

setup(
    name="llmagent",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        "discord.py>=2.0.0",
        "google-generativeai>=0.3.0",
        "python-dotenv>=0.19.0",
        "google-auth>=2.0.0",
        "google-auth-oauthlib>=0.5.0",
        "google-auth-httplib2>=0.1.0",
        "google-api-python-client>=2.0.0",
    ],
)