# Akano Builder

This project, Akano Builder, is a Python script that generates detailed character profiles in Markdown format. It uses a `characters.csv` file as the main input and several other Markdown files as data libraries for different character attributes like origins, specializations, and more.

## How to use

1.  **Prepare the input files**:
    *   Make sure you have the following files in the `inputs` directory:
        *   `characters.csv`: This file should contain the list of characters with their attributes.
        *   `cores.md`: Contains the core information about the characters.
        *   `origins.md`: Contains the origin stories.
        *   `circles.md`: Contains information about the character's circles.
        *   `units.md`: Contains information about the character's units.
        *   `specializations.md`: Contains information about the character's specializations.

2.  **Run the script**:
    *   Execute the `generator.py` script from your terminal:
        ```bash
        python generator.py
        ```

3.  **Find the output**:
    *   The generated Markdown files for each character will be saved in the `output` directory.

## Prompts

Here are some prompts you can use with Gemini to interact with this project:

*   "Can you add a new character to the `characters.csv` file? The character's name is 'Lia', and she is a 'mage' from the 'Northern Kingdom'."
*   "Please, read the `development-specs` file and refactor the `generator.py` file to include a new feature."
