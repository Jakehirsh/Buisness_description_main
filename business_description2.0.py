
import os
import pandas as pd
import csv
import streamlit as st
from dotenv import load_dotenv
from openai import OpenAI
import PyPDF2

# Load API key
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=api_key)

def read_companies_from_excel(uploaded_file):
    df = pd.read_excel(uploaded_file)
    return df['Company'].dropna().tolist()

def extract_pdf_text(uploaded_pdf):
    reader = PyPDF2.PdfReader(uploaded_pdf)
    text = ""
    for page in reader.pages:
        text += page.extract_text() or ""
    return text

def get_business_description(company_name):
    prompt = (
        f"Provide a detailed, professional business description of {company_name}. "
        f"Use the official investor relations page for {company_name}. "
        "Include what the company does, its main lines of business, industries served, "
        "key products or services, major markets or regions, and any notable facts. "
        "For each fact or claim, include a source as a hyperlink or parenthetical citation. "
        "Use recent sources. Don't use anything more than a few months old."
    )
    response = client.responses.create(
        model="gpt-4o",
        input=prompt,
        tools=[{"type": "web_search_preview"}],
    )
    return response.output_text.strip()

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

def save_to_csv(results, output_path="descriptions.csv"):
    fieldnames = ["Company", "Description", "Connection Notes"]
    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in results:
            writer.writerow(row)

def main():
    st.title("Business Descriptions with Newsletter Analysis")

    uploaded_excel = st.file_uploader("Upload Excel File with Company Names", type=["xlsx"])
    uploaded_pdf = st.file_uploader("Upload Market Research PDF", type=["pdf"])

    if uploaded_excel and uploaded_pdf and st.button("Generate Descriptions"):
        with st.spinner("Reading and processing files..."):
            companies = read_companies_from_excel(uploaded_excel)
            newsletter_text = extract_pdf_text(uploaded_pdf)
            results = []

            for company in companies:
                st.write(f"🔍 Processing: **{company}**")
                try:
                    description = get_business_description(company)
                    connection_paragraph = get_connection_paragraph(description, newsletter_text)
                    results.append({
                        "Company": company,
                        "Description": description,
                        "Connection Notes": connection_paragraph
                    })
                except Exception as e:
                    st.error(f"❌ Error processing {company}: {e}")

            if results:
                save_to_csv(results)
                st.success("✅ Results saved to descriptions.csv")
                st.dataframe(pd.DataFrame(results))

                with open("descriptions.csv", "rb") as f:
                    st.download_button("Download CSV", f, file_name="descriptions.csv")

if __name__ == "__main__":
    main()
