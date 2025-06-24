import os
import pandas as pd
from dotenv import load_dotenv
from openai import OpenAI
import PyPDF2

load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=api_key)

def read_companies_from_excel(filepath):
    df = pd.read_excel(filepath)
    return df['Company'].dropna().tolist()

def get_business_description(company_name):
    prompt = (
        f"Provide a detailed, professional business description of {company_name}. "
        f"Use the official investor relations page for {company_name}"
        "Include what the company does, its main lines of business, industries served, "
        "key products or services, major markets or regions, and any notable facts."
        "For each fact or claim, include a source as a hyperlink or parenthetical citation."
        "Use Recent sources, Don't use anything more than a few months old. "
    )
    response = client.responses.create(
        model="gpt-4o",
        input=prompt,
        tools=[{"type": "web_search_preview"}],
    )
    return response.output_text.strip()

def extract_pdf_text(filepath):
    with open(filepath, "rb") as f:
        reader = PyPDF2.PdfReader(f)
        text = ""
        for page in reader.pages:
            text += page.extract_text() or ""
        return text


def get_connection_paragraph(description, newsletter_text):
    prompt = (
        "Below is a business description, followed by the text of a market research newsletter. "
        "Write bullet points explaining if and how the business description connects to the newsletter's main themes. "
        "If there is no strong connection, briefly state so.\n\n"
        "Business Description:\n"
        f"{description}\n\n"
        "Newsletter:\n"
        f"{newsletter_text}\n\n"
        "Connection Paragraph:"
    )
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content.strip()

# Save both outputs to a Markdown file
def save_to_md(company_name, description, connection_paragraph):
    os.makedirs("descriptions", exist_ok=True)
    safe_name = "".join(c for c in company_name if c.isalnum() or c in " -_").rstrip()
    filename = f"descriptions/{safe_name}.md"
    with open(filename, "w", encoding="utf-8") as file:
        file.write(f"# {company_name}\n\n")
        file.write("## Business Description\n")
        file.write(description + "\n\n")
        file.write("## Connection to Market Research Newsletter\n")
        file.write(connection_paragraph + "\n")
    print(f"✅ Saved: {filename}")

# Main execution loop
if __name__ == "__main__":
    excel_path = "companies.xlsx"
    newsletter_path = os.path.join("market_research", "Letterdraft.pdf")

    try:
        companies = read_companies_from_excel(excel_path)
        newsletter_text = extract_pdf_text(newsletter_path)

        for company in companies:
            print(f"\n🔍 Processing: {company}")
            try:
                description = get_business_description(company)
                connection_paragraph = get_connection_paragraph(description, newsletter_text)
                save_to_md(company, description, connection_paragraph)
            except Exception as e:
                print(f"❌ Error processing {company}: {e}")
    except Exception as e:
        print(f"❌ Failed to read Excel or newsletter: {e}")
