import google.generativeai as genai

genai.configure(api_key="AIzaSyC_SZPN-cpkm4e1KoIRlVcRLhgbrQv7s18")

model = genai.GenerativeModel("gemini-2.5-flash")
response = model.generate_content("Explain how AI works in a few words")

print(response.text)