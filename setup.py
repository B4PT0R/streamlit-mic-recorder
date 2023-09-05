from pathlib import Path

import setuptools

this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

setuptools.setup(
    name="streamlit-mic-recorder",
    version="0.0.1",
    author="Baptiste Ferrand",
    author_email="bferrand.math@gmail.com",
    description="Streamlit component that allows to record mono audio from the user's microphone, and/or perform speech recognition directly.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="",
    packages=setuptools.find_packages(),
    include_package_data=True,
    classifiers=[],
    python_requires=">=3.7",
    install_requires=[
        "streamlit >= 0.63",
        "SpeechRecognition"
    ],
)
