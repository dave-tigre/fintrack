import pytest
from fintrack.portfolio import Portfolio
from datetime import datetime

@pytest.fixture
def portfolio():
    return Portfolio()

def test_initial_balance(portfolio):
    assert portfolio.cash == 0
    
def test_add_cash(portfolio):
    portfolio.deposit(1000)
    assert portfolio.cash == 1000  
    
def test_withdraw_cash(portfolio):
    portfolio.deposit(1000)
    portfolio.withdraw(500)
    assert portfolio.cash == 500

def test_record_transaction(portfolio):
    portfolio.deposit(25000)
    portfolio.record_transaction(datetime(2023,11,21), 'AAPL', 'Buy', 10, 150)
    assert portfolio.positions.loc['AAPL', 'Shares'] == 10

def test_remove_stock(portfolio):
    portfolio.deposit(25000)
    portfolio.record_transaction(datetime(2023,11,21), 'AAPL', 'Buy', 10, 150)
    portfolio.record_transaction(datetime(2023,11,21), 'AAPL', 'Sell', 5, 150)
    assert portfolio.positions.loc['AAPL', 'Shares'] == 5

def test_remove_stock_insufficient_shares(portfolio):
    portfolio.deposit(25000)
    portfolio.record_transaction(datetime(2023,11,21), 'AAPL', 'Buy', 10, 150)
    with pytest.raises(ValueError):
        portfolio.record_transaction(datetime(2023,11,21), 'AAPL', 'Sell', 15, 150)
        
def test_buy_stock_not_enough_cash(portfolio):
    portfolio.deposit(100)
    with pytest.raises(ValueError):
        portfolio.record_transaction(datetime(2023,11,21), 'AAPL', 'Buy', 10, 150)

def value(portfolio):
    portfolio.deposit(25000)
    portfolio.record_transaction(datetime(2023,11,21), 'AAPL', 'Buy', 10, 150)
    portfolio.record_transaction(datetime(2023,11,21), 'GOOG', 'Buy', 5, 100)
    assert portfolio.value() == portfolio.cash + (10 * 150 + 5 * 100)
    
def test_calculate_return(portfolio):
    portfolio.deposit(25000)
    portfolio.record_transaction(datetime(2023,11,21), 'AAPL', 'Buy', 10, 150)
    portfolio.record_transaction(datetime(2023,11,21), 'GOOG', 'Buy', 5, 100)
    assert portfolio.calculate_return(25000) == (portfolio.value() - 25000) / 25000
    
def test_save_load(portfolio):
    portfolio.deposit(25000)
    portfolio.record_transaction(datetime(2023,11,21), 'AAPL', 'Buy', 10, 150)
    portfolio.record_transaction(datetime(2023,11,21), 'GOOG', 'Buy', 5, 100)
    portfolio.save_pickle('test_portfolio.pkl')
    
    new_portfolio = Portfolio()
    new_portfolio.load_pickle('test_portfolio.pkl')
    assert new_portfolio.cash == portfolio.cash
    assert new_portfolio.positions.equals(portfolio.positions)
    
    new_portfolio.record_transaction(datetime(2023,11,21), 'AAPL', 'Buy', 10, 150)
    assert new_portfolio.positions.loc['AAPL', 'Shares'] == 20

    new_portfolio.record_transaction(datetime(2023,11,21), 'GOOG', 'Sell', 4, 100)
    assert new_portfolio.positions.loc['GOOG', 'Shares'] == 1
    assert new_portfolio.cash == (25000 - (20*150) - (1*100))

    assert new_portfolio.calculate_return(25000) == portfolio.calculate_return(25000)
    
    new_portfolio.save_pickle('test_portfolio.pkl')
    portfolio.load_pickle('test_portfolio.pkl')
    assert new_portfolio.cash == portfolio.cash
    assert new_portfolio.positions.equals(portfolio.positions)
    assert new_portfolio.calculate_return(25000) == portfolio.calculate_return(25000)
    
    import os
    os.remove('test_portfolio.pkl')