import fitz  # PyMuPDF
import json
from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq

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

# Function to filter and clean the extracted references
def clean_references(raw_references):
    cleaned_references = []
    unwanted_phrases = [
        "Here are the extracted references in the same format as the original document:",
        ""
    ]
    for reference in raw_references:
        if reference.strip() not in unwanted_phrases:
            cleaned_references.append(reference.strip())
    return cleaned_references

# Main execution
def main():
    # Path to the uploaded PDF file
    pdf_path = input("Enter the path to the PDF file: ")

    # Open the PDF to get the total number of pages
    pdf_document = fitz.open(pdf_path)
    total_pages = pdf_document.page_count
    print(f"The document has {total_pages} pages.")

    # User input for pages
    pages_input = input(f"Enter the pages where references are located (comma-separated, within range 1 to {total_pages}): ")
    pages = [int(x) - 1 for x in pages_input.split(',')]

    all_text = ""
    for page_num in pages:
        page = pdf_document.load_page(page_num)
        all_text += extract_text_from_page(page) + "\n"

    # Use Groq API to extract references from the combined text
    references = chain.invoke({"text": all_text})

    # Display the raw output for debugging purposes
    raw_references = references.content.strip().split("\n")
    print(f"Raw extracted references: {raw_references}")

    # Clean the references
    cleaned_references = clean_references(raw_references)

    # Prepare the result
    result = {
        "id": pdf_path.split("/")[-1],
        "references": cleaned_references
    }

    # Print the references in JSON format
    print(json.dumps(result, indent=4, ensure_ascii=False))

if __name__ == "__main__":
    main()
