import openai
import os
from dotenv import load_dotenv
from sqlalchemy.orm import Session
from . import models
import logging

load_dotenv()

openai.api_key = os.getenv("OPENAI_API_KEY")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def get_faq_response(db: Session, question: str):
    faq = db.query(models.FAQ).filter(
        models.FAQ.question.ilike(f"%{question}%")).first()
    if faq:
        logger.info(f"FAQ match found for question: {question}")
        return faq.answer
    return None


def get_ai_response(question: str):
    try:
        logger.debug(
            f"Sending request to OpenAI API with question: {question}")
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": question}
            ],
            max_tokens=150,
            n=1,
            temperature=0.7,
        )
        logger.debug(f"Received response from OpenAI API: {response}")
        return response.choices[0].message['content'].strip()
    except openai.error.AuthenticationError:
        logger.error("Invalid OpenAI API key. Please check your .env file.")
        return "API authentication failed. Please check the server logs."
    except openai.error.RateLimitError:
        logger.error("OpenAI API rate limit exceeded.")
        return "Rate limit exceeded. Please wait and try again later."
    except openai.error.OpenAIError as e:
        logger.error(f"OpenAI API error: {str(e)}")
        return f"OpenAI error: {str(e)}"
    except Exception as e:
        logger.error(
            f"Unexpected error in get_ai_response: {str(e)}", exc_info=True)
        return "Unexpected server error. Please try again later."


def get_chatbot_response(db: Session, question: str):
    try:
        faq_response = get_faq_response(db, question)
        if faq_response:
            return faq_response
        return get_ai_response(question)
    except Exception as e:
        logger.error(f"Error in get_chatbot_response: {str(e)}", exc_info=True)
        return "I'm sorry, but an error occurred while processing your request. Please try again later."
