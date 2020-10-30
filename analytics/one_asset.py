from adaptor import Adaptor


if __name__ == "__main__":
    CLIENT_ID = "PGH9DVE22SZWDFBWK5YJV2PMDOA1UYBO"
    adaptor = Adaptor(CLIENT_ID)
    price_history = adaptor.get_price_history(
        "HYD",
        period_type="month",
        period=1,
        frequency_type='daily')
    underlying, option_terms, option_value = adaptor.get_option_chain("HYD")
    fundamentals = adaptor.get_fundamentals("HYD")
    print(price_history.to_string())
    print(underlying.to_string())
    print(option_terms.to_string())
    print(option_value.to_string())
    print(fundamentals.to_string())