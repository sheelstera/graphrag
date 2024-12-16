import random
import uuid
from faker import Faker
import json
import re

faker = Faker()

def sanitize_variable_name(name):
    """
    Sanitizes a string to be used as a valid JSON key name.
    Replaces spaces, commas, slashes, and other special characters with underscores.
    """
    return re.sub(r'[^\w]', '_', name)

def generate_customer_360_json(n):
    customer_360_data = []
    created_demographics = {}
    created_psychographics = {}
    created_social_media = {}

    for customer_idx in range(1, n + 1):  
        customer_data = {}
        customer_id = str(uuid.uuid4())
        customer_name = faker.name()
        email = faker.email()
        phone = faker.phone_number()
        age = random.randint(18, 75)
        gender = random.choice(["Male", "Female", "Non-Binary", "Other"])
        country = faker.country()
        city = faker.city()
        income = random.randint(30000, 200000)
        customer_segment = random.choice(["Premium", "Mid-Tier", "Budget"])
        personality = random.choice(["Analytical", "Amiable", "Expressive", "Driver"])

        # Customer basic details
        customer_data["Customer"] = {
            "customer_id": customer_id,
            "name": customer_name,
            "email": email,
            "phone": phone,
            "age": age,
            "gender": gender,
            "country": country,
            "city": city,
            "income": income,
            "segment": customer_segment,
            "personality": personality
        }

        # Demographic Attributes
        demographics = {
            'marital_status': random.choice(["Single", "Married", "Divorced", "Widowed"]),
            'education': random.choice(["High School", "Bachelors", "Masters", "Doctorate"]),
            'occupation': faker.job(),
            'age_group': f"{(age // 10) * 10}s"  # E.g., '30s', '40s'
        }

        customer_data["Demographics"] = demographics

        # Psychographic Attributes
        hobbies = [faker.word() for _ in range(random.randint(1, 3))]
        values = random.choice(["Environment", "Health", "Wealth", "Adventure"])
        lifestyle = random.choice(["Active", "Sedentary", "Balanced"])

        psychographics = {
            'hobbies': hobbies,
            'values': values,
            'lifestyle': lifestyle
        }

        customer_data["Psychographics"] = psychographics

        # Social Media Platforms
        platform = random.choice(["Facebook", "Twitter", "Instagram", "LinkedIn"])
        posts = random.randint(10, 100)
        followers = random.randint(100, 5000)

        social_media = {
            "platform": platform,
            "posts": posts,
            "followers": followers
        }

        customer_data["SocialMedia"] = social_media

        customer_360_data.append(customer_data)

    return customer_360_data

n_customers = int(input("Enter the number of customers to generate: "))
customer_360_json = generate_customer_360_json(n_customers)

output_file = "customer_360_data.json"
with open(output_file, "w") as file:
    json.dump(customer_360_json, file, indent=4)

print(f"JSON data for {n_customers} customers written to {output_file}.")
