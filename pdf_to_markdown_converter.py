import os
import fitz  # PyMuPDF
import sys

def convert_pdf_to_markdown(pdf_path, md_path):
    """
    Reads text from a PDF file using PyMuPDF and saves it to a Markdown file.
    """
    print(f"Processing {pdf_path}...")
    try:
        # Open the PDF file with PyMuPDF
        doc = fitz.open(pdf_path)

        # Check if the file is a valid PDF and can be opened
        if not doc.is_pdf:
            print(f"Warning: {pdf_path} is not a valid PDF file. Skipping.")
            return

        # Check for encryption
        if doc.is_encrypted:
            # Try to authenticate with an empty password. If it fails, skip the file.
            if not doc.authenticate(''):
                print(f"Warning: {pdf_path} is encrypted and cannot be opened. Skipping.")
                doc.close()
                return
            print(f"Info: Decrypted {pdf_path} with an empty password.")

        text = ""
        for i, page in enumerate(doc):
            try:
                # Extract text from the page
                page_text = page.get_text("text")
                print(f"Page {i + 1} text: {page_text}")

                if page_text:
                    text += page_text
            except Exception as page_e:
                print(f"Could not extract text from page {i + 1} in {pdf_path}: {page_e}", file=sys.stderr)

        doc.close()

        if not text.strip():
            print(f"Warning: No text extracted from {pdf_path}. It might be an image-based PDF.")
            return

        # Write the extracted text to a Markdown file
        with open(md_path, 'w', encoding='utf-8') as md_file:
            md_file.write(text)

        print(f"Successfully converted {pdf_path} to {md_path}")

    except Exception as e:
        print(f"An unexpected error occurred while converting {pdf_path}: {e}", file=sys.stderr)

def main():
    """
    Main function to find PDFs in a directory and convert them to Markdown.
    """
    directory = input("Enter the path to the folder containing PDF files (press Enter for current directory): ") or '.'

    if not os.path.isdir(directory):
        print(f"Error: The directory '{directory}' does not exist.", file=sys.stderr)
        return

    print(f"Searching for PDF files in '{directory}'...")
    pdf_files_found = False
    for filename in os.listdir(directory):
        if filename.lower().endswith('.pdf'):
            pdf_files_found = True
            pdf_path = os.path.join(directory, filename)
            md_filename = os.path.splitext(filename)[0] + '.md'
            md_path = os.path.join(directory, md_filename)

            convert_pdf_to_markdown(pdf_path, md_path)

    if not pdf_files_found:
        print("No PDF files found in the specified directory.")



if __name__ == "__main__":
    main()

            
