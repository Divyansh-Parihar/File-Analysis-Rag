from langchain_ollama import ChatOllama, OllamaEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.prompts import PromptTemplate
from langchain_chroma import Chroma
from pydantic import BaseModel, Field
from logger import get_logger

logger = get_logger(__name__)
logger.info("Rag module Loaded")


llm = ChatOllama(model="qwen2.5:0.5b")
logger.info("ChatOllama LLM initialized with model: qwen2.5:0.5b")


class Summary(BaseModel):
    """
    Pydantic model representing the structured output of a document summary.
    """

    topic: str = Field(..., description='Topic or Title of the text')

    key_topics: list[str] = Field(..., description='Key Themes or Topics Discussed in the Text')

    summary: str = Field(..., description="A Long Summary of Text")


structured_llm = llm.with_structured_output(Summary)
logger.debug("Structured LLM Initialized")



class FileAnalysis:
    """
    Handles document summarization and RAG-based querying using a local Ollama LLM.
    """

    def __init__(self):
        """
        Initializes the text splitter and prompt templates for summarization.
        """

        logger.debug("Initializing FileAnalysis instance")

        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size = 5000,
            chunk_overlap = 500
        )

        self.summary_prompt = PromptTemplate(
            template='''You are an expert document analyst.

            Analyze the following text carefully and generate:

            1. A clear title/topic
            2. A highly detailed summary
            3. Important concepts discussed
            4. Key arguments and insights
            5. Important examples if present

            The summary should:
            - be comprehensive
            - retain important details
            - avoid vague wording
            - explain the ideas clearly
            - be at least 300-500 words if enough content exists

            TEXT:
            {text}''',
            input_variables=['text']
        )

        self.summarize_prompt = PromptTemplate(
            template='''You are an expert summarizer.

            Below are multiple summaries from different parts of a document.

            Create ONE final comprehensive summary that:
            - combines all important information
            - preserves technical details
            - explains key ideas clearly
            - avoids repetition
            - is well structured
            - is detailed and informative

            Also generate:
            1. Final Topic/Title
            2. Final Key Topics
            3. Final Detailed Summary

            SUMMARIES:
            {summary}''',
            input_variables=['summary']
        )

        logger.info("FileAnalysis initialized: splitter and prompts ready")


    def summarize(self, text: str):
        """
        Splits text into chunks and returns a structured LLM-generated summary.
        """

        logger.info("summarize() called")
        logger.debug(f"Input text length: {len(text)} characters")
    
        self.chunks = self.splitter.create_documents([text])
        logger.info(f"Text split into {len(self.chunks)} chunk(s)")

        if len(self.chunks) == 1:
            logger.info("Single chunk detected — invoking structured LLM directly")
            response = structured_llm.invoke(f"Generate a Summary from this document: \n{text}")
            return response

        summary_chain = self.summary_prompt | structured_llm
        logger.debug("summary_chain built (summary_prompt | structured_llm)")

        summaries = []

        for i, chunk in enumerate(self.chunks):
            logger.debug(f"Summarizing chunk {i + 1}/{len(self.chunks)} ({len(chunk.page_content)} chars)")
            res = summary_chain.invoke({'text': chunk.page_content})
            summaries.append(res)
            logger.debug(f"Chunk {i + 1} summarized. Topic: '{res.topic}'")

        logger.info(f"All {len(summaries)} chunk summaries generated — combining")
        combined = '\n\n'.join([s.summary for s in summaries])

        summarize_chain = self.summarize_prompt | structured_llm 
        logger.debug("summarize_chain built (summarize_prompt | structured_llm)")

        final_summary  = summarize_chain.invoke({'summary': combined})
        logger.info(f"Final summary generated. Topic: '{final_summary.topic}'")
        
        return final_summary
        


    def query(self, text : str):
        """
        Retrieves relevant chunks from the vector store and answers the question using the LLM.
        """

        logger.info(f"query() called with question: '{text[:100]}...' " if len(text) > 100 else f"query() called with question: '{text}'")

        vector_store = Chroma.from_documents(
            documents=self.chunks,
            embedding=OllamaEmbeddings(model="llama3.2:3b"),
            #persist_directory='chroma',
            collection_name='sample'
        )
        logger.debug("Chroma vector store created from documents")
        
        retriever = vector_store.as_retriever(search_type = 'similarity', search_kwargs = {"k":3})
        logger.debug("Retriever initialized (similarity, k=3)")

        result = retriever.invoke(text)
        logger.info(f"Retriever returned {len(result)} document(s)")

        prompt = PromptTemplate(
            template='''You are a helpful AI assistant.

            Answer the user's question ONLY using the provided context.

            Rules:
            - Do not hallucinate
            - If the answer is missing, say "I don't know based on the provided document."
            - Give detailed and accurate answers
            - Use complete sentences

            CONTEXT:
            {context}

            QUESTION:
            {question}''',
            input_variables=['context','question']
        )

        context = "\n\n".join([doc.page_content for doc in result])
        logger.debug(f"Context assembled from {len(result)} retrieved doc(s): {len(context)} chars")

        final_prompt = prompt.invoke({'context': context, 'question': text})

        answer = llm.invoke(final_prompt)
        logger.info("Query answered successfully")

        return answer
    


file_analysis = FileAnalysis()
logger.info("Global file_analysis instance created")
