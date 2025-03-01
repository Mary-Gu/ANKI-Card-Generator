# ANKI_Card_Generator
An automatic tool that generates context-aware Q&amp;A pairs and ANKI fill-in-the-blank cards from input text using the qwen-turbo model.  

## Overview
This project is an automated tool that generates context-rich Q&A pairs and ANKI flashcards from provided input text. By leveraging the qwen-turbo model, it processes text files (e.g., `initial_input.txt`) and outputs question files and ANKI-ready CSV files to help users better grasp key concepts from the source material.  

## Features
- **Automatic Text Processing:** Splits long texts into manageable chunks for complete and accurate question generation.  
- **Context-Aware Q&A:** Produces Q&A pairs closely related to the original content for improved understanding.  
- **ANKI Card Generation:** Creates CSV-formatted fill-in-the-blank questions suitable for importing into ANKI.  
- **Customizable & Extendable:** Built on top of the qwen-turbo model and Aliyun API, making it easy to customize and extend.  

## Repository Structure  
anki-qa-generator/   
├── README.md # Project description and usage guide   
├── LICENSE # Open-source license (e.g., MIT)   
├── initial_input.txt # Sample input text file   
├── temp/ # Folder for generated output files (e.g., Question_Output.txt, Final_Output.txt)   
├── ANKI_Card_Generator.py # Main program source code      
└── requirements.txt # List of project dependencies  

## Installation & Usage

1. **Clone the Repository**
   ```bash
   git clone https://github.com/Mary-Gu/ANKI-Card-Generator.git
   cd ANKI-Card-Generator

2. **Configure the API Key**
In the code, locate the line API_KEY = "sk-xxxxxxxx" and replace it with your own API key.  
Alternatively, consider configuring the API key as an environment variable.  
