#imports
import asyncio
import aiohttp
import os
import google.generativeai as genai

from dotenv import load_dotenv
from tqdm.asyncio import tqdm

import queryDB



load_dotenv() #import environment variables 



def message_generator(company_name, overview, industry, employees, query):
    
    genai.configure(api_key=os.getenv('GEMINI_API_KEY'))

    model = genai.GenerativeModel("gemini-2.5-flash")
    response = model.generate_content(f"Create a cold outreach message to another company with this description: \"{query}\". You have the following info about the company being reached out to. Company name: {company_name}, industry: {industry}, no. employees: {employees}, company description: \"{overview}\".")

    return response.text




async def send_outreach_email(to_email, subject, user_email, message):

    async with aiohttp.ClientSession() as session:
        url = "http://localhost:5001/api/send-email"
        
        payload = {
            "to": to_email,
            "subject": subject,
            "body": message
        }
        
        if user_email:
            payload["user_email"] = user_email
        
        try:
            async with session.post(url, json=payload) as response:
                result = await response.json()
                
                if response.status == 200:
                    return {"success": True, "data": result}
                else:
                    return {"success": False, "error": result.get("error", "Unknown error")}
                    
        except Exception as e:
            return {"success": False, "error": str(e)}
        