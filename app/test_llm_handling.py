def test_database_not_found():
    result = answer_question("test question", "nonexistent_db")
    assert len(result) == 1
    assert len(result[0]) == 2
    assert result[0][0] == "test question"
    assert result[0][1] == "Database non trovato"

@patch('os.path.exists', return_value=True)
def test_successful_answer(mock_exists, mock_embeddings, mock_vectorstore, mock_chat_openai):
    mock_qa_chain = Mock()
    mock_qa_chain.return_value = {"result": "Test answer"}
    
    with patch('langchain.chains.RetrievalQA.from_chain_type', return_value=mock_qa_chain):
        result = answer_question("test question", "test_db")
        
        assert len(result) == 1
        assert len(result[0]) == 2
        assert result[0][0] == "test question"
        assert result[0][1] == "Test answer"

@patch('os.path.exists', return_value=True)
def test_error_handling(mock_exists, mock_embeddings):
    mock_embeddings.side_effect = Exception("Test error")
    
    result = answer_question("test question", "test_db")
    
    assert len(result) == 1
    assert len(result[0]) == 2
    assert result[0][0] == "test question"
    assert "Si è verificato un errore: Test error" in result[0][1]