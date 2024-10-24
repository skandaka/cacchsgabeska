import re
from urllib.parse import urlparse


def extract_business_name(raw_name, url):
    # Remove common suffixes and clean up the name
    suffixes = ['Inc.', 'LLC', 'Ltd', 'Limited', 'Corp', 'Corporation', 'Co.', 'Company', 'Group']
    name = raw_name.split('|')[0].split('-')[0].strip()
    for suffix in suffixes:
        name = name.replace(suffix, '').strip()

    # Remove location information (usually after a comma or in parentheses)
    name = re.sub(r'\s*[\(\[].+?[\)\]]', '', name)
    name = name.split(',')[0].strip()

    # If the name is still too long or seems generic, try to extract from the URL
    if len(name.split()) > 3 or name.lower() in ['home', 'welcome', 'index']:
        domain = urlparse(url).netloc
        name = domain.split('.')[0]
        if name.lower() in ['www', 'web']:
            name = domain.split('.')[1]
        name = name.replace('-', ' ').title()

    return name


def generate_personalized_email(raw_business_name, url, extra_info):
    business_name = extract_business_name(raw_business_name, url)

    email_content = f"Hello {business_name} team,\n\n"

    email_content += "I hope this email finds you well. As a high school student passionate about web development, I'm reaching out with an exciting opportunity that I believe could benefit your business.\n\n"

    if extra_info.get('description'):
        email_content += f"I was particularly drawn to your focus on {extra_info['description'][:50]}... It aligns perfectly with the kind of projects I'm eager to work on. "

    email_content += f"I'm offering my web development services to {business_name} completely free of charge. My goal is to build my portfolio with real-world projects while providing value to businesses like yours.\n\n"

    if extra_info.get('keywords'):
        keywords = extra_info['keywords'].split(',')[:3]
        email_content += f"I noticed that {', '.join(keywords)} are key aspects of your business. I'm confident I can create a website that effectively showcases these strengths. "

    email_content += "Here's what I'm proposing:\n\n"
    email_content += "1. I'll create a sample redesign of one page from your current website, free of charge.\n"
    email_content += "2. If you like what you see, we can discuss redesigning more pages or even your entire website.\n"
    email_content += "3. This is all at no cost to you - my payment is the experience and the ability to showcase the work in my portfolio.\n\n"

    if 'social_media' in extra_info:
        email_content += "I've also taken a look at your social media presence and see great potential for enhancing your online engagement across platforms. "

    if 'contact_page' in extra_info:
        email_content += "I appreciate the clear communication channels you've set up on your contact page. It shows you value open dialogue, which is something I strongly believe in as well.\n\n"

    email_content += f"""Here's a brief overview of what I can offer {business_name}:

1. Responsive web design to ensure your site looks great on all devices
2. Modern, user-friendly interfaces to enhance visitor engagement
3. Performance optimization to improve loading speeds and user experience
4. Integration of the latest web technologies to keep you ahead of the curve

I understand that I'm younger than your typical web developer, but I'm incredibly motivated to learn and grow. I'm confident that my fresh perspective, combined with my technical skills, could bring a unique value to your online presence.

Would you be interested in seeing a sample redesign of one of your web pages? If so, I'd be happy to get started right away. There's no obligation to continue beyond this initial sample - it's simply an opportunity for you to see what I can do.

Thank you for considering this opportunity. I'm really looking forward to the possibility of working with {business_name} and contributing to your online success.

Best regards,
Skanda Athreya

P.S. You can view some of my previous projects at skandaa.me, or reach me directly at 847-877-2340 if you'd like to discuss further.
"""

    return email_content.strip()


if __name__ == "__main__":
    # Test the email generator
    test_business_name = "Acme Corporation - New York Branch | Home"
    test_url = "https://www.acmecorp.com"
    test_extra_info = {
        "description": "Leading provider of innovative solutions",
        "keywords": "technology,innovation,customer service",
        "social_media": ["https://www.facebook.com/acmecorp", "https://www.linkedin.com/company/acmecorp"],
        "contact_page": "/contact-us"
    }
    print(generate_personalized_email(test_business_name, test_url, test_extra_info))