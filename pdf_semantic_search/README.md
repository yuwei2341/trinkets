# Semantic PDF Search App

This web application allows users to perform semantic searches across multiple PDF files. Built using Flask, Hugging Face Transformers, and FAISS, the app provides a streamlined way to upload, index, and search PDFs by their content.

---

## Features

- **Upload PDFs**: Upload and index PDF files. Extracted text is stored and embeddings are generated for semantic search.
- **Semantic Search**: Use advanced embeddings to search PDFs by meaning rather than keywords.
- **Dynamic Indexing**: Supports adding and replacing PDFs without restarting the app.
- **Multi-PDF Search**: Search within selected PDFs or across all indexed files.
- **Scalable Backend**: Utilizes a pretrained model from Hugging Face for multilingual semantic understanding.

---

## Caveat
The primary purpose is to search in OneNote-converted PDFs. Therefore,
- it only supports non-image PDF, and
- certain optimization is made toward such PDFs, e.g. removing bullet points

---

## Installation

### Prerequisites

1. **Python**: Ensure Python 3.8 or higher is installed.
2. **Dependencies**: Install the required Python libraries:
   ```bash
   pip install -r requirements.txt
3. **GPU Support (Optional)**: If using a GPU, ensure CUDA is properly installed and available for PyTorch.

### Setting Up the Project
1. Clone the repository:
    ```bash
    git clone https://github.com/username/semantic-pdf-search.git
    cd semantic-pdf-search
2. Create the required directories:
    ```bash
    mkdir -p uploads extracted_data data/pdf_files
3. Set up the pretrained model: The app uses the `Alibaba-NLP/gte-multilingual-base` model. It will be automatically downloaded on the first run.
4. Start the Flask server:
    ```bash 
    python app.py
5. Visit the application in your browser at http://127.0.0.1:5000.

## Usage

### Upload PDFs

1. Go to the home page of the app in your browser.
2. Click the "Upload PDFs" button and select one or more PDF files to upload.
3. The app will process the uploaded files by extracting their text and generating embeddings. These embeddings will be used for semantic searches.

### Perform a Search

1. Enter a search query in the search box.
2. (Optional) Select specific PDFs to limit the search to certain files. If no files are selected, the search will include all indexed PDFs.
3. View the search results ranked by semantic similarity. Each result includes:
   - The PDF file name.
   - The text snippet containing the match.
   - The page number in the PDF.
   - The similarity score.

### Replace an Existing PDF

1. If you upload a file with the same name as an already uploaded PDF, the app will prompt you for confirmation.
2. Choose "Yes" to replace the existing file or "No" to keep the current version.

---

## Folder Structure

The application organizes files and data into the following directories:

- **`uploads`**: Temporary storage for files uploaded during the current session.
- **`data/pdf_files`**: Permanent storage for the uploaded PDF files.
- **`extracted_data`**: Stores text and embeddings extracted from PDFs for semantic search.
- **`app.log`**: Log file for monitoring application events and debugging issues.

---

## Technologies Used

- **Flask**: A lightweight Python web framework for building the application.
- **Hugging Face Transformers**: Used for generating multilingual semantic embeddings.
- **FAISS**: A library for efficient similarity search and clustering.
- **PyTorch**: Supports the embedding model for semantic understanding.

---

## Configuration

The application’s behavior can be adjusted by modifying the following parameters in `app.py`:

| Parameter                 | Default Value                     | Description                                  |
|---------------------------|-----------------------------------|----------------------------------------------|
| `UPLOAD_FOLDER`           | `'uploads'`                      | Folder for temporarily storing uploaded files. |
| `EXTRACTED_DATA_FOLDER`   | `'extracted_data'`               | Directory to save text and embeddings.      |
| `PDF_DIRECTORY`           | `'data/pdf_files'`               | Directory for storing uploaded PDF files.   |
| `MODEL_CKPT`              | `'Alibaba-NLP/gte-multilingual-base'` | Pretrained model checkpoint for embeddings. |
| `K_NEIGHBORS`             | `5`                              | Number of search results to return.         |

To use a GPU, ensure CUDA is properly set up, and the device will be automatically detected.

---

## Logging

The application logs events and errors in the `app.log` file. To change the logging level, modify the `logging.basicConfig` settings in `app.py`.

---

## Future Enhancements

- **User Management**: Add user authentication for secure access.
- **Text Summarization**: Integrate features to summarize search results.
- **Better Storage**: Store PDFs and embeddings in a database
- **Enhanced UI**: Improve the user interface for a more intuitive experience.
