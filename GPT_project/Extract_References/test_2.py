import fitz  # PyMuPDF
import json
import os
import logging
import re
from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Initialize Groq Chat Model
chat = ChatGroq(
    temperature=0,
    model="llama3-70b-8192",
    api_key="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"
)

# Define the prompt for extracting references
system_prompt = "You are a helpful assistant that extracts references from provided text and returns them in the exact format they appear."
human_prompt_template = """
{text}
Extract the references from the text above and ensure they are in the same format as the original document. Do not include any introductory phrases or unrelated content. Only return the references.
"""

prompt = ChatPromptTemplate.from_messages([("system", system_prompt), ("human", human_prompt_template)])

chain = prompt | chat

# Function to extract text from a PDF page
def extract_text_from_page(page):
    text = page.get_text("text")
    return text

# Function to identify and extract the references section
def extract_references_section(text):
    # Look for common patterns that denote the start of the references section
    reference_section_patterns = [
        r"^references",  # "References" heading
        r"^bibliography",  # "Bibliography" heading
        r"^\[\d+\]",  # References starting with numbers in square brackets
        r"^\d+\.",  # References starting with numbers followed by a period
        r"^\[\d+\]:"  # References starting with numbers followed by a colon
    ]

    # Join all patterns into one combined regex
    combined_pattern = re.compile("|".join(reference_section_patterns), re.MULTILINE)

    # Find the first occurrence of the references section
    match = combined_pattern.search(text)
    if match:
        # Extract the text starting from the match to the end
        return text[match.start():].strip()
    return None

# Function to filter and clean the extracted references
def clean_references(raw_references):
    cleaned_references = []
    current_reference = ""

    # Define irrelevant phrases or sentences to be removed
    irrelevant_phrases = [
        "Here are the extracted references", "There are no references", "The text appears",
        "This is a self-contained passage", "The text does not contain any citations",
        "https://", "http://", "Please provide the text", "I'll be happy to extract the references for you",
        "There is no text above"
    ]

    for reference in raw_references:
        reference = reference.strip()

        # Check for irrelevant content
        if not any(phrase in reference for phrase in irrelevant_phrases) and len(reference) > 10 and any(
                char.isalpha() for char in reference):

            # Check if the line seems to start a new reference (often starts with a digit or reference number)
            if any(char.isdigit() for char in reference) and not reference.startswith("There is no"):
                if current_reference:
                    cleaned_references.append(current_reference.strip())
                current_reference = reference
            else:
                # Append to the current reference if it continues on a new line
                current_reference += " " + reference

    # Append the last reference if it exists
    if current_reference:
        cleaned_references.append(current_reference.strip())

    return cleaned_references

# Function to split text into manageable chunks
def split_text_into_chunks(text, max_chunk_size=2000):
    paragraphs = text.split('\n\n')
    chunks = []
    current_chunk = []

    for paragraph in paragraphs:
        current_chunk.append(paragraph)
        if len('\n\n'.join(current_chunk)) > max_chunk_size:
            chunks.append('\n\n'.join(current_chunk))
            current_chunk = []

    if current_chunk:
        chunks.append('\n\n'.join(current_chunk))

    return chunks

# Main function
def main():
    # Define the directory containing the PDF files
    pdf_directory = "D:/Innodata/GPT_project/Extract_References/sample-pdfs2"

    # Create the output directory if it doesn't exist
    output_dir = "out"
    os.makedirs(output_dir, exist_ok=True)

    # Iterate over all PDF files in the directory
    for pdf_file in os.listdir(pdf_directory):
        if pdf_file.endswith(".pdf"):
            pdf_path = os.path.join(pdf_directory, pdf_file)

            try:
                # Open the PDF to get the total number of pages
                pdf_document = fitz.open(pdf_path)
                total_pages = pdf_document.page_count
                logging.info(f"The document '{pdf_file}' has {total_pages} pages.")

                all_text = ""
                for page_num in range(total_pages):
                    page = pdf_document.load_page(page_num)
                    all_text += extract_text_from_page(page) + "\n"

                # Identify and extract the references section
                references_text = extract_references_section(all_text)
                if references_text:
                    # Split the references text into chunks
                    text_chunks = split_text_into_chunks(references_text)

                    # Use Groq API to extract references from each chunk
                    all_references = []
                    for chunk in text_chunks:
                        try:
                            references = chain.invoke({"text": chunk})
                            raw_references = references.content.strip().split("\n")
                            cleaned_references = clean_references(raw_references)
                            all_references.extend(cleaned_references)
                        except Exception as e:
                            logging.error(f"Error processing chunk: {e}")

                    # Prepare the result
                    result = {
                        "id": pdf_file,
                        "references": all_references
                    }

                    output_filename = f"{os.path.splitext(pdf_file)[0]}.json"
                    output_path = os.path.join(output_dir, output_filename)
                    with open(output_path, "w", encoding="utf-8") as output_file:
                        json.dump(result, output_file, indent=4, ensure_ascii=False)

                    logging.info(f"Saved extracted references to '{output_path}'")
                else:
                    logging.warning(f"No references section found in '{pdf_file}'")

            except FileNotFoundError:
                logging.error(f"File '{pdf_file}' not found.")
            except Exception as e:
                logging.error(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
