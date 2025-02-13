from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from . import models, schemas, chatbot
from .database import engine, get_db
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

try:
    models.Base.metadata.create_all(bind=engine)
    logger.info("Database tables created successfully.")
except Exception as e:
    logger.error(f"Error creating database tables: {e}")

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/chat", response_model=schemas.ChatResponse)
def chat(chat_input: schemas.ChatInput, db: Session = Depends(get_db)):
    try:
        logger.info(f"Received chat input: {chat_input.message}")
        response = chatbot.get_chatbot_response(db, chat_input.message)
        logger.info(f"Generated chatbot response: {response}")
        return {"response": response}
    except Exception as e:
        logger.error(f"Error processing chat request: {e}", exc_info=True)
        raise HTTPException(
            status_code=500, detail="An internal error occurred. Please try again later."
        )


@app.post("/faqs", response_model=schemas.FAQ)
def create_faq(faq: schemas.FAQCreate, db: Session = Depends(get_db)):
    try:
        db_faq = models.FAQ(**faq.dict())
        db.add(db_faq)
        db.commit()
        db.refresh(db_faq)
        logger.info(f"FAQ added: {faq.question}")
        return db_faq
    except Exception as e:
        logger.error(f"Error creating FAQ: {e}", exc_info=True)
        raise HTTPException(
            status_code=500, detail="Failed to create FAQ. Please try again."
        )


@app.get("/faqs", response_model=list[schemas.FAQ])
def read_faqs(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    try:
        faqs = db.query(models.FAQ).offset(skip).limit(limit).all()
        logger.info(f"Retrieved {len(faqs)} FAQs.")
        return faqs
    except Exception as e:
        logger.error(f"Error retrieving FAQs: {e}", exc_info=True)
        raise HTTPException(
            status_code=500, detail="Failed to retrieve FAQs. Please try again."
        )


@app.delete("/faqs", status_code=204)
def delete_all_faqs(db: Session = Depends(get_db)):
    try:
        db.query(models.FAQ).delete()
        db.commit()
        return {"message": "All FAQs have been deleted."}
    except Exception as e:
        logger.error(f"Error deleting FAQs: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500, detail="An error occurred while deleting FAQs.")


@app.delete("/faqs/{faq_id}", status_code=204)
def delete_faq(faq_id: int, db: Session = Depends(get_db)):
    try:
        faq = db.query(models.FAQ).filter(models.FAQ.id == faq_id).first()
        if faq is None:
            raise HTTPException(status_code=404, detail="FAQ not found.")
        db.delete(faq)
        db.commit()
        return {"message": f"FAQ with ID {faq_id} has been deleted."}
    except Exception as e:
        logger.error(f"Error deleting FAQ: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500, detail="An error occurred while deleting the FAQ.")
