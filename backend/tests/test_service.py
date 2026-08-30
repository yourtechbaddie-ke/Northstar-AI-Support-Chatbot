from agents.service import answer_customer


def test_stock_lookup_returns_catalog_product():
    result = answer_customer("Is the Sovereign Shearling Trench in stock?")
    assert result["intent"] == "stock_availability"
    assert result["products"]
    assert result["products"][0]["name"] == "Sovereign Shearling Trench"


def test_out_of_stock_product_is_reported():
    result = answer_customer("Do you have the Ethereal Track Set in Rose Gold?")
    assert result["intent"] == "stock_availability"
    assert result["products"][0]["status"] == "OUT_OF_STOCK"


def test_return_policy_is_deterministic_without_llm_key():
    result = answer_customer("Can I return an item?")
    assert result["intent"] == "return_request"
    assert "30 days" in result["message"]


def test_unknown_request_escalates():
    result = answer_customer("Can you help me change my delivery address?")
    assert result["intent"] == "escalation"
    assert result["products"] == []
