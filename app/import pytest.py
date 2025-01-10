import pytest
from unittest.mock import Mock, patch
import os
from .llm_handling import answer_question

# app/test_llm_handling.py

@pytest.fixture
def mock_embeddings():
    with patch('langchain_community.embeddings.HuggingFaceEmbeddings') as mock:
        yield mock

@pytest.fixture
def mock_vectorstore():
    with patch('langchain_community.vectorstores.FAISS') as mock:
        mock_instance = Mock()
        mock_instance.as_retriever.return_value = Mock()
        mock.load_local.return_value = mock_instance
        yield mock

@pytest.fixture
def mock_chat_openai():
    with patch('langchain_openai.ChatOpenAI') as mock:
        yield mock

def test_database_not_found():
    result = answer_question("test question", "nonexistent_db")
    assert len(result) == 2
    assert result[0]["role"] == "user"
    assert result[0]["content"] == "test question"
    assert result[1]["role"] == "assistant"
    assert result[1]["content"] == "Database non trovato"

@patch('os.path.exists', return_value=True)
def test_successful_answer(mock_exists, mock_embeddings, mock_vectorstore, mock_chat_openai):
    mock_qa_chain = Mock()
    mock_qa_chain.return_value = {"result": "Test answer"}
    
    with patch('langchain.chains.RetrievalQA.from_chain_type', return_value=mock_qa_chain):
        result = answer_question("test question", "test_db")
        
        assert len(result) == 2
        assert result[0]["role"] == "user"
        assert result[0]["content"] == "test question"
        assert result[1]["role"] == "assistant"
        assert result[1]["content"] == "Test answer"

@patch('os.path.exists', return_value=True)
def test_error_handling(mock_exists, mock_embeddings):
    mock_embeddings.side_effect = Exception("Test error")
    
    result = answer_question("test question", "test_db")
    
    assert len(result) == 2
    assert result[0]["role"] == "user"
    assert result[0]["content"] == "test question"
    assert result[1]["role"] == "assistant"
    assert "Si è verificato un errore: Test error" in result[1]["content"]