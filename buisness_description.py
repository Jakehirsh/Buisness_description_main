import os
from dotenv import load_dotenv
from openai import OpenAI

# Load API key from .env file
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=api_key)

# Ask OpenAI to describe a business
def get_business_description(company_name):
    prompt = (
        f"Provide a detailed, professional business description of {company_name}. "
        "Include what the company does, its main lines of business, industries served, "
        "key products or services, major markets or regions, and any notable facts."
    )
    response = client.responses.create(
        model="gpt-4.1",
        input=prompt,
        tools=[{"type": "web_search_preview"}],
    )
    return response.output_text.strip()


def save_to_md(company_name, description):
    # Make sure the "descriptions" folder exists
    if not os.path.exists("descriptions"):
        os.mkdir("descriptions")

    
    safe_name = company_name.replace(" ", "_").replace("/", "_")
    filename = "descriptions/" + safe_name + ".md"

    
    with open(filename, "w") as file:
        file.write("# " + company_name + "\n\n")
        file.write(description)

    print("Saved to", filename)


if __name__ == "__main__":
    company = input("Enter the company name: ")
    description = get_business_description(company)
    print(f"\nBusiness Description for {company}:\n{description}\n")
    save_to_md(company, description)
