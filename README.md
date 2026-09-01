# TeikoTechnical

##Summary 
This repository contains my Teiko technical examination submission, covering all parts detailed in the instructions.

I received the assignment late Friday evening and, due to unreliable internet access over the weekend, was only able to open it on Monday. As a result, the implementation was completed under a significantly compressed timeline. While I was able to complete the core functionality and required outputs, the limited time for final validation and refinement meant I was unable to test the pipeline as extensively as I would have liked. The dashboard, in particular, was completed with limited time for iteration and polish.

## Instructions to Reproduce Outputs 
1. Clones the repository and navigate to the project root: 
    git clone https://github.com/TaisiaK/TeikoTechnical.git
    cd TeikoTechnical
2. Install dependencies 
    run: make setup 
Installs the Python dependiencies in requirement.txt. The project was developed and tested using Python 3.9.9. For reproducibility, Python 3.9.9 is the recommended version. 
3.  Run the complete data pipeline 
    run: make pipeline 
This will load data, intialize database, preform analysis, and generate analysis outputs that are added stored in the outputs file. 
4. Launch the dashboard 
    run: make dashboard 
This starts the Streamlit dashboard locally. The link to the dashboard is: http://localhost:8501. 

## Releational Database Scheme and Rational 
The database is made up of three tables: subjects, samples, and cell_counts. This structure was chosen to separate subject-level information, sample-level information, and sample measurements. This decreases redundancy and provides flexibility as the data scales in the number of projects, samples, and cell populations measured. 

### Schema 
subjects 
CREATE TABLE subjects (
            subject_id TEXT PRIMARY KEY, 
            project TEXT NOT NULL, 
            condition TEXT NOT NULL, 
            age INTEGER NOT NULL, 
            sex TEXT NOT NULL,
            treatment TEXT NOT NULL,
            response TEXT);

This table stores information that describes an individual subject, including project, demographic, and treatment information. SQL query testing led to the assumption that each subject is associated with one project. Therefore, project information was stored at this level to avoid duplicating project information for all samples belonging to a subject. For similar reasons, treatment and response were stored at this level. 

Samples 
CREATE TABLE samples (
            sample_id TEXT PRIMARY KEY, 
            subject_id TEXT NOT NULL,  
            sample_type TEXT NOT NULL, 
            time_from_treatment_start INTEGER NOT NULL, 
            FOREIGN KEY (subject_id) REFERENCES  subjects(subject_id));

The samples table stores information specific to each biological sample. Unique sample_ids and references to subject_id are used to represent the one-to-many relationship between subjects and samples. Although SQL query testing showed that sample_type is consistent across all samples from an individual subject, it was stored at the sample level because it describes the biological sample rather than the subject. This also allows the schema to accommodate future datasets where a subject may contribute different sample types.

cell_counts
CREATE TABLE cell_counts (
            sample_id TEXT NOT NULL, 
            population TEXT NOT NULL, 
            count INTEGER NOT NULL, 
            PRIMARY KEY (sample_id, population), 
            FOREIGN KEY (sample_id) REFERENCES samples(sample_id));

This table stores cell-population measurements for each sample. Each population measurement is allocated to its own individual row. This design allows future projects to store new types of cell populations without restructuring the database. Similarly, if information is missing for some cell populations, the available measurements can still be uploaded without requiring empty columns or changes to the database schema.
 
### Scalability 
The schema scales by adding records rather than changing the database structure. This allows hundreds of projects and thousands of samples to be added without requiring new columns or changes to the existing tables. The row-based design of cell_counts also allows additional cell populations to be added as new rows rather than requiring the database schema to be modified.

As the database grows, indexes could be added to fields frequently used for filtering and joining, such as subjects.project, samples.subject_id, and cell_counts.population. This would allow queries to locate relevant records more efficiently rather than scanning entire tables. Indexes would be added selectively because they require additional storage and can increase the cost of inserting or updating records.

## Overview of Code Structure 

| Filename | Description |
| --- | --- | 
| 'load_data.py' | Initalizes database schema and loads all rows from cell-count.csv |
| 'analysis.py' | Preforms all analysis from parts 2, 3, and 4 exports the resulting tables and plots to the outputs folder. | 
| 'dashboard.py' | Creates the dashboard |
| Makefile	| Provides commands to set up dependencies, run the complete analysis pipeline, and launch the dashboard. |
| requirements.txt	| Lists the Python dependencies required to run the project. |
| cell-count.csv	| Source dataset used by the data-loading and analysis pipeline.|
| loblaw-database.db	| SQLite relational database containing the loaded data. | 
