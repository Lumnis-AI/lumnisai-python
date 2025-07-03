"""
Structured Output Examples for Lumnis SDK

This example shows how to get AI responses in structured JSON format
using Pydantic models. Perfect for building APIs, extracting data,
or integrating with other systems.
"""

import asyncio
from typing import List, Optional

from pydantic import BaseModel, Field

import lumnisai


# Example 1: Simple data extraction
class ProductInfo(BaseModel):
    name: str = Field(description="Product name")
    price: float = Field(description="Price in USD")
    features: List[str] = Field(description="Key features")
    in_stock: bool = Field(description="Availability")


# Example 2: Nested structures
class Address(BaseModel):
    street: str
    city: str
    state: Optional[str] = None
    country: str
    postal_code: Optional[str] = None


class Company(BaseModel):
    name: str = Field(description="Company name")
    industry: str = Field(description="Industry/sector")
    founded: int = Field(description="Year founded")
    headquarters: Address
    employee_count: Optional[str] = None
    website: Optional[str] = None


# Example 3: Analysis output
class SentimentAnalysis(BaseModel):
    sentiment: str = Field(description="Overall sentiment: positive, negative, or neutral")
    score: float = Field(description="Confidence score between 0 and 1", ge=0, le=1)
    key_phrases: List[str] = Field(description="Important phrases from the text")
    summary: str = Field(description="Brief summary of the content")


def product_extraction_example():
    """Extract product information from natural language."""
    client = lumnisai.Client()
    
    response = client.invoke(
        "Tell me about the MacBook Pro 16-inch with M3 Max chip",
        response_format=ProductInfo,
        user_id="user-123"
    )
    
    if response.structured_response:
        product = ProductInfo(**response.structured_response)
        print(f"\n{product.name}")
        print(f"Price: ${product.price:,.2f}")
        print(f"In Stock: {'Yes' if product.in_stock else 'No'}")
        print(f"Features: {', '.join(product.features[:3])}...")


def company_info_example():
    """Extract detailed company information with nested data."""
    client = lumnisai.Client()
    
    response = client.invoke(
        "Tell me about SpaceX including their headquarters location",
        response_format=Company,
        response_format_instructions="Include the full address with street, city, state, and country",
        user_id="user-123"
    )
    
    if response.structured_response:
        company = Company(**response.structured_response)
        print(f"\n{company.name}")
        print(f"Industry: {company.industry}")
        print(f"Founded: {company.founded}")
        print(f"Headquarters: {company.headquarters.street}")
        print(f"             {company.headquarters.city}, {company.headquarters.state} {company.headquarters.postal_code}")
        print(f"             {company.headquarters.country}")


def sentiment_analysis_example():
    """Analyze sentiment and extract key information from text."""
    client = lumnisai.Client()
    
    customer_review = """
    I recently purchased this laptop and I'm extremely happy with it!
    The performance is outstanding, the battery life is incredible,
    and the display is gorgeous. The only minor issue is that it
    runs a bit warm under heavy load, but that's expected with this
    much power. Definitely recommend!
    """
    
    response = client.invoke(
        f"Analyze this customer review: {customer_review}",
        response_format=SentimentAnalysis,
        user_id="user-123"
    )
    
    if response.structured_response:
        analysis = SentimentAnalysis(**response.structured_response)
        print(f"\nSentiment: {analysis.sentiment.upper()} (confidence: {analysis.score:.2%})")
        print(f"Key phrases: {', '.join(analysis.key_phrases)}")
        print(f"Summary: {analysis.summary}")


async def async_batch_processing():
    """Process multiple items concurrently with structured output."""
    async with lumnisai.AsyncClient() as client:
        products = [
            "iPhone 15 Pro Max",
            "Samsung Galaxy S24 Ultra", 
            "Google Pixel 8 Pro"
        ]
        
        # Process all products concurrently
        tasks = [
            client.invoke(
                f"Tell me about {product}",
                response_format=ProductInfo,
                user_id="user-123"
            )
            for product in products
        ]
        
        responses = await asyncio.gather(*tasks)
        
        print("\n📱 Product Comparison:")
        for response in responses:
            if response.structured_response:
                product = ProductInfo(**response.structured_response)
                print(f"\n{product.name}: ${product.price:,.2f}")
                print(f"  Features: {', '.join(product.features[:2])}...")


def json_schema_example():
    """Using raw JSON schema instead of Pydantic models."""
    client = lumnisai.Client()
    
    # Define schema directly (useful when you don't want to create models)
    task_schema = {
        "type": "object",
        "properties": {
            "tasks": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "title": {"type": "string"},
                        "priority": {"type": "string", "enum": ["high", "medium", "low"]},
                        "estimated_hours": {"type": "number"}
                    },
                    "required": ["title", "priority", "estimated_hours"]
                }
            },
            "total_hours": {"type": "number"},
            "deadline": {"type": "string"}
        },
        "required": ["tasks", "total_hours"]
    }
    
    response = client.invoke(
        "Break down the project 'Build a mobile app' into 5 main tasks",
        response_format=task_schema,
        response_format_instructions="Set realistic time estimates in hours",
        user_id="user-123"
    )
    
    if response.structured_response:
        data = response.structured_response
        print(f"\n📋 Project Breakdown ({data['total_hours']} hours total)")
        for task in data['tasks']:
            print(f"  • {task['title']} ({task['priority']}) - {task['estimated_hours']}h")


def error_handling_example():
    """Robust error handling for production use."""
    from pydantic import ValidationError
    
    client = lumnisai.Client()
    
    try:
        response = client.invoke(
            "Analyze the market performance of Apple stock",
            response_format={
                "type": "object",
                "properties": {
                    "symbol": {"type": "string"},
                    "current_price": {"type": "number"},
                    "change_percent": {"type": "number"},
                    "recommendation": {"type": "string", "enum": ["buy", "hold", "sell"]},
                    "analysis": {"type": "string"}
                },
                "required": ["symbol", "current_price", "recommendation", "analysis"]
            },
            user_id="user-123"
        )
        
        # Always check both responses
        if response.structured_response:
            data = response.structured_response
            print(f"\n📊 {data['symbol']} Analysis")
            print(f"Price: ${data['current_price']:.2f}")
            if 'change_percent' in data:
                print(f"Change: {data['change_percent']:+.2f}%")
            print(f"Recommendation: {data['recommendation'].upper()}")
            print(f"Analysis: {data['analysis']}")
        else:
            # Fallback to text response
            print(f"Analysis: {response.output_text}")
            
    except ValidationError as e:
        print(f"Data validation error: {e}")
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    print("🚀 Lumnis SDK - Structured Output Examples\n")
    
    print("1️⃣ Product Information Extraction")
    product_extraction_example()
    
    print("\n2️⃣ Company Information with Nested Data")
    company_info_example()
    
    print("\n3️⃣ Sentiment Analysis")
    sentiment_analysis_example()
    
    print("\n4️⃣ Using JSON Schema Directly")
    json_schema_example()
    
    print("\n5️⃣ Async Batch Processing")
    asyncio.run(async_batch_processing())
    
    print("\n6️⃣ Error Handling")
    error_handling_example()
    
    print("\n✅ All examples completed!")